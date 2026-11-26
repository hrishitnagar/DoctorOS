// Types mirror the backend schemas from FRONTEND_API_CONTRACT.md

export interface DashboardInfo { message: string; doctor_id: number; doctor_name: string; role: string }
export interface LoginResponse { access_token: string; token_type: string }
export interface HealthInfo { status: string; application: string; message: string }

export interface Patient {
  id: number; patient_uid: string; name: string; dob: string | null; gender: string | null;
  phone: string | null; email: string | null; address: string | null;
  blood_group: string | null; emergency_contact: string | null;
}
export interface PatientCreate {
  name: string; dob?: string | null; gender?: string | null; phone?: string | null; email?: string | null;
  address?: string | null; blood_group?: string | null; emergency_contact?: string | null;
}
export interface PatientListResponse { items: Patient[]; total: number; skip: number; limit: number }

export type AppointmentStatus = 'scheduled' | 'completed' | 'cancelled' | 'no-show';
export type UpdatableStatus = 'completed' | 'cancelled' | 'no-show';
export interface AppointmentCreate { patient_id: number; appointment_datetime: string; duration_minutes: 15 | 30 | 60; reason?: string | null }
export interface Appointment {
  id: number; patient_id: number; doctor_id: number; appointment_datetime: string;
  duration_minutes: number; status: AppointmentStatus; reason: string | null;
}

export interface MedicationCreate { drug: string; dose?: string | null; frequency?: string | null; duration?: string | null; instructions?: string | null }
export interface Medication extends MedicationCreate { id: number }
export interface VisitCreate {
  patient_id: number; appointment_id?: number | null; observations?: string | null; diagnosis?: string | null;
  prescription_notes?: string | null; visit_date: string; medications: MedicationCreate[];
}
export interface Visit {
  id: number; appointment_id: number | null; patient_id: number; doctor_id: number; observations: string | null;
  diagnosis: string | null; prescription_notes: string | null; visit_date: string; medications: Medication[];
}

export interface DocumentUploadResponse { id: number; patient_id: number; document_type: string; ocr_status: string; uploaded_at: string }
export interface OcrResult {
  message: string; document_id: number; ocr_status: string; extraction_status: string; success: boolean;
  entities_saved: number; lab_results_saved: number;
}

export interface TimelineVisit {
  type: 'visit'; id: number; date: string; appointment_id: number | null; doctor_id: number;
  observations: string | null; diagnosis: string | null; prescription_notes: string | null; medications: Medication[];
}
export interface TimelineDocument { type: 'document'; id: number; date: string; document_type: string; ocr_status: string }
export interface TimelineLab {
  type: 'lab_result'; id: number; date: string | null; document_id: number | null; test_name: string;
  value: number; unit: string | null; ref_range: string | null;
}
export type TimelineRecord = TimelineVisit | TimelineDocument | TimelineLab;
export interface TimelineResponse {
  patient_id: number; patient_uid: string; patient_name: string; total_records: number; timeline: TimelineRecord[];
}

export interface PendingEntity { id: number; entity_type: string; value: string; unit: string | null; confidence: number | null; review_status: string }
export interface PendingLab {
  id: number; test_name: string; value: number; unit: string | null; ref_range: string | null;
  test_date: string | null; confidence: number | null; review_status: string;
}
export interface PendingReview { document_id: number; patient_id: number; entities: PendingEntity[]; lab_results: PendingLab[]; total_pending: number }
export interface EntityPatch { value?: string | null; unit?: string | null }
export interface LabPatch { test_name?: string | null; value?: number | null; unit?: string | null; ref_range?: string | null; test_date?: string | null }

export interface RagCitation {
  source_id: string; chunk_id: number; document_id: number; patient_id: number;
  chunk_index: number; page_no: number | null; document_date: string | null;
}
export interface RagAnswer { answer: string; citations: RagCitation[]; retrieved_chunks: number }

export interface Conversation { id: number; patient_id: number; doctor_id: number; title: string; created_at: string; updated_at: string }
export interface ChatMessage { id: number; role: 'user' | 'assistant'; content: string; citations: RagCitation[] | null; created_at: string }
export interface ChatResponse { conversation: Conversation; user_message: ChatMessage; assistant_message: ChatMessage }
export interface ConversationList { conversations: Conversation[]; total: number }
export interface ConversationDetail extends Conversation { messages: ChatMessage[] }

export interface SummaryCitation { record_type: string; record_id: number; date: string | null; document_id: number | null }
export interface PatientSummary {
  id: number; patient_id: number; doctor_id: number; summary: string; citations: SummaryCitation[] | null; generated_at: string;
}
