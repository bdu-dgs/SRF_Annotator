import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = "SRF LLM Annotator"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    srf_prompt_path: str = os.getenv("SRF_PROMPT_PATH", "backend/prompts/srf_prompt.txt")
    cors_origins: list[str] = [
        "https://srf-annotator.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]


settings = Settings()
