import SaveAltIcon from "@mui/icons-material/SaveAlt";
import { Button } from "@mui/material";

import { saveAnnotations } from "../api/annotations";
import type { AnnotationResult } from "../types/annotation";
import { annotationsToCsv, downloadBlob } from "../utils/download";


type ExportButtonProps = {
  rows: AnnotationResult[];
  disabled?: boolean;
  onError: (message: string) => void;
  onSaved: (message: string) => void;
};


export default function ExportButton({ rows, disabled = false, onError, onSaved }: ExportButtonProps) {
  async function handleExport() {
    try {
      await saveAnnotations(rows);
      downloadBlob(annotationsToCsv(rows), "srf_annotations.csv");
      onSaved("Annotations saved and exported.");
    } catch (error) {
      onError(error instanceof Error ? error.message : "Failed to export annotations.");
    }
  }

  return (
    <Button
      variant="outlined"
      startIcon={<SaveAltIcon />}
      disabled={disabled || rows.length === 0}
      onClick={handleExport}
    >
      Export CSV
    </Button>
  );
}
