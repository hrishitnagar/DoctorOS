import apiClient from './client';
import type { DashboardInfo, HealthInfo, LoginResponse } from '@/types';

export const authApi = {
  /** FORM DATA (not JSON). Field is "username" and carries the email. */
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);
    const { data } = await apiClient.post<LoginResponse>('/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },
  /** The contract has no /auth/me; GET /doctor/dashboard validates the token and returns the doctor. */
  me: async (): Promise<DashboardInfo> => (await apiClient.get<DashboardInfo>('/doctor/dashboard')).data,
  health: async (): Promise<HealthInfo> => (await apiClient.get<HealthInfo>('/health')).data,
};
