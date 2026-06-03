import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Button, Stack, Typography } from "@mui/material";
import type { ChangeEvent } from "react";


type FileUploadProps = {
  onUpload: (file: File) => void;
  disabled?: boolean;
  fileName?: string | null;
};


export default function FileUpload({ onUpload, disabled = false, fileName }: FileUploadProps) {
  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      onUpload(file);
    }
    event.target.value = "";
  }

  return (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ sm: "center" }}>
      <Button
        component="label"
        variant="contained"
        startIcon={<UploadFileIcon />}
        disabled={disabled}
      >
        Upload CSV
        <input hidden accept=".csv,text/csv" type="file" onChange={handleChange} />
      </Button>
      {fileName ? (
        <Typography variant="body2" color="text.secondary">
          {fileName}
        </Typography>
      ) : null}
    </Stack>
  );
}
