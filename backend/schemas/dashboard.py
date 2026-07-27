from typing import List
from pydantic import BaseModel, Field
from backend.schemas.session import SessionSummary
from backend.schemas.status import APIStatus

class DashboardMetrics(BaseModel):
    label: str = Field(..., example="Observed sessions", description="Metric description title")
    value: str = Field(..., example="1,248", description="Metric numeric string value")
    change: str = Field(..., example="+18.4%", description="Percentage or qualitative change label")
    tone: str = Field(..., example="blue", description="UI tone indicator: blue, green, coral, violet")
    icon: str = Field(..., example="◫", description="UI icon glyph")

class GeographyItem(BaseModel):
    country: str = Field(..., example="Germany", description="Source country name")
    code: str = Field(..., example="DE", description="ISO 3166-1 alpha-2 code")
    sessions: int = Field(..., example="126", description="Attack session count from country")
    color: str = Field(..., example="#6fd6aa", description="UI map color code")

class OverviewSection(BaseModel):
    generatedAt: str = Field(..., example="2026-07-27T16:00:00Z", description="Telemetry snapshot generation timestamp")
    metrics: List[DashboardMetrics] = Field(..., description="Executive top metric summary grid")
    geography: List[GeographyItem] = Field(..., description="Top source countries breakdown")

class TimelinePoint(BaseModel):
    time: str = Field(..., example="14:00", description="Hour time-window string (HH:MM UTC)")
    sessions: int = Field(..., example=89, description="Total sessions recorded in hour window")
    anomalies: int = Field(..., example=8, description="Anomalous behavior count in hour window")

class ThreatSummary(BaseModel):
    label: str = Field(..., example="Reconnaissance bot", description="Archetype title")
    sessions: int = Field(..., example=502, description="Total archetype session count")
    share: int = Field(..., example=39, description="Percentage share of total traffic")
    color: str = Field(..., example="#47a8ff", description="UI cluster color")
    description: str = Field(..., example="Automated probes with short command sequences.", description="Behavioral description")

class DashboardResponse(BaseModel):
    overview: OverviewSection = Field(..., description="Executive metric and geography overview")
    timeline: List[TimelinePoint] = Field(..., description="24-hour attack volume and anomaly timeline")
    sessions: List[SessionSummary] = Field(..., description="Recent session activity snapshot")
    intelligence: List[ThreatSummary] = Field(..., description="Archetype cluster threat breakdown")
    health: APIStatus = Field(..., description="Backend system component health status")
