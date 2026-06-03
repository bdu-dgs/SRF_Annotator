import type { AnnotationResult } from "../types/annotation";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";


export async function uploadNotesCsv(file: File): Promise<AnnotationResult[]> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to analyze CSV."));
  }

  const payload = (await response.json()) as { results: AnnotationResult[] };
  return payload.results;
}


export async function saveAnnotations(rows: AnnotationResult[]): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/save_annotations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ annotations: rows })
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to save annotations."));
  }
}


async function getErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = await response.json();
    return typeof payload.detail === "string" ? payload.detail : fallback;
  } catch {
    return fallback;
  }
}
