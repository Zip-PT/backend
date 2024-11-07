import whisper
import openai
import warnings
from fastapi import HTTPException
import os
from datetime import datetime
from app.core.config import settings


class AudioService:
    def __init__(self):
        # 경고 메시지 무시
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            self.model = whisper.load_model("base")
        openai.api_key = settings.OPENAI_API_KEY

    async def process_audio(self, audio_file):
        temp_file_name = None
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file_name = f"temp_audio_{timestamp}.mp3"

            # 파일 저장
            with open(temp_file_name, "wb") as buffer:
                buffer.write(await audio_file.read())

            # Whisper 변환
            result = self.model.transcribe(temp_file_name)
            transcribed_text = result["text"]

            # GPT 요약
            summary = await self._get_summary(transcribed_text)

            return {
                "transcription": transcribed_text,
                "summary": summary
            }
        finally:
            if temp_file_name and os.path.exists(temp_file_name):
                os.remove(temp_file_name)

    async def _get_summary(self, text):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
부동산 매물 방문 시 녹음된 음성을 텍스트로 변환한 내용입니다. 
다음 카테고리별로 중요 정보를 구조화하여 요약해주세요:

1. 비용 정보
- 보증금
- 월세
- 관리비 (포함/미포함 항목 구분)
- 기타 비용 (중개수수료, 권리금 등)

2. 매물 상태
- 방향/채광
- 환기/통풍
- 수압/온수
- 누수/곰팡이 여부
- 방음/층간소음

3. 시설/옵션
- 기본 제공 가전/가구
- 주방 시설
- 욕실 상태
- 보안 시설

4. 주변 환경
- 교통 접근성
- 편의시설
- 소음이나 악취 등 환경 문제

위 정보들 중 언급되지 않은 항목은 생략하고, 
언급된 내용만 간단명료하게 정리해주세요.
특별히 중요하거나 주의가 필요한 사항은 별도로 강조해주세요.
"""},
                {"role": "user", "content": text}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
