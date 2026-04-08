import asyncio
import random
from connection_manager import manager
from services.fleet_service import fleet_service

class SimulatorService:
    def __init__(self):
        self.vehicles = [
    {"id": "v-1", "plateNumber": "서울 70가 1234", "lat": 37.4970, "lng": 127.0260, "speed": 50, "status": "normal"},
    {"id": "v-2", "plateNumber": "경기 32나 5678", "lat": 37.4820, "lng": 127.0180, "speed": 40, "status": "delayed"},
]

    async def start_simulation(self):
        while True:
            updated_data_list = []
            for v in self.vehicles:
                # 좌표 이동 시뮬레이션
                v["lat"] += random.uniform(-0.0005, 0.0005)
                v["lng"] += random.uniform(-0.0005, 0.0005)
                v["speed"] = random.randint(40, 110)

                # [중요] FleetService를 통해 분석 수행
                analysis_result = await fleet_service.analyze_vehicle(v)
                updated_data_list.append(analysis_result)

            # 분석된 결과(좌표 + 이벤트)를 브로드캐스트
            await manager.broadcast({
                "type": "FLEET_MONITOR_UPDATE",
                "payload": updated_data_list
            })
            
            await asyncio.sleep(1)

simulator_service = SimulatorService()