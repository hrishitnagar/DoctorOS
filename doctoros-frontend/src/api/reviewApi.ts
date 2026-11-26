import apiClient from './client';
import type { EntityPatch, LabPatch, PendingReview } from '@/types';

type Decision = 'approved' | 'rejected';

export const reviewApi = {
  pending: async (documentId: number): Promise<PendingReview> =>
    (await apiClient.get<PendingReview>(`/review/pending/${documentId}`)).data,
  editEntity: async (id: number, body: EntityPatch): Promise<void> => {
    await apiClient.patch(`/review/entities/${id}`, body);
  },
  editLab: async (id: number, body: LabPatch): Promise<void> => {
    await apiClient.patch(`/review/lab-results/${id}`, body);
  },
  decideEntity: async (id: number, decision: Decision): Promise<void> => {
    await apiClient.post(`/review/entities/${id}/decision`, { decision });
  },
  decideLab: async (id: number, decision: Decision): Promise<void> => {
    await apiClient.post(`/review/lab-results/${id}/decision`, { decision });
  },
};
