from typing import List, Optional
from datetime import datetime
# [수정] ForeignKey, DateTime을 반드시 import 해야 합니다!
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class Route(Base, TimestampMixin):
    __tablename__ = "routes"
    id: Mapped[int] = mapped_column(primary_key=True)
    # 이제 ForeignKey를 인식합니다.
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    
    # 이제 DateTime을 인식합니다.
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="routes")
    driver: Mapped["Driver"] = relationship(back_populates="routes")
    points: Mapped[List["RoutePoint"]] = relationship(back_populates="route")
    delay_events: Mapped[List["DelayEvent"]] = relationship(back_populates="route")