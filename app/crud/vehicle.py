# ============================================================
# app/crud/vehicle.py
#
# 📌 "CRUD"란?
#   Create / Read / Update / Delete — DB 조작 함수만 모아두는 레이어입니다.
#   라우터(API)에서 직접 DB 쿼리를 작성하면 코드가 뒤섞여 복잡해지기 때문에
#   쿼리 로직을 여기에 분리해 관리합니다.
#
#   [데이터 흐름]
#   API 라우터 → (여기 함수 호출) → DB 조회 → 결과 반환 → 라우터에서 응답 생성
# ============================================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func   # ✅ [수정] func 추가 (count 집계에 필요)
from app.models import Vehicle, Driver, RoutePoint, Route
from datetime import datetime


# ──────────────────────────────────────────────
# 1. 전체 차량 목록 + 각 차량의 현재(최신) 위치 조회
# ──────────────────────────────────────────────
async def get_all_vehicles_with_location(db: AsyncSession) -> list[dict]:
    """
    모든 차량과 해당 차량에 배정된 기사, 그리고 가장 최근 GPS 좌표를 함께 조회합니다.

    [쿼리 구조]
    vehicles
      LEFT JOIN drivers       → 기사가 없는 차량도 포함하기 위해 LEFT JOIN
      LEFT JOIN route_points  → 아직 운행 기록이 없는 차량도 포함하기 위해 LEFT JOIN
                                단, route_points 중 가장 최신 1건만 가져옴 (서브쿼리 사용)
    """

    # ✅ [수정] RoutePoint에는 vehicle_id가 없고 route_id만 있습니다.
    #    따라서 Route 테이블을 경유해서 차량과 연결해야 합니다.
    #    Vehicle → Route → RoutePoint 순서로 JOIN합니다.
    #
    #    [수정 전 - 잘못된 코드]
    #      .outerjoin(RoutePoint, RoutePoint.vehicle_id == Vehicle.id)  ← vehicle_id 컬럼 없음!
    #
    #    [수정 후 - 올바른 코드]
    #      Route를 먼저 JOIN하고, RoutePoint는 Route를 통해 연결

    # 서브쿼리: 차량(vehicle_id)별 가장 최신 route_point의 recorded_at 값을 구함
    # 이 값을 이용해 "가장 최신 좌표 1건"만 JOIN 조건에 사용합니다.
    latest_recorded_at_subquery = (
        select(RoutePoint.recorded_at)
        .join(Route, RoutePoint.route_id == Route.id)       # route_points → routes 연결
        .where(Route.vehicle_id == Vehicle.id)              # 해당 차량의 경로만 필터
        .order_by(RoutePoint.recorded_at.desc())            # 최신순 정렬
        .limit(1)                                           # 딱 1건만
        .correlate(Vehicle)                                 # 바깥 쿼리의 Vehicle과 연관
        .scalar_subquery()                                  # 단일 값으로 사용하겠다는 선언
    )

    stmt = (
        select(
            Vehicle.id.label("vehicle_id"),                 # ✅ [수정] 명시적으로 레이블 지정
            Vehicle.plate_number.label("plate"),            # ✅ [수정] 실제 컬럼명은 plate_number
            Driver.name.label("driver_name"),
            RoutePoint.latitude.label("lat"),               # ✅ [수정] 실제 컬럼명은 latitude
            RoutePoint.longitude.label("lng"),              # ✅ [수정] 실제 컬럼명은 longitude
            RoutePoint.recorded_at.label("last_updated"),
            # ※ RoutePoint에 speed 컬럼이 없으므로 제거했습니다.
            #   speed가 필요하다면 RoutePoint 모델에 컬럼을 추가해야 합니다.
        )
        # 기사가 없는 차량도 조회하기 위해 LEFT OUTER JOIN 사용
        .outerjoin(Driver, Vehicle.driver_id == Driver.id)
        # 가장 최신 route_point를 가져오기 위해 Route를 경유해서 JOIN
        .outerjoin(
            Route,
            Route.vehicle_id == Vehicle.id
        )
        .outerjoin(
            RoutePoint,
            and_(
                RoutePoint.route_id == Route.id,
                RoutePoint.recorded_at == latest_recorded_at_subquery,
            ),
        )
    )

    result = await db.execute(stmt)
    # .mappings() → 결과를 dict처럼 키로 접근 가능한 형태로 반환
    return result.mappings().all()


# ──────────────────────────────────────────────
# 2. 특정 차량의 경로 이력 조회 (날짜 범위 + 페이지네이션)
# ──────────────────────────────────────────────
async def get_route_points_by_vehicle(
    db: AsyncSession,
    vehicle_id: int,
    start_date: datetime,
    end_date: datetime,
    limit: int = 1000,      # 한 번에 가져올 최대 포인트 수 (기본값 1000)
    offset: int = 0,        # 몇 번째 데이터부터 가져올지 (페이지네이션)
) -> tuple[list[RoutePoint], int]:
    """
    특정 차량의 GPS 기록 포인트를 날짜 범위로 조회합니다.
    페이지네이션을 지원하며, 전체 건수(total)도 함께 반환합니다.

    Returns:
        (RoutePoint 목록, 전체 건수)
    """

    # ✅ [수정] RoutePoint는 route_id로 연결되므로,
    #    vehicle_id로 직접 필터할 수 없습니다.
    #    Route 테이블을 서브쿼리로 경유해야 합니다.

    # 해당 차량의 모든 route_id를 먼저 구하는 서브쿼리
    vehicle_route_ids = (
        select(Route.id)
        .where(Route.vehicle_id == vehicle_id)
        .scalar_subquery()
    )

    # 공통 필터 조건 (재사용을 위해 변수로 분리)
    common_filters = and_(
        RoutePoint.route_id.in_(vehicle_route_ids),         # 해당 차량의 경로에 속하는 포인트만
        RoutePoint.recorded_at >= start_date,               # 시작 날짜 이후
        RoutePoint.recorded_at <= end_date,                 # 종료 날짜 이전
    )

    # ── 전체 건수 카운트 쿼리 ──
    # ✅ [수정] func이 누락되어 있었습니다. 위에서 import 추가했습니다.
    count_stmt = (
        select(func.count())                                # COUNT(*) 집계 함수
        .select_from(RoutePoint)
        .where(common_filters)
    )
    total = await db.scalar(count_stmt)                     # 단일 숫자 값으로 바로 꺼내기

    # ── 실제 데이터 조회 쿼리 ──
    stmt = (
        select(RoutePoint)
        .where(common_filters)
        .order_by(RoutePoint.recorded_at.asc())             # 시간순 정렬 (경로 재현용)
        .limit(limit)                                       # 최대 N건만
        .offset(offset)                                     # M번째부터 시작 (페이지 이동)
    )
    result = await db.execute(stmt)

    # .scalars().all() → ORM 객체(RoutePoint) 리스트로 반환
    return result.scalars().all(), total