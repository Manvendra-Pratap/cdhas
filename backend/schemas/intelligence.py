from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.schemas.dashboard import ThreatSummary, GeographyItem

class AnomalyItem(BaseModel):
    id: str = Field(..., example="e6f0a2bd", description="Session ID")
    ip: str = Field(..., example="185.220.101.42", description="Attacker source IP")
    country: str = Field(..., example="Germany", description="Origin country")
    flag: str = Field(..., example="DE", description="ISO country code")
    severity: str = Field(..., example="Critical", description="Severity classification")
    score: float = Field(..., example=0.94, description="Isolation Forest anomaly score (0.0 to 1.0)")
    archetype: str = Field(..., example="Post-exploitation", description="Attacker archetype cluster")
    reasons: List[str] = Field(default_factory=list, example=["Excessive privilege escalation commands", "High anomaly score"], description="Anomaly trigger explanations")

class AnomalyListResponse(BaseModel):
    anomalies: List[AnomalyItem] = Field(..., description="List of detected anomalous sessions")
    total: int = Field(..., example=8, description="Total anomalous session count")
    critical_count: int = Field(..., example=2, description="Critical severity count")
    average_score: float = Field(..., example=0.78, description="Average anomaly score across network")

class ClusterItem(BaseModel):
    cluster_id: int = Field(..., example=1, description="K-Means cluster index")
    archetype: str = Field(..., example="Post-exploitation", description="Attacker archetype classification")
    sessions_count: int = Field(..., example=12, description="Sessions belonging to cluster")
    share_percentage: int = Field(..., example=35, description="Percentage of overall traffic")
    color: str = Field(..., example="#ef7f88", description="UI cluster color code")
    centroid_features: Dict[str, float] = Field(..., description="K-Means normalized feature centroid coordinates")
    description: str = Field(..., example="Download, persistence, or lateral-movement behavior.", description="Behavior description")

class ClusterListResponse(BaseModel):
    clusters: List[ClusterItem] = Field(..., description="Extracted K-Means behavioral clusters")
    total_clusters: int = Field(..., example=5, description="Total number of behavioral clusters")
    total_analyzed: int = Field(..., example=128, description="Total sessions analyzed")

class DangerousIPItem(BaseModel):
    ip: str = Field(..., example="185.220.101.42")
    country: str = Field(..., example="Germany")
    flag: str = Field(..., example="DE")
    sessions: int = Field(..., example=14)
    severity: str = Field(..., example="Critical")
    score: float = Field(..., example=0.94)

class MalwareFamilyItem(BaseModel):
    family: str = Field(..., example="Mirai Botnet")
    count: int = Field(..., example=184)
    share: int = Field(..., example=38)

class IntelligenceResponse(BaseModel):
    global_threat_score: int = Field(..., example=78, description="Global network threat posture score (0 to 100)")
    ai_confidence: float = Field(..., example=94.2, description="Model classification confidence percentage")
    highest_threat_archetype: str = Field(..., example="Post-exploitation")
    most_active_country: str = Field(..., example="India")
    average_risk_score: float = Field(..., example=0.68)
    archetypes: List[ThreatSummary] = Field(..., description="K-Means cluster distribution")
    top_malware: List[MalwareFamilyItem] = Field(..., description="Observed malware payload classifications")
    dangerous_ips: List[DangerousIPItem] = Field(..., description="High priority threat actors")

    # Threat Summaries & MITRE ATT&CK Matrix
    top_countries_summary: Optional[List[Dict[str, Any]]] = Field(None, description="Top attack source countries summary")
    highest_risk_regions: Optional[List[Dict[str, Any]]] = Field(None, description="Highest threat risk regions")
    mitre_matrix: Optional[List[Dict[str, str]]] = Field(None, description="Aggregated MITRE ATT&CK techniques matrix")
