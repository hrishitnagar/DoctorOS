import apiClient from './client';
import type { Visit, VisitCreate } from '@/types';

export const visitApi = {
  create: async (body: VisitCreate): Promise<Visit> => (await apiClient.post<Visit>('/visits/', body)).data,
};
