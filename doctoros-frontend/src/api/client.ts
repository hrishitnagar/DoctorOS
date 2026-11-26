import axios, { AxiosError } from 'axios';
import { NO_APPOINTMENT_MSG, SESSION_EXPIRED_KEY, TOKEN_KEY } from '@/utils/constants';

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const tokenStore = {
  get: (): string | null => localStorage.getItem(TOKEN_KEY),
  set: (t: string): void => localStorage.setItem(TOKEN_KEY, t),
  clear: (): void => localStorage.removeItem(TOKEN_KEY),
};

const apiClient = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' } });

apiClient.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (r) => r,
  (error: AxiosError) => {
    // No refresh tokens exist: on 401 the user must sign in again.
    if (error.response?.status === 401 && !window.location.pathname.startsWith('/login')) {
      tokenStore.clear();
      sessionStorage.setItem(SESSION_EXPIRED_KEY, '1');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default apiClient;

interface ValidationItem { loc: (string | number)[]; msg: string }

export function getStatus(err: unknown): number | undefined {
  return axios.isAxiosError(err) ? err.response?.status : undefined;
}

/** Turns any thrown error into a readable message. */
export function getErrorMessage(err: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (!axios.isAxiosError(err)) return err instanceof Error ? err.message : fallback;
  if (!err.response) return 'Unable to connect to server';
  const { status, data } = err.response as { status: number; data?: { detail?: string | ValidationItem[] } };
  const detail = data?.detail;
  if (status === 403) return typeof detail === 'string' && detail.toLowerCase().includes('inactive') ? detail : NO_APPOINTMENT_MSG;
  if (status === 422 && Array.isArray(detail)) {
    return detail.map((d) => `${d.loc.filter((p) => p !== 'body').join('.')}: ${d.msg}`).join('; ');
  }
  if (typeof detail === 'string') return detail;
  if (status === 404) return 'Patient/resource not found';
  if (status >= 500) return 'The server had a problem. Please retry shortly.';
  return fallback;
}
