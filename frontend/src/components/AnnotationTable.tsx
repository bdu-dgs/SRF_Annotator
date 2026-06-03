import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridRowModel
} from "@mui/x-data-grid";
import { Chip, Typography } from "@mui/material";

import type { AnnotationResult } from "../types/annotation";


type AnnotationTableProps = {
  rows: AnnotationResult[];
  onRowsChange: (rows: AnnotationResult[]) => void;
};


export default function AnnotationTable({ rows, onRowsChange }: AnnotationTableProps) {
  const columns: GridColDef[] = [
    {
      field: "note_id",
      headerName: "Note ID",
      width: 150
    },
    {
      field: "srf_present",
      headerName: "SRF Present",
      width: 130,
      renderCell: (params: GridRenderCellParams<AnnotationResult, boolean>) => (
        <Chip
          size="small"
          color={params.value ? "warning" : "default"}
          label={params.value ? "Yes" : "No"}
          variant={params.value ? "filled" : "outlined"}
        />
      )
    },
    {
      field: "srf_type",
      headerName: "SRF Type",
      width: 180,
      editable: true
    },
    {
      field: "supporting_phrase",
      headerName: "Supporting Phrase",
      flex: 1,
      minWidth: 360,
      editable: true,
      renderCell: (params: GridRenderCellParams<AnnotationResult, string | null>) => (
        <Typography variant="body2" sx={{ whiteSpace: "normal", lineHeight: 1.45, py: 1 }}>
          {params.value ?? ""}
        </Typography>
      )
    },
    {
      field: "reviewer_status",
      headerName: "Reviewer's Opinion",
      width: 190,
      editable: true,
      type: "singleSelect",
      valueOptions: ["correct", "false"],
      renderCell: (params: GridRenderCellParams<AnnotationResult, string | null>) =>
        params.value ? (
          <Chip
            size="small"
            color={params.value === "correct" ? "success" : "error"}
            label={params.value}
          />
        ) : (
          <Typography variant="body2" color="text.secondary">
            Unreviewed
          </Typography>
        )
    }
  ];

  function handleProcessRowUpdate(updatedRow: GridRowModel) {
    const nextRow = updatedRow as AnnotationResult;
    onRowsChange(rows.map((row) => (row.note_id === nextRow.note_id ? nextRow : row)));
    return nextRow;
  }

  return (
    <DataGrid
      rows={rows}
      columns={columns}
      getRowId={(row) => row.note_id}
      autoHeight
      disableRowSelectionOnClick
      processRowUpdate={handleProcessRowUpdate}
      initialState={{
        pagination: {
          paginationModel: { pageSize: 10, page: 0 }
        }
      }}
      pageSizeOptions={[10, 25, 50]}
      sx={{
        borderColor: "divider",
        bgcolor: "background.paper",
        "& .MuiDataGrid-cell": {
          alignItems: "center"
        },
        "& .MuiDataGrid-columnHeaders": {
          bgcolor: "#eef4f7"
        }
      }}
    />
  );
}
