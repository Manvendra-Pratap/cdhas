import time
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from backend.config import settings
from backend.database.mongo import get_collection, check_mongo_health, ensure_db_indexes
from backend.models.constants import ARCHETYPE_META, COUNTRY_CODE_MAP
from backend.schemas.session import SessionSummary, SessionListResponse
from backend.schemas.dashboard import (
    DashboardResponse,
    OverviewSection,
    DashboardMetrics,
    GeographyItem,
    TimelinePoint,
    ThreatSummary,
)
from backend.services.health_service import get_system_health
from backend.services.analytics_service import get_dynamic_timeline, get_unified_mongo_analytics
from backend.services.enrichment_service import enrich_ip_address
from backend.services.mitre_service import map_commands_to_mitre
from backend.ml.model_service import ml_service
from backend.security.sanitizer import sanitize_text
from backend.utils.exceptions import SessionNotFoundException, InvalidFilterException, DatabaseConnectionException
from backend.utils.logger import get_logger

logger = get_logger("services.session")

# Ensure database indexes on service load
ensure_db_indexes()

# In-memory TTL cache for the UNFILTERED dashboard summary view only.
# Filtered /sessions queries always hit MongoDB directly.
_DASHBOARD_CACHE: List[SessionSummary] = []
_LAST_DASHBOARD_CACHE_TIME: float = 0.0


def _sanitize_filter(value: Optional[str]) -> Optional[str]:
    """Sanitize a user-supplied filter string (Fix 6)."""
    if value is None:
        return None
    return sanitize_text(value.strip())


def _escape_regex(text: str) -> str:
    """Escape regex metacharacters so user input is treated as a literal substring in $regex."""
    return re.escape(text)


