import apiClient from './client';
import type { PatientSummary } from '@/types';

export const summaryApi = {
  get: async (patientId: number): Promise<PatientSummary> =>
    (await apiClient.get<PatientSummary>(`/patients/${patientId}/summary`)).data,
  generate: async (patientId: number, forceRegenerate: boolean): Promise<PatientSummary> =>
    (await apiClient.post<PatientSummary>(`/patients/${patientId}/summary`, { force_regenerate: forceRegenerate })).data,
};
