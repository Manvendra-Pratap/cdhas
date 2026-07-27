from typing import Dict, Any, List

FEATURE_NAMES = [
    "duration_sec",
    "cmd_count",
    "unique_cmd_count",
    "failed_login_count",
    "priv_escalation_count",
    "download_file_count",
]

def extract_features_from_session(session: Dict[str, Any]) -> List[float]:
    """Extract a 6-dimensional numerical feature vector from a session dict or model."""
    if hasattr(session, "model_dump"):
        s = session.model_dump()
    elif isinstance(session, dict):
        s = session
    else:
        s = session.__dict__

    commands = s.get("commands") or []
    cmd_count = len(commands)
    unique_cmd_count = len(set(commands))

    # Parse duration string (e.g. "14m 22s", "00m 44s", "45s")
    duration_str = str(s.get("duration") or "30s")
    duration_sec = 30.0
    try:
        if "m" in duration_str and "s" in duration_str:
            parts = duration_str.split("m")
            minutes = float(parts[0].strip())
            seconds = float(parts[1].replace("s", "").strip())
            duration_sec = minutes * 60 + seconds
        elif "s" in duration_str:
            duration_sec = float(duration_str.replace("s", "").strip())
    except Exception:
        duration_sec = 45.0

    # Failed login attempts heuristics
    username = str(s.get("username") or "").lower()
    failed_login_count = 1.0 if username in ("root", "admin", "test", "oracle", "user", "guest") else 0.0

    # Privilege escalation keywords
    priv_keywords = ("sudo", "su", "shadow", "passwd", "pty", "chmod 777", "chmod +x")
    priv_escalation_count = float(sum(1 for c in commands if any(k in c.lower() for k in priv_keywords)))

    # Downloaded file keywords
    download_keywords = ("curl", "wget", "busybox", ".sh", ".bin", "http://", "https://")
    download_file_count = float(sum(1 for c in commands if any(k in c.lower() for k in download_keywords)))

    return [
        float(duration_sec),
        float(cmd_count),
        float(unique_cmd_count),
        float(failed_login_count),
        float(priv_escalation_count),
        float(download_file_count),
    ]

def normalize_features(feature_vectors: List[List[float]]) -> List[List[float]]:
    """Min-Max normalization of feature matrix across columns."""
    if not feature_vectors:
        return []

    num_features = len(feature_vectors[0])
    normalized = []

    min_vals = [min(v[i] for v in feature_vectors) for i in range(num_features)]
    max_vals = [max(v[i] for v in feature_vectors) for i in range(num_features)]

    for vector in feature_vectors:
        norm_row = []
        for i in range(num_features):
            diff = max_vals[i] - min_vals[i]
            norm_val = (vector[i] - min_vals[i]) / diff if diff > 0 else 0.0
            norm_row.append(norm_val)
        normalized.append(norm_row)

    return normalized
