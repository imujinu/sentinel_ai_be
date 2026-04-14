from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Float, Index, BigInteger  # ← 수정
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class RoutePoint(Base, TimestampMixin):
    __tablename__ = "route_points"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # ← 수정
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime)

    route: Mapped["Route"] = relationship(back_populates="points")

    __table_args__ = (
        Index("ix_route_recorded", "route_id", "recorded_at"),
    )