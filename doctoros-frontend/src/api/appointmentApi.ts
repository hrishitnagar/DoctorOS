import apiClient from './client';
import type { Appointment, AppointmentCreate, UpdatableStatus } from '@/types';

export const appointmentApi = {
  create: async (body: AppointmentCreate): Promise<Appointment> => (await apiClient.post<Appointment>('/appointments/', body)).data,
  updateStatus: async (id: number, status: UpdatableStatus): Promise<Appointment> =>
    (await apiClient.patch<Appointment>(`/appointments/${id}/status`, { status })).data,
};
