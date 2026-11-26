import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { CalendarClock, ChevronDown, FileText, FlaskConical, HeartPulse, Pill, Plus, Stethoscope, Wrench } from 'lucide-react';
import { appointmentApi } from '@/api/appointmentApi';
import toast from 'react-hot-toast';
import { getErrorMessage } from '@/api/client';
import { Badge, Button, Card, EmptyState, Input, Select, StatusBadge } from '@/components/ui/ui';
import { LabValue } from '@/components/medical/medical';
import type { Appointment, Patient, TimelineDocument, TimelineLab, TimelineRecord, TimelineVisit, UpdatableStatus } from '@/types';
import { calcAge, formatDate, formatDateTime } from '@/utils/formatDate';
import { showValue } from '@/utils/formatMedical';
import { StatusUpdater } from './AppointmentModal';

const Row = ({ k, v, mono }: { k: string; v: string | null; mono?: boolean }) => (
  <div className="rounded-xl bg-slate-50 p-3"><dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">{k}</dt><dd className={`mt-1 text-sm text-slate-900 ${mono ? 'font-mono' : ''}`}>{v || '—'}</dd></div>
);

export function OverviewTab({ patient, onNewAppointment }: { patient: Patient; onNewAppointment: () => void }) {
  const [apptId, setApptId] = useState('');
  const [status, setStatus] = useState<UpdatableStatus>('completed');
  const [appt, setAppt] = useState<Appointment | null>(null);
  const [busy, setBusy] = useState(false);
  const run = async () => {
    const id = Number(apptId);
    if (!id) return toast.error('Enter an appointment ID');
    setBusy(true);
    try { setAppt(await appointmentApi.updateStatus(id, status)); toast.success('Status updated'); }
    catch (e) { toast.error(getErrorMessage(e)); } finally { setBusy(false); }
  };
  return (
    <div className="space-y-6">
      <Card>
        <h3 className="mb-4 font-bold text-slate-900">Demographics</h3>
        <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Row k="Patient ID" v={patient.patient_uid} mono /><Row k="Date of birth" v={`${formatDate(patient.dob)} (${calcAge(patient.dob)})`} />
          <Row k="Gender" v={patient.gender} /><Row k="Blood group" v={patient.blood_group} mono /><Row k="Phone" v={patient.phone} mono /><Row k="Email" v={patient.email} />
          <div className="sm:col-span-2 lg:col-span-3"><Row k="Address" v={patient.address} /></div>
          <div className="sm:col-span-2 lg:col-span-3"><Row k="Emergency contact" v={patient.emergency_contact} /></div>
        </dl>
      </Card>
      <Card>
        <h3 className="mb-1 flex items-center gap-2 font-bold text-slate-900"><CalendarClock className="h-5 w-5 text-brand-600" />Appointments</h3>
        <p className="mb-4 text-sm text-slate-500">AI features unlock once you have a scheduled or completed appointment with this patient. The backend has no appointment list, so use the ID shown when you create one.</p>
        <Button onClick={onNewAppointment}><Plus className="h-4 w-4" />New Appointment</Button>
        <div className="mt-5 flex flex-wrap items-end gap-3 border-t border-slate-100 pt-4">
          <div className="w-40"><Input label="Appointment ID" type="number" min={1} value={apptId} onChange={(e) => setApptId(e.target.value)} /></div>
          <div className="w-44"><Select label="New status" value={status} onChange={(e) => setStatus(e.target.value as UpdatableStatus)}><option value="completed">completed</option><option value="cancelled">cancelled</option><option value="no-show">no-show</option></Select></div>
          <Button variant="secondary" loading={busy} onClick={run}>Update status</Button>
        </div>
        {appt && <div className="mt-4"><StatusUpdater appointment={appt} onChanged={setAppt} /></div>}
      </Card>
    </div>
  );
}

const visits = (t: TimelineRecord[]) => t.filter((r): r is TimelineVisit => r.type === 'visit');

