import { Link, useNavigate } from 'react-router-dom';
import { Activity, ClipboardCheck, ShieldCheck, Upload, UserPlus, Users } from 'lucide-react';
import { authApi } from '@/api/authApi';
import { patientApi } from '@/api/patientApi';
import { Button, Card, EmptyState, ErrorState, Skeleton } from '@/components/ui/ui';
import { Caduceus } from '@/components/ui/Brand';
import { PrintRing } from '@/components/ui/PrintRing';
import { Tilt } from '@/components/ui/Tilt';
import { useApi } from '@/hooks/useApi';
import { useAuth } from '@/hooks/useAuth';
import { IMG } from '@/utils/assets';
import { formatDate } from '@/utils/formatDate';

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const patients = useApi(() => patientApi.list({ limit: 10 }), []);
  const health = useApi(() => authApi.health(), []);

  const stats = [
    { label: 'Total patients', value: patients.loading ? '…' : String(patients.data?.total ?? 0), icon: Users, art: IMG.heart, tint: 'from-brand-600 to-brand-800' },
    { label: 'Backend status', value: health.loading ? '…' : health.error ? 'Offline' : 'Healthy', icon: Activity, art: IMG.lungs, tint: 'from-azure-500 to-azure-700' },
    { label: 'Signed in as', value: user?.role ?? '—', icon: ShieldCheck, art: IMG.brain, tint: 'from-ai-500 to-ai-700' },
  ];

  return (
    <div className="space-y-6">
      {/* hero */}
      <div className="relative overflow-hidden rounded-3xl bg-ink-900 text-paper-50 shadow-deep">
        <img src={IMG.hero} alt="" aria-hidden decoding="async" className="absolute inset-0 h-full w-full object-cover object-[20%_40%] opacity-[.28] sepia" />
        <div className="absolute inset-0 bg-gradient-to-r from-ink-900 via-ink-900/80 to-ink-900/20" />
        <div className="relative grid items-center gap-4 p-5 sm:p-8 md:grid-cols-[1.3fr_1fr]">
          <div>
            <div className="mb-3 flex items-center gap-2 text-ai-200"><Caduceus style={{ height: 22 }} /><span className="font-label text-[11px] font-bold uppercase tracking-[0.3em]">Good to see you</span></div>
            <h1 className="text-3xl font-bold leading-tight sm:text-5xl">Welcome,<br /><span className="italic text-ai-200">{user?.doctor_name}</span></h1>
            <p className="mt-3 max-w-md text-sm text-paper-200/85">Manage patients, review AI extractions and explore records with cited answers.</p>
          </div>
          <div className="hidden items-center justify-center py-6 sm:flex md:py-4"><PrintRing width={116} /></div>
        </div>
      </div>

      {/* stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        {stats.map(({ label, value, icon: Icon, art, tint }) => (
          <Tilt key={label} className="animate-fadeUp overflow-hidden rounded-2xl shadow-soft">
            <div className={`relative bg-gradient-to-br ${tint} p-5 text-white`}>
              <img src={art} alt="" aria-hidden loading="lazy" decoding="async" className="absolute -right-4 -top-2 h-[130%] w-1/2 object-cover opacity-25 mix-blend-multiply sepia-print" />
              <Icon className="relative mb-3 h-6 w-6 opacity-90" aria-hidden />
              <p className="relative font-label text-[11px] font-bold uppercase tracking-[0.18em] opacity-90">{label}</p>
              <p className="relative font-display text-4xl font-bold capitalize">{value}</p>
            </div>
          </Tilt>
        ))}
      </div>

      {/* quick actions */}
      <Card>
        <h2 className="mb-3 text-xl font-bold text-slate-900">Quick actions</h2>
        <div className="grid gap-3 sm:flex sm:flex-wrap">
          <Button onClick={() => navigate('/patients?create=1')}><UserPlus className="h-4 w-4" />Create Patient</Button>
          <Button variant="ai" onClick={() => navigate('/patients')}><Upload className="h-4 w-4" />Upload Document</Button>
          <Button variant="secondary" onClick={() => navigate('/reviews')}><ClipboardCheck className="h-4 w-4" />Review Pending</Button>
        </div>
      </Card>

      {/* recent patients */}
      <Card>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">Recent patients</h2>
          <Link to="/patients" className="text-sm font-bold text-brand-700 hover:underline">View all</Link>
        </div>
        {patients.loading ? <div className="space-y-2"><Skeleton className="h-12" /><Skeleton className="h-12" /><Skeleton className="h-12" /></div>
          : patients.error ? <ErrorState message={patients.error} onRetry={patients.reload} />
          : patients.data && patients.data.items.length > 0 ? (
            <ul className="divide-y divide-slate-200">
              {patients.data.items.map((p) => (
                <li key={p.id}>
                  <Link to={`/patients/${p.id}`} className="flex items-center justify-between gap-3 rounded-xl px-2 py-3 transition hover:bg-paper-100">
                    <span className="flex min-w-0 items-center gap-3">
                      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-ink-600 to-ink-900 font-display font-bold text-ai-200 ring-2 ring-ai-500/50">{p.name.charAt(0)}</span>
                      <span className="min-w-0"><span className="block truncate text-sm font-bold text-slate-900">{p.name}</span><span className="block font-mono text-xs text-slate-500">{p.patient_uid}</span></span>
                    </span>
                    <span className="shrink-0 text-xs text-slate-500">{formatDate(p.dob)}</span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : <EmptyState icon={<Users className="h-5 w-5" />} text="No patients yet. Create your first patient to get started."
            action={<Button onClick={() => navigate('/patients?create=1')}>Create Patient</Button>} />}
      </Card>
    </div>
  );
}
