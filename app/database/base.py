from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# 모든 모델이 상속받을 최상위 클래스
class Base(DeclarativeBase):
    pass

# 모든 테이블에 공통으로 들어갈 컬럼들 (상속용)
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now()
    )