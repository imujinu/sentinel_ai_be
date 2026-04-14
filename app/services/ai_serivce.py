from transformers import pipeline
import torch

class AIService:
    def __init__(self):
        # 1. 감성 분석(Sentiment Analysis) 모델 로드 (가장 가볍고 범용적임)
        # 실제로는 '사고/정체 분류 모델'로 갈아끼우는 지점입니다.
        print("🤖 AI 모델 로딩 중... 잠시만 기다려주세요.")
        self.classifier = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1 # CPU 사용 (GPU가 있다면 0으로 설정 가능)
        )
        print("✅ AI 모델 로드 완료!")

    async def analyze_status(self, text: str):
        """차량 리포트 텍스트를 분석하여 위험도 산출"""
        # 모델 추론 (Inference)
        result = self.classifier(text)[0]
        
        # NEGATIVE(부정적)일 경우 위험으로 간주 (Score는 확률값)
        is_danger = result['label'] == 'NEGATIVE'
        confidence = result['score']
        
        return is_danger, confidence

# 싱글톤 객체 생성
ai_service = AIService()