import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Check, ClipboardCheck, Pencil, Search, X } from 'lucide-react';
import { getErrorMessage } from '@/api/client';
import { reviewApi } from '@/api/reviewApi';
import { Badge, Button, Card, EmptyState, ErrorState, Input, Modal, PageHeader, SkeletonList } from '@/components/ui/ui';
import { LabValue } from '@/components/medical/medical';
import { useApi } from '@/hooks/useApi';
import { IMG } from '@/utils/assets';
import type { PendingEntity, PendingLab } from '@/types';
import { formatDate } from '@/utils/formatDate';
import { showValue } from '@/utils/formatMedical';

function Confidence({ value }: { value: number | null }) {
  if (value === null) return <span className="text-xs text-slate-400">Confidence n/a</span>;
  const pct = Math.round(value * 100);
  const color = pct >= 85 ? 'bg-moss-500' : pct >= 60 ? 'bg-ai-500' : 'bg-rust-500';
  return (
    <span className="flex items-center gap-2 text-xs text-slate-600" title={`Confidence ${value}`}>
      <span className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200"><span className={`block h-full ${color}`} style={{ width: `${pct}%` }} /></span>
      <span className="font-mono">{pct}%</span>
    </span>
  );
}

type Editing = { kind: 'entity'; item: PendingEntity } | { kind: 'lab'; item: PendingLab } | null;
interface EditForm { value: string; unit: string; test_name: string; ref_range: string; test_date: string }

