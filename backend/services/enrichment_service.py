from typing import Dict, Any, Optional
from backend.utils.logger import get_logger

logger = get_logger("services.enrichment")

def enrich_ip_address(
    ip: str,
    country: Optional[str] = None,
    session_data: Optional[Dict[str, Any]] = None,
    score: Optional[float] = None
) -> Dict[str, Any]:
    """
    Pass-through real GeoIP data (latitude, longitude, city, country, region, timezone)
    from the session's MongoDB document (populated by geolocate.py / backfill pipeline).
    Returns asn: None and isp: None honestly — no fabricated ASN/ISP data.
    Computes threat_confidence dynamically from the ML anomaly risk score.
    """
    doc = session_data or {}

    real_country = doc.get("country") or country or "Unknown"
    real_city = doc.get("city")
    real_lat = doc.get("latitude")
    real_lon = doc.get("longitude")
    real_region = doc.get("region")
    real_tz = doc.get("timezone")

    # Threat confidence derived dynamically from real Isolation Forest ML anomaly score
    if score is not None:
        threat_confidence = round(score * 100.0, 1)
    elif doc.get("score") is not None:
        threat_confidence = round(doc["score"] * 100.0, 1)
    else:
        threat_confidence = None

    enriched = {
        "country": real_country,
        "flag": doc.get("flag") or (real_country[:2].upper() if len(real_country) >= 2 else "UN"),
        "region": real_region,
        "city": real_city,
        "latitude": real_lat,
        "longitude": real_lon,
        "asn": None,
        "isp": None,
        "timezone": real_tz,
        "threat_confidence": threat_confidence,
    }

    logger.debug(f"Applied real telemetry enrichment for IP '{ip}' ({real_country})")
    return enriched
