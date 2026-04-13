from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.vehicle import VehicleData

router = APIRouter()

@router.websocket("/ws/{vehicleId}")
async def websocket_fleet(websocket: WebSocket, vehicleId: str):
    await websocket.accept()
    manager = websocket.app.state.manager # 매니저도 state에서 관리 권장
    fleet_service = websocket.app.state.fleet_service
    
    try:
        while True:
            raw_data = await websocket.receive_json()
            data = VehicleData(**raw_data)
            
            # Service에 로직 위임
            processed_data = await fleet_service.process_vehicle_data(data)
            
            # 브로드캐스트
            await manager.broadcast(processed_data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)