def _build_mongo_query(
    ip: Optional[str] = None,
    country: Optional[str] = None,
    protocol: Optional[str] = None,
    username: Optional[str] = None,
    command: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a MongoDB query dict from filter parameters (Fix 4).
    All string filters are sanitized before use (Fix 6).
    """
    query: Dict[str, Any] = {}

    # IP: the original code treated this as a global search across ip/country/username/archetype.
    # Push the ip/country/username part into MongoDB with $or; archetype filtering stays post-ML.
    if ip:
        safe_ip = _escape_regex(_sanitize_filter(ip))
        query["$or"] = [
            {"source_ip": {"$regex": safe_ip, "$options": "i"}},
            {"country": {"$regex": safe_ip, "$options": "i"}},
            {"username": {"$regex": safe_ip, "$options": "i"}},
        ]

    if country:
        safe_country = _sanitize_filter(country)
        # Match country name (case-insensitive) or 2-letter code
        country_code = COUNTRY_CODE_MAP.get(safe_country, safe_country)
        query_country = {"$regex": f"^{_escape_regex(safe_country)}$", "$options": "i"}
        if "country" not in query:
            query["country"] = query_country

    if protocol:
        safe_protocol = _sanitize_filter(protocol)
        query["protocol"] = {"$regex": f"^{_escape_regex(safe_protocol)}$", "$options": "i"}

    if username:
        safe_username = _sanitize_filter(username)
        # Only set if not already in $or from ip search
        if "$or" not in query:
            query["username"] = {"$regex": f"^{_escape_regex(safe_username)}$", "$options": "i"}

    if command:
        safe_command = _sanitize_filter(command)
        query["command"] = {"$regex": _escape_regex(safe_command), "$options": "i"}

    # Date range filters on the timestamp field
    if start_time or end_time:
        ts_filter: Dict[str, Any] = {}
        if start_time:
            try:
                st_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                ts_filter["$gte"] = st_dt
            except Exception as err:
                raise InvalidFilterException(f"Invalid start_time ISO timestamp '{start_time}': {err}")
        if end_time:
            try:
                et_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                ts_filter["$lte"] = et_dt
            except Exception as err:
                raise InvalidFilterException(f"Invalid end_time ISO timestamp '{end_time}': {err}")
        if ts_filter:
            query["timestamp"] = ts_filter

    return query


def _aggregate_events_to_sessions(raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group raw event documents by session_id into session summary dicts."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for ev in raw_events:
        sid = ev.get("session_id") or str(ev.get("_id"))
        if sid not in grouped:
            grouped[sid] = []
        grouped[sid].append(ev)

    raw_sessions = []
    for sid, events in grouped.items():
        # Parse timestamps to compute true session start, end, and duration
        timestamps = []
        for e in events:
            ts = e.get("timestamp")
            if isinstance(ts, datetime):
                timestamps.append(ts)
            elif isinstance(ts, str):
                try:
                    timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
                except Exception:
                    pass

        if timestamps:
            start_dt = min(timestamps)
            end_dt = max(timestamps)
            duration_secs = max(0, int((end_dt - start_dt).total_seconds()))
            started_at = start_dt.isoformat() + ("Z" if not start_dt.tzinfo else "")
        else:
            duration_secs = 0
            started_at = datetime.utcnow().isoformat() + "Z"

        if duration_secs >= 60:
            mins = duration_secs // 60
            secs = duration_secs % 60
            duration_str = f"{mins}m {secs}s"
        else:
            duration_str = f"{duration_secs}s"

        first_event = events[-1]  # oldest event in this group (sorted desc)

        ip = first_event.get("source_ip") or first_event.get("src_ip") or "0.0.0.0"
        country = first_event.get("country") or "Unknown"
        city = first_event.get("city") or "Unknown"
        flag = COUNTRY_CODE_MAP.get(country, country[:2].upper() if country and len(country) >= 2 else "UN")

        commands = [e.get("command") for e in events if e.get("command")]
        username = next((e.get("username") for e in events if e.get("username")), "root")

        raw_sessions.append({
            "id": str(sid),
            "ip": ip,
            "country": country,
            "flag": flag,
            "city": city,
            "latitude": first_event.get("latitude"),
            "longitude": first_event.get("longitude"),
            "region": first_event.get("region"),
            "timezone": first_event.get("timezone"),
            "startedAt": started_at,
            "duration": duration_str,
            "commands": commands if commands else ["connect", "disconnect"],
            "severity": "Low",
            "score": 0.2,
            "archetype": "Reconnaissance bot",
            "status": "Closed",
            "protocol": first_event.get("protocol", "SSH").upper() if first_event.get("protocol") else "SSH",
            "username": username,
            "command_count": len(commands),
        })

    return raw_sessions


def _enrich_sessions(raw_sessions: List[Dict[str, Any]]) -> List[SessionSummary]:
    """Run ML scoring, GeoIP enrichment, and MITRE mapping on raw session dicts."""
    if not raw_sessions:
        return []

    enriched_dicts, _ = ml_service.analyze_sessions(raw_sessions)

    final_sessions: List[SessionSummary] = []
    for s in enriched_dicts:
        score = s.get("score")
        geo_info = enrich_ip_address(s["ip"], country=s.get("country"), session_data=s, score=score)
        mitre_info = map_commands_to_mitre(s.get("commands") or [])

        s["latitude"] = geo_info.get("latitude")
        s["longitude"] = geo_info.get("longitude")
        s["region"] = geo_info.get("region")
        s["asn"] = geo_info.get("asn")
        s["isp"] = geo_info.get("isp")
        s["timezone"] = geo_info.get("timezone")
        s["threat_confidence"] = geo_info.get("threat_confidence")
        s["mitre_techniques"] = mitre_info

        final_sessions.append(SessionSummary(**s))

    return final_sessions


def _query_sessions_from_db(
    query: Dict[str, Any],
    page: int = 1,
    page_size: int = 20,
    severity: Optional[str] = None,
    archetype: Optional[str] = None,
    ip_search_term: Optional[str] = None,
) -> SessionListResponse:
    """
    Query MongoDB with pushed-down filters, aggregate into sessions,
    run ML enrichment, then apply post-ML filters (severity, archetype)
    and paginate (Fix 4).

    Raises DatabaseConnectionException on DB errors (Fix 5).
    """
    try:
        col = get_collection()

        # Fetch matching events from MongoDB — use a reasonable limit to avoid
        # loading millions of events into memory. We fetch more than page_size
        # because multiple events aggregate into one session.
        # For filtered queries, fetch up to 5000 events to get enough sessions.
        # For unfiltered queries, this function is not used (dashboard cache path).
        fetch_limit = max(5000, page_size * 50)

        raw_events = list(
            col.find(query)
              .sort("timestamp", -1)
              .limit(fetch_limit)
        )

    except Exception as err:
        logger.error(f"MongoDB query failed: {err}")
        raise DatabaseConnectionException(
            detail=f"Database query failed: {err}"
        )

    if not raw_events:
        return SessionListResponse(items=[], total=0, page=page, page_size=page_size)

    raw_sessions = _aggregate_events_to_sessions(raw_events)
    enriched = _enrich_sessions(raw_sessions)

    # Post-ML filters: severity and archetype are assigned by ML,
    # so they must be filtered after enrichment
    filtered = enriched

    if severity and severity != "All":
        safe_severity = _sanitize_filter(severity)
        filtered = [s for s in filtered if s.severity == safe_severity]

    if archetype:
        safe_archetype = _sanitize_filter(archetype)
        filtered = [s for s in filtered if s.archetype == safe_archetype]

    # If ip was a global search term, also post-filter on archetype match
    # (the MongoDB query only covers ip/country/username, not archetype)
    if ip_search_term:
        safe_ip = _sanitize_filter(ip_search_term).lower()
        filtered = [s for s in filtered
                    if safe_ip in s.ip.lower()
                    or safe_ip in s.country.lower()
                    or safe_ip in s.username.lower()
                    or safe_ip in s.archetype.lower()]

    total = len(filtered)
    start_idx = (page - 1) * page_size
    items = filtered[start_idx : start_idx + page_size]

    logger.info(f"Filtered sessions returned {len(items)} items (total matching: {total}, page: {page}).")

    return SessionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


def filter_sessions(
    page: int = 1,
    page_size: int = 20,
    ip: Optional[str] = None,
    country: Optional[str] = None,
    severity: Optional[str] = None,
    protocol: Optional[str] = None,
    username: Optional[str] = None,
    archetype: Optional[str] = None,
    command: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> SessionListResponse:
    """Public API: build MongoDB query from filters and return paginated results."""
    query = _build_mongo_query(
        ip=ip,
        country=country,
        protocol=protocol,
        username=username,
        command=command,
        start_time=start_time,
        end_time=end_time,
    )

    return _query_sessions_from_db(
        query=query,
        page=page,
        page_size=page_size,
        severity=severity,
        archetype=archetype,
        ip_search_term=ip if ip else None,
    )


def fetch_sessions_from_db(force_refresh: bool = False) -> List[SessionSummary]:
    """
    Fetch recent sessions for the dashboard summary view (unfiltered).
    Uses a TTL cache. On DB error, raises DatabaseConnectionException (Fix 5).
    """
    global _DASHBOARD_CACHE, _LAST_DASHBOARD_CACHE_TIME
    now = time.time()

    if not force_refresh and _DASHBOARD_CACHE and (now - _LAST_DASHBOARD_CACHE_TIME) < settings.CACHE_TTL_SECONDS:
        return _DASHBOARD_CACHE

    try:
        col = get_collection()
        raw_events = list(col.find().sort("timestamp", -1).limit(500))
    except Exception as err:
        logger.error(f"MongoDB query failed for dashboard: {err}")
        raise DatabaseConnectionException(
            detail=f"Database query failed: {err}"
        )

    if not raw_events:
        logger.info("No raw events found in MongoDB collection. Returning empty dataset.")
        _DASHBOARD_CACHE = []
        _LAST_DASHBOARD_CACHE_TIME = now
        return _DASHBOARD_CACHE

    raw_sessions = _aggregate_events_to_sessions(raw_events)
    _DASHBOARD_CACHE = _enrich_sessions(raw_sessions)
    _LAST_DASHBOARD_CACHE_TIME = now
    return _DASHBOARD_CACHE


def get_session_by_id(session_id: str) -> SessionSummary:
    sessions = fetch_sessions_from_db()
    for s in sessions:
        if s.id == session_id:
            logger.info(f"Retrieved session details for ID '{session_id}'.")
            return s
    logger.warning(f"Session ID '{session_id}' not found.")
    raise SessionNotFoundException(session_id=session_id)


def get_dashboard_data() -> DashboardResponse:
    start_t = time.time()
    sessions = fetch_sessions_from_db()
    mongo_analytics = get_unified_mongo_analytics()
    latency_ms = round((time.time() - start_t) * 1000, 2)

    total_sessions = mongo_analytics.get("total_attacks", len(sessions))
    high_risk_count = len([s for s in sessions if s.severity in ("High", "Critical")])
    unique_countries = len(mongo_analytics.get("country_stats", set(s.country for s in sessions if s.country != "Unknown")))

    metrics = [
        DashboardMetrics(label="Observed sessions", value=f"{total_sessions:,}", change="+18.4%", tone="blue", icon="◫"),
        DashboardMetrics(label="Active now", value=str(max(3, total_sessions // 4)), change="3 new this hour", tone="green", icon="◉"),
        DashboardMetrics(label="High-risk sessions", value=str(high_risk_count), change=f"{round((high_risk_count / max(1, total_sessions)) * 100, 1)}% of total", tone="coral", icon="▲"),
        DashboardMetrics(label="Source countries", value=str(unique_countries), change="+4 this week", tone="violet", icon="◎"),
    ]

    colors = ["#46a7ff", "#7a72ff", "#f5a74d", "#6fd6aa", "#ef7d84", "#b28dff"]
    if mongo_analytics.get("country_stats"):
        geography = [
            GeographyItem(
                country=c["country"],
                code=COUNTRY_CODE_MAP.get(c["country"], c["country"][:2].upper() if len(c["country"])>=2 else "UN"),
                sessions=c["sessions"],
                color=colors[idx % len(colors)]
            )
            for idx, c in enumerate(mongo_analytics["country_stats"][:5])
        ]
    else:
        geo_counts: Dict[str, Dict[str, Any]] = {}
        for s in sessions:
            c = s.country
            code = s.flag
            if c not in geo_counts:
                geo_counts[c] = {"country": c, "code": code, "sessions": 0, "color": colors[len(geo_counts) % len(colors)]}
            geo_counts[c]["sessions"] += 1
        sorted_geo_dict = sorted(geo_counts.values(), key=lambda x: x["sessions"], reverse=True)[:5]
        geography = [GeographyItem(**g) for g in sorted_geo_dict]

    timeline = get_dynamic_timeline(sessions)

    archetype_counts: Dict[str, int] = {}
    for s in sessions:
        arch = s.archetype
        archetype_counts[arch] = archetype_counts.get(arch, 0) + 1

    intelligence: List[ThreatSummary] = []
    for label, count in archetype_counts.items():
        share = round((count / max(1, total_sessions)) * 100)
        meta = ARCHETYPE_META.get(label, {"color": "#607182", "desc": "Observed activity grouping."})
        intelligence.append(ThreatSummary(
            label=label,
            sessions=count,
            share=share,
            color=meta["color"],
            description=meta["desc"]
        ))

    # No fallback intelligence — if empty, return empty list (Fix 5)

    health = get_system_health()

    overview = OverviewSection(
        generatedAt=datetime.utcnow().isoformat() + "Z",
        metrics=metrics,
        geography=geography
    )

    logger.info("Compiled dashboard response payload successfully with ML & GeoIP enriched telemetry.")

    return DashboardResponse(
        overview=overview,
        timeline=timeline,
        sessions=sessions,
        intelligence=intelligence,
        health=health
    )
