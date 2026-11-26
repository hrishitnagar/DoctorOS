import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import toast from 'react-hot-toast';
import { FileText, RefreshCw, Sparkles } from 'lucide-react';
import { getErrorMessage } from '@/api/client';
import { summaryApi } from '@/api/summaryApi';
import { Badge, Button, Card, EmptyState, ErrorState, Modal, SkeletonList } from '@/components/ui/ui';
import { AIDisclaimer, AILabel } from '@/components/medical/medical';
import { useApi } from '@/hooks/useApi';
import type { PatientSummary } from '@/types';
import { formatDate, formatDateTime } from '@/utils/formatDate';

export default function SummaryTab({ patientId }: { patientId: number }) {
  const { data, error, status, loading, reload } = useApi(() => summaryApi.get(patientId), [patientId]);
  const [created, setCreated] = useState<PatientSummary | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);

  const summary = created ?? data;
  const generate = async (force: boolean) => {
    setBusy(true); setConfirm(false); setGenError(null);
    try { setCreated(await summaryApi.generate(patientId, force)); toast.success('Summary generated'); }
    catch (e) { setGenError(getErrorMessage(e)); toast.error(getErrorMessage(e)); } finally { setBusy(false); }
  };

  if (loading) return <SkeletonList rows={3} />;
  if (error && status !== 404 && !summary) return <ErrorState message={error} onRetry={reload} />;

  if (!summary) {
    return (
      <div className="space-y-3">
        <EmptyState icon={<Sparkles className="h-7 w-7" />} title="No clinical summary has been generated yet."
          text="AI will analyze this patient's complete medical history to generate a comprehensive clinical summary."
          action={<Button variant="ai" loading={busy} onClick={() => generate(false)}><Sparkles className="h-4 w-4" />Generate Clinical Summary</Button>} />
        {busy && <p className="text-center text-sm text-slate-500">Generating — this can take several seconds…</p>}
        {genError && <ErrorState message={genError} />}
      </div>
    );
  }

  const groups = (summary.citations ?? []).reduce<Record<string, NonNullable<PatientSummary['citations']>>>((acc, c) => {
    (acc[c.record_type] ??= []).push(c); return acc;
  }, {});

  return (
    <div className="space-y-4">
      <Card className="space-y-4 border-ai-200">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <AILabel />
          <Button variant="secondary" size="sm" loading={busy} onClick={() => setConfirm(true)}><RefreshCw className="h-4 w-4" />Regenerate Summary</Button>
        </div>
        <div className="md-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{summary.summary}</ReactMarkdown></div>
        <p className="text-xs text-slate-500">Generated on {formatDateTime(summary.generated_at)}</p>
        {genError && <ErrorState message={genError} />}
        <AIDisclaimer text="This AI-generated summary requires clinical review." />
      </Card>
      <Card>
        <h3 className="mb-3 font-bold text-slate-900">References (timeline records used)</h3>
        {Object.keys(groups).length === 0 ? <p className="text-sm text-slate-500">No references were returned.</p> :
          Object.entries(groups).map(([type, items]) => (
            <div key={type} className="mb-3"><p className="mb-1 flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-slate-500"><FileText className="h-3.5 w-3.5" />{type.replace('_', ' ')}s</p>
              <ul className="flex flex-wrap gap-2">{items.map((c) => <li key={`${c.record_type}-${c.record_id}`}><Badge tone="purple">#{c.record_id} · {formatDate(c.date)}{c.document_id ? ` · doc ${c.document_id}` : ''}</Badge></li>)}</ul></div>
          ))}
      </Card>
      <Modal open={confirm} onClose={() => setConfirm(false)} title="Regenerate summary?">
        <p className="text-sm text-slate-600">This replaces the existing summary with a newly generated one.</p>
        <div className="mt-5 flex justify-end gap-2"><Button variant="secondary" onClick={() => setConfirm(false)}>Cancel</Button><Button variant="ai" onClick={() => generate(true)}>Regenerate</Button></div>
      </Modal>
    </div>
  );
}
