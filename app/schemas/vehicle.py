# ============================================================
# app/schemas/vehicle.py
#
# 📌 "스키마(Schema)"란?
#   API가 클라이언트(프론트엔드)에게 돌려줄 응답의 "모양"을 정의하는 파일입니다.
#   Pydantic의 BaseModel을 상속받아 만들며,
#   FastAPI가 자동으로 JSON 직렬화(변환) + 유효성 검사를 해줍니다.
#
#   [데이터 흐름]
#   DB 조회 결과 → CRUD → (여기서 스키마로 변환) → API 응답 JSON
# ============================================================

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ──────────────────────────────────────────────
# 1. 차량 현재 위치 스냅샷
#    GET /api/v1/vehicles 응답에서 차량 1대의 데이터를 표현합니다.
# ──────────────────────────────────────────────
class VehicleCurrentLocation(BaseModel):
    vehicle_id: int                         # 차량 고유 ID (DB primary key)
    plate: str                              # 번호판 (예: "서울 70가 1234")
    driver_name: Optional[str]             # 배정된 기사 이름 (없을 수도 있어서 Optional)
    lat: Optional[float]                   # 현재 위도 (아직 운행 전이면 None)
    lng: Optional[float]                   # 현재 경도
    speed: Optional[float]                 # 현재 속도 (km/h)
    last_updated: Optional[datetime]       # 마지막으로 위치가 기록된 시각


# ──────────────────────────────────────────────
# 2. GeoJSON LineString 도형
#
#    📌 GeoJSON이란?
#      지도 데이터를 표현하는 국제 표준 JSON 형식입니다.
#      Leaflet, Mapbox, Google Maps 등 대부분의 지도 라이브러리가 이 형식을 바로 읽을 수 있습니다.
#
#    LineString = 여러 좌표(점)를 이어 만든 "선" 도형
#    좌표 순서 주의: GeoJSON 스펙은 반드시 [경도(lng), 위도(lat)] 순서입니다!
#    (우리가 일상에서 쓰는 "위도, 경도" 순서와 반대입니다)
# ──────────────────────────────────────────────
class GeoJSONLineString(BaseModel):
    type: str = "LineString"               # GeoJSON 스펙 고정값
    coordinates: list[list[float]]         # [[lng, lat], [lng, lat], ...] 형태


# ──────────────────────────────────────────────
# 3. 경로 이력 Feature (단일 경로 1개를 감싸는 GeoJSON 객체)
#
#    GeoJSON Feature = 도형(geometry) + 부가 정보(properties)를 묶은 단위
# ──────────────────────────────────────────────
class RouteHistoryFeature(BaseModel):
    type: str = "Feature"                  # GeoJSON 스펙 고정값
    geometry: GeoJSONLineString            # 실제 선 도형 데이터
    properties: dict                       # 차량 ID, 조회 기간 등 부가 정보


# ──────────────────────────────────────────────
# 4. 경로 이력 전체 응답 (FeatureCollection)
#
#    FeatureCollection = Feature 여러 개를 담는 GeoJSON 최상위 컨테이너
#    GET /api/v1/vehicles/{id}/history 의 최종 응답 형태입니다.
# ──────────────────────────────────────────────
class RouteHistoryResponse(BaseModel):
    type: str = "FeatureCollection"        # GeoJSON 스펙 고정값
    features: list[RouteHistoryFeature]    # Feature 목록 (보통 1개)
    total_points: int                      # 전체 좌표 개수 (페이지네이션 계산용)