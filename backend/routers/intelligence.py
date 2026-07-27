from fastapi import APIRouter, status
from backend.schemas.intelligence import (
    IntelligenceResponse,
    AnomalyListResponse,
    ClusterListResponse,
)
from backend.services.intelligence_service import (
    get_intelligence_overview,
    get_detected_anomalies,
    get_cluster_analytics,
)

router = APIRouter(tags=["ML & Behavioral Intelligence"])

@router.get(
    "/intelligence",
    response_model=IntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Machine Learning Threat Posture & Intelligence",
    description="Returns global threat posture scores, AI model confidence, top malware payload classifications, dangerous threat actor IPs, and archetype clusters.",
    responses={
        200: {
            "description": "ML threat intelligence retrieved successfully."
        }
    }
)
def get_intelligence():
    return get_intelligence_overview()

@router.get(
    "/anomalies",
    response_model=AnomalyListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Isolation Forest Detected Anomalies",
    description="Returns sessions scored by Isolation Forest anomaly detection algorithm (scores 0.0 to 1.0) with rule-assisted explanation vectors.",
    responses={
        200: {
            "description": "Isolation Forest anomaly list retrieved successfully."
        }
    }
)
def get_anomalies():
    return get_detected_anomalies()

@router.get(
    "/clusters",
    response_model=ClusterListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get K-Means Attacker Behavioral Clusters",
    description="Returns automatically grouped K-Means attacker behavior clusters with centroid feature coordinates and share percentages.",
    responses={
        200: {
            "description": "K-Means behavioral clusters retrieved successfully."
        }
    }
)
def get_clusters():
    return get_cluster_analytics()