export function VisitsTab({ timeline, patientId }: { timeline: TimelineRecord[]; patientId: number }) {
  const list = visits(timeline);
  const [open, setOpen] = useState<number | null>(null);
  return (
    <div className="space-y-3">
      <div className="flex justify-end"><Link to={`/patients/${patientId}/visits/new`}><Button><Plus className="h-4 w-4" />Record Visit</Button></Link></div>
      {list.length === 0 ? <EmptyState icon={<Stethoscope className="h-7 w-7" />} text="No visits recorded yet." action={<Link to={`/patients/${patientId}/visits/new`}><Button>Record Visit</Button></Link>} /> :
        list.map((v) => (
          <Card key={v.id}>
            <button className="flex w-full items-center justify-between text-left" aria-expanded={open === v.id} onClick={() => setOpen(open === v.id ? null : v.id)}>
              <span><span className="block font-bold text-slate-900">{v.diagnosis ?? 'Visit'}</span><span className="text-xs text-slate-500">{formatDateTime(v.date)}</span></span>
              <ChevronDown className={`h-5 w-5 transition ${open === v.id ? 'rotate-180' : ''}`} aria-hidden />
            </button>
            {open === v.id && (
              <div className="mt-4 space-y-3 text-sm">
                <Row k="Observations" v={v.observations} /><Row k="Prescription notes" v={v.prescription_notes} />
                {v.medications.length > 0 && <p className="text-xs text-slate-500">{v.medications.length} medication(s) — see Medications tab</p>}
              </div>
            )}
          </Card>
        ))}
    </div>
  );
}

