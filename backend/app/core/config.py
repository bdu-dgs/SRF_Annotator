import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = "SRF LLM Annotator"
    wustl_client_id: str | None = os.getenv("WUSTL_CLIENT_ID")
    wustl_client_secret: str | None = os.getenv("WUSTL_CLIENT_SECRET")
    wustl_api_key: str | None = os.getenv("WUSTL_API_KEY")
    model_name: str | None = os.getenv("MODEL_NAME")
    wustl_token_url: str = (
        "https://login.microsoftonline.com/4ccca3b5-71cd-4e6d-974b-4d9beb96c6d6/oauth2/v2.0/token"
    )
    wustl_token_scope: str = "api://bbeee386-60d6-4ba4-b9a7-631763f66065/.default"
    wustl_ai_gateway_base_url: str = "https://aiapi.wustl.edu/models/v2"
    srf_prompt_path: str = os.getenv("SRF_PROMPT_PATH", "backend/prompts/srf_prompt.txt")
    cors_origins: list[str] = [
        "https://srf-annotator.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]


settings = Settings()
