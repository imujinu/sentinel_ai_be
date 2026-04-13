from pydantic import BaseModel, Field
from datetime import datetime

class VehicleData(BaseModel):
    lat: float
    lng: float
    speed: float
    # 비정형 데이터나 선택적 필드 처리도 가능
    timestamp: datetime = Field(default_factory=datetime.now)