export default function ReviewDashboardPage() {
  const [params, setParams] = useSearchParams();
  const docId = params.get('doc') ? Number(params.get('doc')) : null;
  const [input, setInput] = useState(params.get('doc') ?? '');
  const [busy, setBusy] = useState<string | null>(null);
  const [editing, setEditing] = useState<Editing>(null);

  const review = useApi(async () => (docId ? reviewApi.pending(docId) : null), [docId]);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<EditForm>();

  const load = () => { const n = Number(input); if (n > 0) setParams({ doc: String(n) }); else toast.error('Enter a valid document ID'); };

  const decide = async (kind: 'entity' | 'lab', id: number, decision: 'approved' | 'rejected') => {
    setBusy(`${kind}-${id}`);
    try {
      await (kind === 'entity' ? reviewApi.decideEntity(id, decision) : reviewApi.decideLab(id, decision));
      toast.success(decision === 'approved' ? 'Approved' : 'Rejected');
      review.reload();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setBusy(null); }
  };

  const openEdit = (e: Editing) => {
    setEditing(e);
    if (!e) return;
    reset(e.kind === 'entity'
      ? { value: e.item.value, unit: e.item.unit ?? '', test_name: '', ref_range: '', test_date: '' }
      : { value: String(e.item.value), unit: e.item.unit ?? '', test_name: e.item.test_name, ref_range: e.item.ref_range ?? '', test_date: e.item.test_date ?? '' });
  };

  const saveCorrection = async (f: EditForm) => {
    if (!editing) return;
    try {
      if (editing.kind === 'entity') {
        await reviewApi.editEntity(editing.item.id, { value: f.value, unit: f.unit || null });
        await reviewApi.decideEntity(editing.item.id, 'approved');
      } else {
        await reviewApi.editLab(editing.item.id, {
          test_name: f.test_name, value: Number(f.value), unit: f.unit || null, ref_range: f.ref_range || null, test_date: f.test_date || null,
        });
        await reviewApi.decideLab(editing.item.id, 'approved');
      }
      toast.success('Corrected and approved');
      setEditing(null);
      review.reload();
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const data = review.data;
  const actions = (kind: 'entity' | 'lab', id: number, onEdit: () => void) => (
    <div className="flex gap-2">
      <Button size="sm" variant="success" loading={busy === `${kind}-${id}`} onClick={() => decide(kind, id, 'approved')} aria-label="Approve"><Check className="h-4 w-4" />Approve</Button>
      <Button size="sm" variant="secondary" onClick={onEdit} aria-label="Correct"><Pencil className="h-4 w-4" />Correct</Button>
      <Button size="sm" variant="danger" disabled={busy === `${kind}-${id}`} onClick={() => decide(kind, id, 'rejected')} aria-label="Reject"><X className="h-4 w-4" />Reject</Button>
    </div>
  );

  return (
    <div>
      <PageHeader title="Review Dashboard" art={IMG.sushruta} subtitle="Verify AI-extracted entities and lab results before they become part of the record" />
      <Card className="mb-6">
        <div className="flex flex-wrap items-end gap-3">
          <div className="w-48"><Input label="Document ID" type="number" min={1} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && load()} /></div>
          <Button onClick={load}><Search className="h-4 w-4" />Load pending items</Button>
        </div>
        <p className="mt-2 text-xs text-slate-500">The backend lists pending reviews per document. Open a patient’s Documents tab to find document IDs, or use the “Review” button there.</p>
      </Card>

      {!docId ? <EmptyState icon={<ClipboardCheck className="h-7 w-7" />} text="Enter a document ID to see its pending extractions." />
        : review.loading ? <SkeletonList rows={4} />
        : review.error ? <ErrorState message={review.error} onRetry={review.reload} />
        : !data || data.total_pending === 0 ? <EmptyState icon={<ClipboardCheck className="h-7 w-7" />} title="All caught up!" text="No pending reviews for this document." />
        : (
          <div className="space-y-8">
            <p className="text-sm text-slate-600">Document #{data.document_id} · <Link className="font-semibold text-brand-700 hover:underline" to={`/patients/${data.patient_id}`}>Patient #{data.patient_id}</Link> · {data.total_pending} pending</p>
            <section>
              <h2 className="mb-3 font-bold text-slate-900">Pending Entities ({data.entities.length})</h2>
              {data.entities.length === 0 ? <p className="text-sm text-slate-500">None pending.</p> : (
                <div className="grid gap-3 lg:grid-cols-2">
                  {data.entities.map((e) => (
                    <Card key={e.id} className="space-y-3">
                      <div className="flex items-center justify-between"><Badge tone="purple">{e.entity_type}</Badge><Confidence value={e.confidence} /></div>
                      <p className="font-mono text-base font-semibold text-slate-900">{showValue(e.value)} <span className="text-slate-500">{e.unit ?? ''}</span></p>
                      {actions('entity', e.id, () => openEdit({ kind: 'entity', item: e }))}
                    </Card>
                  ))}
                </div>
              )}
            </section>
            <section>
              <h2 className="mb-3 font-bold text-slate-900">Pending Lab Results ({data.lab_results.length})</h2>
              {data.lab_results.length === 0 ? <p className="text-sm text-slate-500">None pending.</p> : (
                <div className="grid gap-3 lg:grid-cols-2">
                  {data.lab_results.map((l) => (
                    <Card key={l.id} className="space-y-3">
                      <div className="flex items-center justify-between"><p className="font-bold text-slate-900">{l.test_name}</p><Confidence value={l.confidence} /></div>
                      <LabValue value={l.value} unit={l.unit} range={l.ref_range} />
                      <p className="text-xs text-slate-500">Ref range: <span className="font-mono">{showValue(l.ref_range)}</span> · {formatDate(l.test_date)}</p>
                      {actions('lab', l.id, () => openEdit({ kind: 'lab', item: l }))}
                    </Card>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

      <Modal open={!!editing} onClose={() => setEditing(null)} title="Correct extracted value">
        <form onSubmit={handleSubmit(saveCorrection)} className="space-y-4">
          {editing?.kind === 'lab' && <Input label="Test name" {...register('test_name', { required: true })} />}
          <Input label="Value" type={editing?.kind === 'lab' ? 'number' : 'text'} step="any" className="font-mono" {...register('value', { required: true })} />
          <Input label="Unit" {...register('unit')} />
          {editing?.kind === 'lab' && <><Input label="Reference range" placeholder="70-100" {...register('ref_range')} /><Input label="Test date" type="date" {...register('test_date')} /></>}
          <p className="text-xs text-slate-500">Saving applies your correction and approves the item.</p>
          <div className="flex justify-end gap-2"><Button type="button" variant="secondary" onClick={() => setEditing(null)}>Cancel</Button><Button type="submit" loading={isSubmitting}>Save & Approve</Button></div>
        </form>
      </Modal>
    </div>
  );
}
