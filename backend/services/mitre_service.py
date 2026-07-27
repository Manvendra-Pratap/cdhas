from typing import List, Dict, Any

MITRE_TECHNIQUES: Dict[str, Dict[str, str]] = {
    "T1082": {
        "id": "T1082",
        "name": "System Information Discovery",
        "tactic": "Discovery",
        "description": "An adversary may attempt to get detailed information about the operating system and hardware.",
    },
    "T1033": {
        "id": "T1033",
        "name": "System Owner/User Discovery",
        "tactic": "Discovery",
        "description": "Adversaries may attempt to identify the primary user or logged-in account.",
    },
    "T1105": {
        "id": "T1105",
        "name": "Ingress Tool Transfer",
        "tactic": "Command and Control",
        "description": "Adversaries may transfer tools or files from an external system into the compromised environment.",
    },
    "T1003": {
        "id": "T1003",
        "name": "OS Credential Dumping",
        "tactic": "Credential Access",
        "description": "Adversaries may attempt to dump credentials from memory or shadow password databases.",
    },
    "T1548": {
        "id": "T1548",
        "name": "Abuse Elevation Control Mechanism",
        "tactic": "Privilege Escalation",
        "description": "Adversaries may circumvent mechanisms designed to control elevation of privileges.",
    },
    "T1059.004": {
        "id": "T1059.004",
        "name": "Unix Shell Execution",
        "tactic": "Execution",
        "description": "Adversaries may abuse Unix shell commands for execution of malicious scripts.",
    },
    "T1222": {
        "id": "T1222",
        "name": "File & Directory Permissions Modification",
        "tactic": "Defense Evasion",
        "description": "Adversaries may modify file permissions to make payloads executable.",
    },
}

def map_commands_to_mitre(commands: List[str]) -> List[Dict[str, str]]:
    """Maps command strings to MITRE ATT&CK technique IDs, names, and tactics."""
    if not commands:
        return [MITRE_TECHNIQUES["T1059.004"]]

    matched_ids = set()
    for cmd in commands:
        c_lower = cmd.lower()
        if any(k in c_lower for k in ("uname", "cpuinfo", "ls", "pwd", "proc")):
            matched_ids.add("T1082")
        if any(k in c_lower for k in ("whoami", "id", "users")):
            matched_ids.add("T1033")
        if any(k in c_lower for k in ("curl", "wget", "busybox", "http")):
            matched_ids.add("T1105")
        if any(k in c_lower for k in ("shadow", "passwd", "cat /etc/")):
            matched_ids.add("T1003")
        if any(k in c_lower for k in ("sudo", "su", "pty", "spawn")):
            matched_ids.add("T1548")
        if any(k in c_lower for k in ("chmod", "+x", "777")):
            matched_ids.add("T1222")

    if not matched_ids:
        matched_ids.add("T1059.004")

    return [MITRE_TECHNIQUES[tid] for tid in matched_ids if tid in MITRE_TECHNIQUES]
