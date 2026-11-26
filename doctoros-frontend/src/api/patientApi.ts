import apiClient from './client';
import type { Patient, PatientCreate, PatientListResponse } from '@/types';

export const patientApi = {
  list: async (params: { search?: string; skip?: number; limit?: number }): Promise<PatientListResponse> =>
    (await apiClient.get<PatientListResponse>('/patients/', { params: { ...params, search: params.search || undefined } })).data,
  create: async (body: PatientCreate): Promise<Patient> => (await apiClient.post<Patient>('/patients/', body)).data,
  get: async (id: number): Promise<Patient> => (await apiClient.get<Patient>(`/patients/${id}`)).data,
};
