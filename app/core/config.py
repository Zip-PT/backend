from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    NAVER_CLIENT_ID: str = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET: str = os.getenv("NAVER_CLIENT_SECRET")

    CORS_ORIGINS = [
        "http://127.0.0.1:5173",
        "http://localhost:5173"
    ]


settings = Settings()
