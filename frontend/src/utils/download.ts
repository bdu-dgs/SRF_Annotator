export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}


export function annotationsToCsv(rows: Array<Record<string, unknown>>): Blob {
  const columns = [
    "note_id",
    "srf_present",
    "srf_type",
    "supporting_phrase",
    "reviewers_opinion"
  ];
  const normalizedRows = rows.map((row) => ({
    ...row,
    reviewers_opinion: row.reviewer_status
  }));
  const csvRows = [
    columns.join(","),
    ...normalizedRows.map((row) => columns.map((column) => csvValue(row[column])).join(","))
  ];

  return new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8" });
}


function csvValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }

  const text = String(value);
  return `"${text.replaceAll('"', '""')}"`;
}
