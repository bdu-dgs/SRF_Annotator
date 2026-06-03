from functools import lru_cache
import json
from pathlib import Path
import sys
import time
import traceback
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.annotation import AnnotationResult


load_dotenv()

_WUSTL_ACCESS_TOKEN: str | None = None
_WUSTL_ACCESS_TOKEN_EXPIRES_AT = 0.0


class SRFStructuredOutput(BaseModel):
    note_id: str = Field(description="The note identifier provided by the user.")
    srf_present: bool = Field(description="True if any social risk factor is present.")
    srf_type: str | None = Field(
        default=None,
        description="The detected SRF category, such as Transportation, Housing, Food, Financial, Social Support, or Supplemental Aspect.",
    )
    supporting_phrase: str | None = Field(
        default=None,
        description="The exact sentence or phrase from the note that supports the SRF decision.",
    )


def annotate_note(note_id: str, note_text: str) -> AnnotationResult:
    """Annotate a clinical note with LangChain through the WashU AI Gateway."""
    try:
        from langchain_core.prompts import ChatPromptTemplate
    except ModuleNotFoundError as exc:
        raise RuntimeError("LangChain is not installed. Run pip install -r requirements.txt.") from exc

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Return only the requested structured JSON. Use null for unavailable fields.",
            ),
            (
                "human",
                "{prompt_text}\n\nNote ID: {note_id}\n\nClinical Note:\n{note_text}",
            ),
        ]
    )
    try:
        chain = prompt | _get_llm().with_structured_output(SRFStructuredOutput)
        output = chain.invoke(
            {
                "prompt_text": _load_prompt_text(),
                "note_id": note_id,
                "note_text": note_text,
            }
        )
    except Exception as exc:
        _log_gateway_exception(exc)
        raise

    return AnnotationResult(
        note_id=note_id,
        srf_present=output.srf_present,
        srf_type=output.srf_type,
        supporting_phrase=output.supporting_phrase,
    )


def _get_llm():
    try:
        from langchain_openai import ChatOpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError("langchain-openai is not installed. Run pip install -r requirements.txt.") from exc

    _validate_wustl_gateway_settings()

    print(f"WashU AI Gateway model: {settings.model_name}", file=sys.stderr)
    print(f"WashU AI Gateway base_url: {settings.wustl_ai_gateway_base_url}", file=sys.stderr)

    return ChatOpenAI(
        model=settings.model_name,
        api_key=_get_wustl_access_token(),
        base_url=settings.wustl_ai_gateway_base_url,
        default_headers={"X-Api-Key": settings.wustl_api_key},
        temperature=0,
    )


def _validate_wustl_gateway_settings() -> None:
    missing = [
        name
        for name, value in {
            "WUSTL_CLIENT_ID": settings.wustl_client_id,
            "WUSTL_CLIENT_SECRET": settings.wustl_client_secret,
            "WUSTL_API_KEY": settings.wustl_api_key,
            "MODEL_NAME": settings.model_name,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing WashU AI Gateway environment variables: {', '.join(missing)}")


def _get_wustl_access_token() -> str:
    global _WUSTL_ACCESS_TOKEN, _WUSTL_ACCESS_TOKEN_EXPIRES_AT

    if _WUSTL_ACCESS_TOKEN and time.time() < _WUSTL_ACCESS_TOKEN_EXPIRES_AT:
        return _WUSTL_ACCESS_TOKEN

    payload = urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": settings.wustl_client_id,
            "client_secret": settings.wustl_client_secret,
            "scope": settings.wustl_token_scope,
        }
    ).encode("utf-8")
    request = Request(
        settings.wustl_token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            token_response_body = response.read().decode("utf-8")
            token_payload = json.loads(token_response_body)
            print(
                f"WashU token acquisition response: {_redact_token_payload(token_payload)}",
                file=sys.stderr,
            )
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"WashU token acquisition response body: {error_body}", file=sys.stderr)
        raise RuntimeError(f"WashU AI Gateway token request failed with HTTP {exc.code}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"WashU AI Gateway token request failed: {exc.reason}") from exc

    access_token = token_payload.get("access_token")
    if not access_token:
        raise RuntimeError("WashU AI Gateway token response did not include access_token.")

    expires_in = int(token_payload.get("expires_in", 3600))
    _WUSTL_ACCESS_TOKEN = access_token
    _WUSTL_ACCESS_TOKEN_EXPIRES_AT = time.time() + max(expires_in - 60, 0)
    return _WUSTL_ACCESS_TOKEN


def _redact_token_payload(token_payload: dict) -> dict:
    redacted = dict(token_payload)
    if "access_token" in redacted:
        redacted["access_token"] = "<redacted>"
    return redacted


def _log_gateway_exception(exc: Exception) -> None:
    print("WashU AI Gateway request failed.", file=sys.stderr)
    print(f"MODEL_NAME={settings.model_name}", file=sys.stderr)
    print(f"base_url={settings.wustl_ai_gateway_base_url}", file=sys.stderr)

    response = getattr(exc, "response", None)
    response_body = None
    if response is not None:
        response_body = getattr(response, "text", None)
        if callable(response_body):
            response_body = response_body()
        if response_body is None and hasattr(response, "content"):
            content = response.content
            if isinstance(content, bytes):
                response_body = content.decode("utf-8", errors="replace")
            else:
                response_body = str(content)

    if response_body is None:
        response_body = getattr(exc, "body", None)

    print(f"Gateway response body: {response_body}", file=sys.stderr)
    print("Full traceback:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)


@lru_cache(maxsize=1)
def _load_prompt_text() -> str:
    prompt_path = Path(settings.srf_prompt_path)
    if not prompt_path.exists() and prompt_path.parts[:1] == ("backend",):
        prompt_path = Path(__file__).resolve().parents[2] / Path(*prompt_path.parts[1:])
    if not prompt_path.exists():
        raise FileNotFoundError(f"SRF prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")
