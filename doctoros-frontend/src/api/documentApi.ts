import apiClient from './client';
import type { DocumentUploadResponse, OcrResult } from '@/types';

export const documentApi = {
  /** multipart/form-data, field name must be "file" */
  upload: async (patientId: number, file: File, onProgress?: (pct: number) => void): Promise<DocumentUploadResponse> => {
    const form = new FormData();
    form.append('file', file);
    const { data } = await apiClient.post<DocumentUploadResponse>(`/documents/upload/${patientId}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
      },
    });
    return data;
  },
  processOcr: async (documentId: number): Promise<OcrResult> =>
    (await apiClient.post<OcrResult>(`/documents/${documentId}/process-ocr`)).data,
};
