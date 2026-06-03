import { Alert, Box, CircularProgress, Container, Stack, Typography } from "@mui/material";
import { useState } from "react";

import { uploadNotesCsv } from "../api/annotations";
import AnnotationTable from "../components/AnnotationTable";
import ExportButton from "../components/ExportButton";
import FileUpload from "../components/FileUpload";
import type { AnnotationResult } from "../types/annotation";


export default function AnnotationPage() {
  const [rows, setRows] = useState<AnnotationResult[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function handleUpload(file: File) {
    setIsAnalyzing(true);
    setError(null);
    setMessage(null);
    setFileName(file.name);

    try {
      const results = await uploadNotesCsv(file);
      setRows(results);
      setMessage(`Analyzed ${results.length} notes.`);
    } catch (uploadError) {
      setRows([]);
      setError(uploadError instanceof Error ? uploadError.message : "Failed to analyze CSV.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Stack spacing={3}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={2}
          justifyContent="space-between"
          alignItems={{ xs: "stretch", sm: "center" }}
        >
          <Typography variant="h4" component="h1">
            SRF LLM Annotator
          </Typography>
          <ExportButton
            rows={rows}
            disabled={isAnalyzing}
            onError={setError}
            onSaved={setMessage}
          />
        </Stack>
        <FileUpload onUpload={handleUpload} disabled={isAnalyzing} fileName={fileName} />
        {isAnalyzing ? (
          <Box display="flex" gap={1.5} alignItems="center">
            <CircularProgress size={22} />
            <Typography variant="body2" color="text.secondary">
              Analyzing notes with GPT-4o...
            </Typography>
          </Box>
        ) : null}
        {error ? <Alert severity="error">{error}</Alert> : null}
        {message ? <Alert severity="success">{message}</Alert> : null}
        <AnnotationTable rows={rows} onRowsChange={setRows} />
      </Stack>
    </Container>
  );
}
