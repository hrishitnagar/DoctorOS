import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { authApi } from '@/api/authApi';
import { tokenStore } from '@/api/client';
import type { DashboardInfo } from '@/types';

interface AuthState {
  user: DashboardInfo | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}
export const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<DashboardInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(!!tokenStore.get());

  // On load: validate any stored token.
  useEffect(() => {
    if (!tokenStore.get()) return;
    authApi.me().then(setUser).catch(() => tokenStore.clear()).finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await authApi.login(email, password);
    tokenStore.set(access_token);
    setUser(await authApi.me());
  }, []);

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
    window.location.href = '/login';
  }, []);

  const value = useMemo(() => ({ user, loading, isAuthenticated: !!user, login, logout }), [user, loading, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