export function MedicationsTab({ timeline }: { timeline: TimelineRecord[] }) {
  const rows = useMemo(() => visits(timeline).flatMap((v) => v.medications.map((m) => ({ ...m, date: v.date }))), [timeline]);
  if (rows.length === 0) return <EmptyState icon={<Pill className="h-7 w-7" />} text="No medications recorded. Medications appear here when saved with a visit." />;
  return (
    <Card className="overflow-x-auto p-0">
      <table className="w-full text-left text-sm">
        <thead><tr className="bg-slate-50 font-label text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500">{['Drug', 'Dose', 'Frequency', 'Duration', 'Instructions', 'Prescribed'].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr></thead>
        <tbody>{rows.map((m, i) => (
          <tr key={`${m.id}-${i}`} className={i % 2 ? 'bg-slate-50/60' : ''}>
            <td className="px-4 py-3 font-semibold">{m.drug}</td><td className="px-4 py-3 font-mono">{showValue(m.dose)}</td>
            <td className="px-4 py-3">{showValue(m.frequency)}</td><td className="px-4 py-3">{showValue(m.duration)}</td>
            <td className="px-4 py-3">{showValue(m.instructions)}</td><td className="px-4 py-3 text-xs">{formatDate(m.date)}</td>
          </tr>))}</tbody>
      </table>
    </Card>
  );
}

export function LabsTab({ timeline }: { timeline: TimelineRecord[] }) {
  const labs = timeline.filter((r): r is TimelineLab => r.type === 'lab_result');
  if (labs.length === 0) return <EmptyState icon={<FlaskConical className="h-7 w-7" />} text="No lab results yet. Upload and process a lab report to see values here." />;
  return (
    <Card className="overflow-x-auto p-0">
      <table className="w-full text-left text-sm">
        <thead><tr className="bg-slate-50 font-label text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500">{['Test', 'Result', 'Reference range', 'Date'].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr></thead>
        <tbody>{labs.map((l, i) => (
          <tr key={l.id} className={i % 2 ? 'bg-slate-50/60' : ''}>
            <td className="px-4 py-3 font-semibold">{l.test_name}</td>
            <td className="px-4 py-3"><LabValue value={l.value} unit={l.unit} range={l.ref_range} /></td>
            <td className="px-4 py-3 font-mono text-slate-600">{showValue(l.ref_range)}</td><td className="px-4 py-3 text-xs">{formatDate(l.date)}</td>
          </tr>))}</tbody>
      </table>
    </Card>
  );
}

const meta = {
  visit: { icon: Stethoscope, dot: 'bg-azure-500', tone: 'blue' as const, label: 'Visit' },
  document: { icon: FileText, dot: 'bg-ai-500', tone: 'purple' as const, label: 'Document' },
  lab_result: { icon: FlaskConical, dot: 'bg-moss-500', tone: 'green' as const, label: 'Lab result' },
};

export function TimelineTab({ timeline }: { timeline: TimelineRecord[] }) {
  const [filter, setFilter] = useState<'all' | TimelineRecord['type']>('all');
  const [open, setOpen] = useState<string | null>(null);
  const shown = timeline.filter((r) => filter === 'all' || r.type === filter);
  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2" role="group" aria-label="Filter timeline">
        {(['all', 'visit', 'document', 'lab_result'] as const).map((f) => (
          <button key={f} onClick={() => setFilter(f)} aria-pressed={filter === f}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold ${filter === f ? 'bg-brand-600 text-white' : 'bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50'}`}>{f === 'all' ? 'All' : meta[f].label}</button>
        ))}
      </div>
      {shown.length === 0 ? <EmptyState icon={<HeartPulse className="h-7 w-7" />} text="Nothing on the timeline yet." /> : (
        <ol className="relative ml-3 space-y-4 border-l-2 border-gradient border-slate-200 pl-6">
          {shown.map((r) => {
            const m = meta[r.type]; const Icon = m.icon; const key = `${r.type}-${r.id}`;
            return (
              <li key={key} className="relative">
                <span className={`absolute -left-[37px] flex h-7 w-7 items-center justify-center rounded-full text-white ring-4 ring-white ${m.dot}`}><Icon className="h-3.5 w-3.5" aria-hidden /></span>
                <Card className="p-4">
                  <button className="flex w-full items-center justify-between gap-2 text-left" aria-expanded={open === key} onClick={() => setOpen(open === key ? null : key)}>
                    <span><Badge tone={m.tone}>{m.label}</Badge>
                      <span className="ml-2 text-sm font-semibold text-slate-900">
                        {r.type === 'visit' ? r.diagnosis ?? 'Visit' : r.type === 'document' ? `${r.document_type} document` : r.test_name}
                      </span>
                      <span className="mt-1 block text-xs text-slate-500">{r.type === 'lab_result' ? formatDate(r.date) : formatDateTime(r.date)}</span></span>
                    <ChevronDown className={`h-4 w-4 shrink-0 transition ${open === key ? 'rotate-180' : ''}`} aria-hidden />
                  </button>
                  {open === key && <TimelineDetail r={r} />}
                </Card>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}

function TimelineDetail({ r }: { r: TimelineRecord }) {
  if (r.type === 'visit') {
    const v: TimelineVisit = r;
    return (<div className="mt-3 space-y-2 text-sm"><Row k="Observations" v={v.observations} /><Row k="Prescription notes" v={v.prescription_notes} />
      {v.medications.map((m) => <p key={m.id} className="font-mono text-xs">💊 {m.drug} · {showValue(m.dose)} · {showValue(m.frequency)} · {showValue(m.duration)}</p>)}</div>);
  }
  if (r.type === 'document') {
    const d: TimelineDocument = r;
    return <div className="mt-3 flex items-center gap-2 text-sm">OCR status: <StatusBadge status={d.ocr_status} /></div>;
  }
  const l: TimelineLab = r;
  return <div className="mt-3 text-sm"><LabValue value={l.value} unit={l.unit} range={l.ref_range} /><p className="mt-1 text-xs text-slate-500">Range {showValue(l.ref_range)}{l.document_id ? ` · from document #${l.document_id}` : ''}</p></div>;
}

export function UnavailableTab({ title, reason }: { title: string; reason: string }) {
  return <EmptyState icon={<Wrench className="h-7 w-7" />} title={`${title} — Coming Soon`} text={`Backend API not yet implemented. ${reason}`} />;
}
