from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.annotation import AnnotationResult


load_dotenv()


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
    """Annotate a clinical note with LangChain and OpenAI structured output."""
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
    chain = prompt | _get_llm().with_structured_output(SRFStructuredOutput)
    output = chain.invoke(
        {
            "prompt_text": _load_prompt_text(),
            "note_id": note_id,
            "note_text": note_text,
        }
    )

    return AnnotationResult(
        note_id=note_id,
        srf_present=output.srf_present,
        srf_type=output.srf_type,
        supporting_phrase=output.supporting_phrase,
    )


@lru_cache(maxsize=1)
def _get_llm():
    try:
        from langchain_openai import ChatOpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError("langchain-openai is not installed. Run pip install -r requirements.txt.") from exc

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )


@lru_cache(maxsize=1)
def _load_prompt_text() -> str:
    prompt_path = Path(settings.srf_prompt_path)
    if not prompt_path.exists() and prompt_path.parts[:1] == ("backend",):
        prompt_path = Path(__file__).resolve().parents[2] / Path(*prompt_path.parts[1:])
    if not prompt_path.exists():
        raise FileNotFoundError(f"SRF prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")
