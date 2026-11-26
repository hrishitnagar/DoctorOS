import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { CalendarPlus, Pencil, Stethoscope } from 'lucide-react';
import { patientApi } from '@/api/patientApi';
import { timelineApi } from '@/api/timelineApi';
import { Badge, Button, ErrorState, Skeleton } from '@/components/ui/ui';
import { Tilt } from '@/components/ui/Tilt';
import { IMG } from '@/utils/assets';
import { useApi } from '@/hooks/useApi';
import { calcAge } from '@/utils/formatDate';
import { AppointmentModal } from './profile/AppointmentModal';
import AssistantTab from './profile/AssistantTab';
import { LabsTab, MedicationsTab, OverviewTab, TimelineTab, UnavailableTab, VisitsTab } from './profile/ClinicalTabs';
import DocumentsTab from './profile/DocumentsTab';
import SummaryTab from './profile/SummaryTab';

const tabs = [
  ['overview', 'Overview'], ['history', 'Medical History'], ['visits', 'Visits'], ['meds', 'Medications'], ['allergies', 'Allergies'],
  ['labs', 'Lab Results'], ['docs', 'Documents'], ['timeline', 'Timeline'], ['ai', '✨ AI Assistant'], ['summary', '✨ Clinical Summary'],
] as const;
type TabId = (typeof tabs)[number][0];

export default function PatientProfilePage() {
  const id = Number(useParams().id);
  const [tab, setTab] = useState<TabId>('overview');
  const [apptOpen, setApptOpen] = useState(false);
  const patient = useApi(() => patientApi.get(id), [id]);
  const timeline = useApi(() => timelineApi.get(id), [id]);

  if (patient.loading) return <div className="space-y-4"><Skeleton className="h-32" /><Skeleton className="h-64" /></div>;
  if (patient.error || !patient.data) return <ErrorState message={patient.error ?? 'Patient/resource not found'} onRetry={patient.reload} />;
  const p = patient.data;
  const records = timeline.data?.timeline ?? [];

  const body = () => {
    switch (tab) {
      case 'overview': return <OverviewTab patient={p} onNewAppointment={() => setApptOpen(true)} />;
      case 'history': return <UnavailableTab title="Medical History" reason="Conditions will appear here once a medical-history endpoint exists." />;
      case 'allergies': return <UnavailableTab title="Allergies" reason="Allergy records will appear here once an allergy endpoint exists." />;
      case 'ai': return <AssistantTab key={id} patientId={id} patientName={p.name} />;
      case 'summary': return <SummaryTab key={id} patientId={id} />;
      default:
        if (timeline.loading) return <Skeleton className="h-48" />;
        if (timeline.error) return <ErrorState message={timeline.error} onRetry={timeline.reload} />;
        if (tab === 'visits') return <VisitsTab timeline={records} patientId={id} />;
        if (tab === 'meds') return <MedicationsTab timeline={records} />;
        if (tab === 'labs') return <LabsTab timeline={records} />;
        if (tab === 'docs') return <DocumentsTab patientId={id} timeline={records} onRefresh={timeline.reload} />;
        return <TimelineTab timeline={records} />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="relative overflow-hidden rounded-3xl bg-ink-900 text-paper-50 shadow-deep">
        <img src={IMG.collage} alt="" aria-hidden decoding="async" className="absolute inset-0 h-full w-full object-cover object-center opacity-[.22] sepia" />
        <div className="absolute inset-0 bg-gradient-to-r from-ink-900 via-ink-900/85 to-ink-900/40" />
        <div className="relative flex flex-wrap items-center justify-between gap-4 p-4 sm:p-6">
          <div className="flex min-w-0 items-center gap-4">
            <Tilt max={16}>
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-ai-200 via-ai-500 to-ai-700 font-display text-3xl font-bold text-ink-900 shadow-deep ring-2 ring-ai-200/60">{p.name.charAt(0)}</div>
            </Tilt>
            <div className="min-w-0">
              <h1 className="truncate text-2xl font-bold sm:text-3xl">{p.name}</h1>
              <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-paper-200">
                <span className="rounded-md bg-white/15 px-2 py-0.5 font-mono text-xs">{p.patient_uid}</span>
                {p.gender ?? '—'} · {calcAge(p.dob)} {p.blood_group && <Badge tone="red">{p.blood_group}</Badge>}
              </p>
              <p className="truncate text-xs text-paper-200/80">{[p.phone, p.email].filter(Boolean).join(' · ') || 'No contact info'}</p>
            </div>
          </div>
          <div className="flex w-full flex-wrap gap-2 sm:w-auto">
            <Button variant="secondary" onClick={() => setApptOpen(true)}><CalendarPlus className="h-4 w-4" />New Appointment</Button>
            <Link to={`/patients/${id}/visits/new`}><Button variant="secondary"><Stethoscope className="h-4 w-4" />Record Visit</Button></Link>
            <Button variant="ghost" disabled title="Coming Soon — backend has no patient update endpoint" className="!text-paper-200/70"><Pencil className="h-4 w-4" />Edit (Coming Soon)</Button>
          </div>
        </div>
      </div>

      <div role="tablist" aria-label="Patient sections" className="scroll-thin flex gap-1 overflow-x-auto border-b border-slate-300">
        {tabs.map(([key, label]) => (
          <button key={key} role="tab" aria-selected={tab === key} onClick={() => setTab(key)}
            className={`whitespace-nowrap border-b-2 px-4 py-3 font-label text-[11px] font-bold uppercase tracking-[0.12em] transition ${tab === key ? 'border-ai-600 text-ink-900' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>{label}</button>
        ))}
      </div>
      <div role="tabpanel" className="animate-fadeUp">{body()}</div>

      <AppointmentModal open={apptOpen} onClose={() => setApptOpen(false)} patientId={id} onCreated={timeline.reload} />
    </div>
  );
}
