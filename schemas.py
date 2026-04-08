from pydantic import BaseModel
from typing import List, Optional

class VehicleBase(BaseModel):
    id: str
    plateNumber: str
    lat: float
    lng: float
    status: str  # "normal", "delayed", "critical"

class AIAlert(BaseModel):
    id: str
    severity: str
    message: str
    vehicle: str