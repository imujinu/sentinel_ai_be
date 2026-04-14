from typing import List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class Driver(Base, TimestampMixin):
    __tablename__ = "drivers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    license_number: Mapped[str] = mapped_column(String(50), unique=True)
    routes: Mapped[List["Route"]] = relationship(back_populates="driver")