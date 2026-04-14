from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # 접속 중인 모든 웹소켓 세션을 담는 리스트 (자바의 List<WebSocketSession> 역할)
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """새로운 클라이언트가 접속했을 때 호출"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"새로운 연결: 현재 {len(self.active_connections)}명 접속 중")

    def disconnect(self, websocket: WebSocket):
        """클라이언트가 나갔을 때 호출"""
        self.active_connections.remove(websocket)
        print(f"연결 종료: 현재 {len(self.active_connections)}명 접속 중")

    async def broadcast(self, message: dict):
        """접속한 모든 사람에게 실시간 데이터 전송 (핵심!)"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # 연결이 끊긴 세션이 있을 경우 에러 방지
                print(f"전송 실패: {e}")

# 어디서든 쓸 수 있게 객체 하나를 미리 생성해둡니다.
manager = ConnectionManager()