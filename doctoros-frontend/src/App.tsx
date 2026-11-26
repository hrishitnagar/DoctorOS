import { lazy, Suspense } from 'react';
import { Navigate, Outlet, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import { Spinner } from './components/ui/ui';
import { useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const PatientListPage = lazy(() => import('./pages/PatientListPage'));
const PatientProfilePage = lazy(() => import('./pages/PatientProfilePage'));
const VisitCreatePage = lazy(() => import('./pages/VisitCreatePage'));
const ReviewDashboardPage = lazy(() => import('./pages/ReviewDashboardPage'));

function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div className="flex min-h-screen items-center justify-center"><Spinner label="Checking session…" /></div>;
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center"><Spinner label="Loading…" /></div>}>
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/patients" element={<PatientListPage />} />
          <Route path="/patients/:id" element={<PatientProfilePage />} />
          <Route path="/patients/:id/visits/new" element={<VisitCreatePage />} />
          <Route path="/reviews" element={<ReviewDashboardPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
    </Suspense>
  );
}
