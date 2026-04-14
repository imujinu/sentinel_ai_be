from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal, List

# 실시간 위치 정보 업데이트 스키마
class LocationUpdate(BaseModel):
    vehicle_id: int
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    speed: float = Field(..., description="현재 속도 (km/h)")
    timestamp: datetime = Field(default_factory=datetime.now)

# 차량 상태 정보 스키마
class VehicleStatus(BaseModel):
    id: int
    plate: str = Field(..., description="차량 번호판")
    current_lat: float
    current_lng: float
    delay_status: bool = Field(False, description="지연 여부")
    last_updated: datetime

# AI 지연 분석 결과 스키마
class DelayAnalysisResult(BaseModel):
    is_delayed: bool
    severity: Literal["정상", "경미", "심각"]
    estimated_delay_min: int = Field(..., description="예상 지연 시간 (분)")
    reason: str = Field(..., description="지연 원인 분석 내용")

# AI 채팅 메시지 스키마
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    context_used: Optional[dict] = Field(None, description="분석에 사용된 데이터 컨텍스트")

    class Config:
        from_attributes = True
