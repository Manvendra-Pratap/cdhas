# Import json to parse raw JSON log lines from the Cowrie log file
import json

# Import datetime to convert ISO timestamp strings into Python datetime objects
from datetime import datetime

# Define the set of Cowrie event types that we know how to handle
SUPPORTED_EVENTS = {
    "cowrie.session.connect",
    "cowrie.login.failed",
    "cowrie.login.success",
    "cowrie.command.input",
    "cowrie.session.closed",
    "cowrie.direct-tcpip.request",
}

# Map each raw Cowrie event type to a short, human-readable plain name for the normalized schema
EVENT_TYPE_MAP = {
    # When a new session is started (a machine connected to the honeypot)
    "cowrie.session.connect": "connect",
    # When an attacker tries a username/password and it fails
    "cowrie.login.failed": "login_failed",
    # When an attacker tries a username/password and it succeeds
    "cowrie.login.success": "login_success",
    # When the attacker types a command inside the fake shell
    "cowrie.command.input": "command",
    # When the session ends / the attacker disconnects
    "cowrie.session.closed": "disconnect",
    # When the attacker tries to open a TCP tunnel through the honeypot
    "cowrie.direct-tcpip.request": "port_forward",
}


# Define the main parsing function — takes a raw JSON string line and returns a normalized dict or None
def parse_line(raw_line: str):
    # Strip any leading/trailing whitespace and newline characters from the raw line
    raw_line = raw_line.strip()

    # If the line is empty after stripping, there is nothing to parse — return None
    if not raw_line:
        return None

    # Attempt to parse the line as a JSON object — if it fails, the line is malformed
    try:
        # Parse the raw JSON string into a Python dictionary
        raw = json.loads(raw_line)
    except json.JSONDecodeError:
        # If the line is not valid JSON, we cannot process it — return None
        return None

    # Extract the event identifier field from the parsed JSON (Cowrie uses "eventid")
    event_id = raw.get("eventid", "")

    # If this event type is not in our supported set, we don't process it — return None
    if event_id not in SUPPORTED_EVENTS:
        return None

    # Look up the plain-english event type name from our mapping dictionary
    event_type = EVENT_TYPE_MAP[event_id]

    # Extract the timestamp string from the raw log; default to empty string if missing
    timestamp_str = raw.get("timestamp", "")

    # Attempt to parse the timestamp into a Python datetime object using ISO 8601 format
    try:
        # Cowrie timestamps look like "2024-01-15T10:23:45.123456Z" — parse accordingly
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        # If the timestamp cannot be parsed, fall back to the current UTC time
        timestamp = datetime.utcnow()

    # Extract the attacker's source IP address from the "src_ip" field
    source_ip = raw.get("src_ip", None)

    # Extract the attacker's source port number from the "src_port" field, default to 0 if missing
    source_port = int(raw.get("src_port", 0))

    # Extract the session identifier — Cowrie calls this "session"
    session_id = raw.get("session", "")

    # Extract the username field — only present in login events, None for other event types
    username = raw.get("username", None)

    # Extract the password field — only present in login events, None for other event types
    password = raw.get("password", None)

    # Extract the command the attacker typed — only present in command input events
    command = raw.get("input", None)

    # Build and return the normalized event dictionary matching the required schema exactly
    return {
        # Python datetime object representing when the event occurred
        "timestamp": timestamp,
        # The attacker's IP address as a string
        "source_ip": source_ip,
        # The attacker's source port as an integer
        "source_port": source_port,
        # All Cowrie honeypot events use SSH protocol
        "protocol": "ssh",
        # Plain-english event type (connect / login_failed / login_success / command / disconnect / port_forward)
        "event_type": event_type,
        # Username attempted — None if not applicable to this event type
        "username": username,
        # Password attempted — None if not applicable to this event type
        "password": password,
        # Shell command typed — None if not applicable to this event type
        "command": command,
        # Unique session identifier string from Cowrie
        "session_id": session_id,
        # The name of this specific honeypot sensor for multi-sensor deployments
        "honeypot": "cowrie-01",
        # The original raw dictionary before normalization, preserved for debugging
        "raw": raw,
    }
