import apiClient from './client';
import type { RagAnswer } from '@/types';

export const ragApi = {
  ask: async (patientId: number, question: string): Promise<RagAnswer> =>
    (await apiClient.post<RagAnswer>(`/patients/${patientId}/ask`, { question })).data,
};
