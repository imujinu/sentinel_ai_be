# app/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 1. DB 주소 (환경변수에서 가져오는 것이 좋음)
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/sentinel_db"

# 2. 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 3. 세션 팩토리 생성 (DB 작업 시 이 세션을 빌려 씀)
async_session = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

# 의존성 주입용 함수 (FastAPI 등에서 사용)
async def get_db():
    async with async_session() as session:
        yield session