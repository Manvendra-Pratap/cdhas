from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SessionSummary(BaseModel):
    id: str = Field(..., example="e6f0a2bd", description="Unique session identifier")
    ip: str = Field(..., example="185.220.101.42", description="Attacker source IP address")
    country: str = Field(..., example="Germany", description="Origin country name")
    flag: str = Field(..., example="DE", description="ISO 3166-1 alpha-2 country code")
    city: str = Field(..., example="Frankfurt", description="Origin city name")
    startedAt: str = Field(..., example="2026-07-26T11:38:11Z", description="Session connection start time (ISO 8601 UTC)")
    duration: str = Field(..., example="14m 22s", description="Session connection duration")
    commands: List[str] = Field(default_factory=list, example=["uname -a", "id"], description="Observed input commands")
    severity: str = Field(..., example="Critical", description="Computed threat severity: Low, Medium, High, Critical")
    score: float = Field(..., example=0.94, description="Anomaly risk score (0.0 to 1.0)")
    archetype: str = Field(..., example="Post-exploitation", description="AI behavioral attack archetype classification")
    status: str = Field("Closed", example="Closed", description="Session state: Active or Closed")
    protocol: str = Field("SSH", example="SSH", description="Target honeypot protocol: SSH, Telnet, HTTP")
    username: str = Field("root", example="root", description="Credential username attempted")

    # Enriched GeoIP2 & MITRE ATT&CK Metadata
    latitude: Optional[float] = Field(None, example=50.1109, description="GeoIP latitude coordinate for map plotting")
    longitude: Optional[float] = Field(None, example=8.6821, description="GeoIP longitude coordinate for map plotting")
    region: Optional[str] = Field(None, example="Hesse", description="Origin region/state name")
    asn: Optional[str] = Field(None, example="AS200019 TOR Exit Node", description="Autonomous System Number and ISP registry")
    isp: Optional[str] = Field(None, example="Praxis Host LLC", description="Internet Service Provider name")
    timezone: Optional[str] = Field(None, example="Europe/Berlin", description="Origin timezone string")
    threat_confidence: Optional[float] = Field(None, example=96.5, description="Attacker threat confidence percentage")
    mitre_techniques: Optional[List[Dict[str, str]]] = Field(None, description="Mapped MITRE ATT&CK techniques")

class SessionDetails(SessionSummary):
    pass

class SessionListResponse(BaseModel):
    items: List[SessionSummary] = Field(..., description="Paginated list of matching sessions")
    total: int = Field(..., example=42, description="Total matching session count across all pages")
    page: int = Field(..., example=1, description="Current page index")
    page_size: int = Field(..., example=20, description="Items per page limit")
