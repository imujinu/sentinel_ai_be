# services/ai_service.py
from transformers import pipeline

class AIService:
    def __init__(self):
        # 가장 가벼운 텍스트 분류 모델 하나를 로드해봅니다.
        # 나중에 실제 물류 특화 모델로 갈아끼울 자리입니다.
        self.classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased")

    async def predict_accident(self, vehicle_history: list):
        """차량의 과거 경로 데이터를 보고 사고 확률을 예측하는 척 합니다."""
        # 실제로는 여기서 모델 추론이 일어납니다.
        # 지금은 간단하게 텍스트 분석으로 테스트!
        sample_text = "The vehicle speed dropped suddenly and engine heat is rising."
        result = self.classifier(sample_text)
        
        return {
            "probability": 0.85 if result[0]['label'] == 'NEGATIVE' else 0.1,
            "reason": "급격한 속도 저하 및 엔진 과열 감지"
        }

ai_service = AIService()