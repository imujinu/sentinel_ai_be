from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime  # ← 수정
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class DelayEvent(Base, TimestampMixin):
    __tablename__ = "delay_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    cause: Mapped[str] = mapped_column(String(255))
    delay_minutes: Mapped[int] = mapped_column()
    occurred_at: Mapped[datetime] = mapped_column(DateTime)

    route: Mapped["Route"] = relationship(back_populates="delay_events")