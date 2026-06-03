from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd

from app.models.annotation import AnnotationResult


NOTE_ID_COLUMNS = ("note_id", "id", "note id", "noteid")
NOTE_TEXT_COLUMNS = ("text", "note", "clinical_note", "clinical note", "note_text")


def read_notes_csv(file_bytes: bytes) -> pd.DataFrame:
    """Read uploaded CSV content and validate required note columns."""
    dataframe = pd.read_csv(BytesIO(file_bytes))
    note_id_column = _find_column(dataframe, NOTE_ID_COLUMNS)
    note_text_column = _find_column(dataframe, NOTE_TEXT_COLUMNS)

    if note_id_column is None:
        raise ValueError("CSV must include a note_id column.")
    if note_text_column is None:
        raise ValueError("CSV must include a clinical note text column.")

    return dataframe.rename(columns={note_id_column: "note_id", note_text_column: "text"})


def annotations_to_csv(annotations: list[AnnotationResult]) -> str:
    """Convert reviewed annotations to CSV text."""
    rows = []
    for annotation in annotations:
        row = _model_to_dict(annotation)
        row["reviewers_opinion"] = row.pop("reviewer_status", None)
        rows.append(row)
    output = StringIO()
    pd.DataFrame(rows).to_csv(output, index=False)
    return output.getvalue()


def save_annotations_csv(annotations: list[AnnotationResult], output_path: Path) -> Path:
    """Persist reviewed annotations to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(annotations_to_csv(annotations), encoding="utf-8")
    return output_path


def _find_column(dataframe: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    normalized_columns = {column.strip().lower(): column for column in dataframe.columns}
    for candidate in candidates:
        if candidate in normalized_columns:
            return normalized_columns[candidate]
    return None


def _model_to_dict(annotation: AnnotationResult) -> dict:
    if hasattr(annotation, "model_dump"):
        return annotation.model_dump()
    return annotation.dict()
