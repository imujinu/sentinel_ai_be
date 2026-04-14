# ============================================================
# app/api/v1/vehicles.py
#
# 📌 "라우터(Router)"란?
#   클라이언트의 HTTP 요청(GET, POST 등)을 받아서
#   적절한 CRUD 함수를 호출하고, 결과를 JSON으로 응답하는 레이어입니다.
#
#   이 파일은 비즈니스 로직이나 DB 쿼리를 직접 작성하지 않고
#   crud/vehicle.py의 함수에 위임(delegation)합니다.
#
#   [데이터 흐름]
#   HTTP 요청 → (여기서 요청 파싱 + 유효성 검사) → CRUD 함수 호출 → JSON 응답 반환
# ============================================================

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.db.session import get_db
from app.crud.vehicle import get_all_vehicles_with_location, get_route_points_by_vehicle

# APIRouter: FastAPI의 라우터 객체
# prefix="/api/v1/vehicles" → 이 라우터의 모든 엔드포인트 앞에 자동으로 붙는 경로
# tags=["vehicles"]         → Swagger 문서(/docs)에서 그룹핑할 때 사용
router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])


# ──────────────────────────────────────────────
# 1. 전체 차량 목록 + 현재 위치 조회
#    GET /api/v1/vehicles
# ──────────────────────────────────────────────
@router.get("")
async def get_vehicles(db: AsyncSession = Depends(get_db)):
    """
    모든 차량의 현재 위치와 기사 정보를 반환합니다.

    Depends(get_db): FastAPI의 의존성 주입(Dependency Injection)
      → 요청이 들어올 때마다 DB 세션을 자동으로 생성해서 함수에 주입해줍니다.
      → 함수가 끝나면 세션을 자동으로 닫아줍니다. (커넥션 누수 방지)
    """

    # CRUD 레이어에 DB 조회를 위임
    rows = await get_all_vehicles_with_location(db)

    # ✅ [수정] CRUD에서 레이블을 명시적으로 지정했으므로
    #    더 이상 방어 코드(if "vehicle_id" in r else ...)가 필요 없습니다.
    #    r["vehicle_id"]로 일관되게 접근합니다.
    #
    #    [수정 전 - 불안정한 코드]
    #      "vehicle_id": r["vehicle_id"] if "vehicle_id" in r else r.Vehicle.id
    #      "plate": r.Vehicle.plate  ← 실제 컬럼명은 plate_number
    #
    #    [수정 후 - 안정적인 코드]
    #      CRUD에서 .label("vehicle_id"), .label("plate") 로 지정했으므로 직접 접근
    return {
        "success": True,
        "data": [
            {
                "vehicle_id": r["vehicle_id"],
                "plate": r["plate"],
                "driver_name": r["driver_name"],
                "lat": r["lat"],
                "lng": r["lng"],
                "last_updated": r["last_updated"],
            }
            for r in rows  # 조회된 모든 행을 dict 리스트로 변환
        ],
    }


# ──────────────────────────────────────────────
# 2. 특정 차량의 경로 이력 조회
#    GET /api/v1/vehicles/{vehicle_id}/history
#
#    요청 예시:
#      GET /api/v1/vehicles/1/history
#          ?start_date=2025-04-01T00:00:00
#          &end_date=2025-04-01T23:59:59
#          &limit=500
#          &offset=0
# ──────────────────────────────────────────────
@router.get("/{vehicle_id}/history")
async def get_vehicle_history(
    vehicle_id: int,                        # URL 경로에서 추출 (예: /vehicles/1/history → 1)
    # Query(...) → 쿼리 파라미터. ...는 "필수값"이라는 의미 (기본값 없음)
    start_date: datetime = Query(..., description="ISO 8601, ex) 2025-04-01T00:00:00"),
    end_date: datetime = Query(..., description="ISO 8601, ex) 2025-04-01T23:59:59"),
    limit: int = Query(default=1000, le=5000),  # 최대 5000건 제한 (le = less than or equal)
    offset: int = Query(default=0, ge=0),       # 음수 방지 (ge = greater than or equal)
    db: AsyncSession = Depends(get_db),
):
    """
    특정 차량의 GPS 이동 경로를 GeoJSON 형태로 반환합니다.
    지도 라이브러리에서 바로 사용할 수 있는 표준 형식입니다.
    """

    # ── 입력값 유효성 검사 ──
    # start_date가 end_date보다 크거나 같으면 의미 없는 조회이므로 에러 반환
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date"
        )

    # CRUD 레이어에 DB 조회를 위임
    # points = RoutePoint 객체 리스트, total = 전체 건수
    points, total = await get_route_points_by_vehicle(
        db, vehicle_id, start_date, end_date, limit, offset
    )

    # ── GeoJSON 좌표 변환 ──
    # 📌 주의: GeoJSON 스펙은 [경도(lng), 위도(lat)] 순서입니다!
    #          우리가 일상에서 쓰는 "위도, 경도"와 순서가 반대입니다.
    #          이 부분은 실수가 잦은 곳이므로 항상 주의하세요.
    coordinates = [[p.longitude, p.latitude] for p in points]  # ✅ [수정] 실제 컬럼명 사용

    # ── GeoJSON FeatureCollection 구조 생성 ──
    # 지도 라이브러리가 바로 읽을 수 있는 표준 GeoJSON 형태로 조립합니다.
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",   # 점들을 이은 "선" 도형
                    "coordinates": coordinates,
                },
                "properties": {             # 도형 외의 부가 정보
                    "vehicle_id": vehicle_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "point_count": len(points),     # 현재 페이지에서 반환된 포인트 수
                },
            }
        ],
        "total_points": total,  # 전체 포인트 수 (페이지네이션 UI에 표시용)
        "limit": limit,         # 요청한 limit 값 그대로 반환 (클라이언트 참고용)
        "offset": offset,       # 요청한 offset 값 그대로 반환
    }

    return {"success": True, "data": geojson}