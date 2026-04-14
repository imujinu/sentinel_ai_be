from typing import List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(20), unique=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(50))

    # 관계 설정 (문자열로 참조)
    routes: Mapped[List["Route"]] = relationship(back_populates="vehicle")