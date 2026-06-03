export type ReviewerStatus = "correct" | "false" | null;

export type AnnotationResult = {
  note_id: string;
  srf_present: boolean;
  srf_type: string | null;
  supporting_phrase: string | null;
  reviewer_status: ReviewerStatus;
};
