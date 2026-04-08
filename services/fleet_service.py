import math
from datetime import datetime

class FleetService:
    def __init__(self):
        # 1. 감시 구역 설정
        self.WATCH_ZONES = [
            {"name": "강남역 공사구간", "lat": 37.4979, "lng": 127.0276, "radius": 0.005},
            {"name": "서초 나들목 정체구간", "lat": 37.4833, "lng": 127.0192, "radius": 0.008}
        ]

    async def analyze_vehicle(self, data: dict):
        # 2. 실시간 분석 시작
        lat, lng = data["lat"], data["lng"]
        plate = data["plateNumber"]
        speed = data["speed"]
        
        event = None
        
        # 지오펜싱 체크
        for zone in self.WATCH_ZONES:
            dist = math.sqrt((lat - zone["lat"])**2 + (lng - zone["lng"])**2)
            if dist < zone["radius"]:
                event = {
                    "type": "ZONE_ALARM",
                    "level": "warning",
                    "message": f"🚨 [알람] {plate} 차량이 '{zone['name']}'에 진입했습니다."
                }
                # 서버 터미널에 실시간 로그 찍기 (가시성 확보)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {event['message']}")

        # 과속 체크
        if speed > 100:
            event = {
                "type": "SPEED_ALARM",
                "level": "critical",
                "message": f"🔥 [긴급] {plate} 차량 과속 중! ({speed}km/h)"
            }
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {event['message']}")

        return {"data": data, "event": event}

fleet_service = FleetService()