import whisper
import openai
from fastapi import HTTPException
import os
from datetime import datetime
from app.core.config import settings


class AudioService:
    def __init__(self):
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                    "content": "한국에서 월세 계약을 위해 부동산 매물에 방문한 상태에서 녹음된 텍스트입니다..."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content


audio_service = AudioService()
