# data_models.py
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class RegulationType(str, Enum):
    """Activity types following CDS standards"""
    NO_PARKING = "no_parking"
    NO_STOPPING = "no_stopping"  # Added from CDS
    PARKING = "parking"  # Updated to match CDS
    LOADING = "loading"
    PAID_PARKING = "paid_parking"
    TIME_LIMITED = "time_limited"
    PASSENGER_LOADING = "passenger_loading"
    COMMERCIAL_LOADING = "commercial_loading"

class RateUnitPeriod(str, Enum):
    """Rate unit periods following CDS standards"""
    ROLLING = "rolling"
    CALENDAR = "calendar"

class Rate(BaseModel):
    """CDS-compliant rate information"""
    rate: float
    rate_unit: str  # hour, day, etc.
    rate_unit_period: RateUnitPeriod
    
class TimeSpan(BaseModel):
    """CDS-compliant time span"""
    days_of_week: List[str]  # Changed from days to match CDS
    time_of_day_start: str  # Changed from start_time to match CDS
    time_of_day_end: str    # Changed from end_time to match CDS

class Rule(BaseModel):
    """CDS-compliant rule"""
    activity: str
    max_stay: Optional[int] = None  # Duration in minutes
    user_classes: Optional[List[str]] = None
    rate: Optional[Rate] = None

class CurbPolicy(BaseModel):
    """CDS-compliant curb policy"""
    curb_policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    published_date: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    priority: Optional[int] = None
    time_spans: Optional[List[TimeSpan]] = None
    rules: List[Rule]
    data_source_operator_id: Optional[List[str]] = None

class Location(BaseModel):
    """Geographic location information"""
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class SignData(BaseModel):
    """CDS-compliant sign data"""
    version: str = "1.0"
    time_zone: Optional[str] = None
    last_updated: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    currency: str = "USD"
    location: Optional[Location] = None
    policies: List[CurbPolicy]
    author: Optional[str] = None
    license_url: Optional[str] = None