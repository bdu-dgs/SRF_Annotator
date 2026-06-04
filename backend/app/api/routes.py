from datetime import datetime, timezone
from pathlib import Path
import sys
import traceback

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.models.annotation import AnnotationBatchResponse, SaveAnnotationsRequest
from app.services.csv_service import read_notes_csv, save_annotations_csv
from app.services.llm_service import annotate_note, debug_llm_hello


router = APIRouter()


@router.post("/analyze", response_model=AnnotationBatchResponse)
async def analyze(file: UploadFile = File(...)):
    """Upload a CSV of clinical notes and return structured SRF annotations."""
    print("=== ENTERED FUNCTION analyze ===")
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload must be a CSV file.")

    try:
        dataframe = read_notes_csv(await file.read())
        results = [
            annotate_note(note_id=str(row.note_id), note_text=str(row.text))
            for row in dataframe.itertuples(index=False)
        ]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        print("Analyze endpoint failed.", file=sys.stderr)
        print(f"MODEL_NAME={settings.model_name}", file=sys.stderr)
        print("Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Analyze failed with {type(exc).__name__}: {exc}",
        ) from exc

    return AnnotationBatchResponse(results=results)


@router.post("/save_annotations")
async def save_annotations(payload: SaveAnnotationsRequest):
    """Save reviewed annotations to a backend CSV file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = Path(__file__).resolve().parents[2] / "outputs" / f"srf_annotations_{timestamp}.csv"
    saved_path = save_annotations_csv(payload.annotations, output_path)
    return {
        "status": "saved",
        "filename": saved_path.name,
        "path": str(saved_path),
        "rows_saved": len(payload.annotations),
    }


@router.get("/debug-llm")
async def debug_llm():
    """Temporary endpoint for debugging Render WashU LLM connectivity."""
    try:
        content = debug_llm_hello()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Debug LLM request failed with {type(exc).__name__}. Check Render logs.",
        ) from exc

    return {"status": "ok", "response": content}
