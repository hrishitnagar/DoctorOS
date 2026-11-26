import apiClient from './client';
import type { TimelineResponse } from '@/types';

export const timelineApi = {
  get: async (patientId: number): Promise<TimelineResponse> =>
    (await apiClient.get<TimelineResponse>(`/patients/${patientId}/timeline`)).data,
};
