import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import http_exception_handler, global_exception_handler
from app.api.websocket import router as ws_router
from app.services.simulator_service import start_simulation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 실행
    # 시뮬레이터 백그라운드 실행
    task = asyncio.create_task(start_simulation())
    
    yield
    
    # 서버 종료 시 실행
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Sentinel AI Backend",
    description="Real-time Fleet Tracking and Delay Analysis System",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 설정
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 예외 핸들러 등록
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 라우터 등록
app.include_router(ws_router)

@app.get("/")
async def read_root():
    return {"success": True, "data": {"message": "Sentinel AI Backend is Running!"}, "error": None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
