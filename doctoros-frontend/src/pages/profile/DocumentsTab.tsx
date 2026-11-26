import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { ClipboardCheck, FileText, ScanText, UploadCloud } from 'lucide-react';
import { documentApi } from '@/api/documentApi';
import { getErrorMessage } from '@/api/client';
import { Button, Card, EmptyState, StatusBadge } from '@/components/ui/ui';
import type { TimelineDocument, TimelineRecord } from '@/types';
import { ALLOWED_UPLOAD_TYPES, MAX_UPLOAD_BYTES } from '@/utils/constants';
import { formatDateTime } from '@/utils/formatDate';

function validate(file: File): string | null {
  if (!ALLOWED_UPLOAD_TYPES.includes(file.type)) return 'File type not supported. Please upload PDF, PNG, or JPEG files.';
  if (file.size > MAX_UPLOAD_BYTES) return 'File is too large. Maximum allowed size is 10 MB.';
  if (file.size === 0) return 'The file is empty.';
  return null;
}

export default function DocumentsTab({ patientId, timeline, onRefresh }: { patientId: number; timeline: TimelineRecord[]; onRefresh: () => void }) {
  const [progress, setProgress] = useState<number | null>(null);
  const [drag, setDrag] = useState(false);
  const [processing, setProcessing] = useState<number | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const docs = timeline.filter((r): r is TimelineDocument => r.type === 'document');
  const active = docs.some((d) => ['pending', 'processing'].includes(d.ocr_status.toLowerCase()));

  // Poll while the backend is still running OCR in the background.
  const refresh = useCallback(onRefresh, [onRefresh]);
  useEffect(() => { if (!active) return; const t = setInterval(refresh, 6000); return () => clearInterval(t); }, [active, refresh]);

  const upload = async (file: File | undefined) => {
    if (!file) return;
    const err = validate(file);
    if (err) return toast.error(err);
    setProgress(0);
    try {
      const doc = await documentApi.upload(patientId, file, setProgress);
      toast.success(`Uploaded (document #${doc.id}). OCR is running in the background.`);
      onRefresh();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setProgress(null); if (input.current) input.current.value = ''; }
  };

  const process = async (id: number) => {
    setProcessing(id);
    toast('Processing started…', { icon: 'ℹ️' });
    try {
      const r = await documentApi.processOcr(id);
      r.success ? toast.success(`${r.entities_saved} entities and ${r.lab_results_saved} lab results saved`) : toast.error(r.message);
      onRefresh();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setProcessing(null); }
  };

  return (
    <div className="space-y-5">
      <div
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); void upload(e.dataTransfer.files[0]); }}
        className={`flex flex-col items-center rounded-2xl border-2 border-dashed p-8 text-center transition ${drag ? 'border-brand-500 bg-brand-50' : 'border-slate-300 bg-white/60 hover:border-brand-400'}`}>
        <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-ink-600 to-ink-900 text-white shadow-lg"><UploadCloud className="h-7 w-7" /></div>
        <p className="font-semibold text-slate-900">Drag & drop a medical document here</p>
        <p className="mb-3 text-xs text-slate-500">PDF, PNG, JPG or JPEG · max 10 MB</p>
        <input ref={input} type="file" accept=".pdf,.png,.jpg,.jpeg" className="sr-only" id="file-input" aria-label="Choose file" onChange={(e) => void upload(e.target.files?.[0])} />
        <Button onClick={() => input.current?.click()} loading={progress !== null}>Browse files</Button>
        {progress !== null && (
          <div className="mt-4 w-full max-w-sm" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
            <div className="h-2 overflow-hidden rounded-full bg-slate-200"><div className="h-full bg-gradient-to-r from-brand-500 to-ai-500 transition-all" style={{ width: `${progress}%` }} /></div>
            <p className="mt-1 text-xs text-slate-500">{progress}%</p>
          </div>
        )}
      </div>

      {docs.length === 0 ? <EmptyState icon={<FileText className="h-7 w-7" />} text="No documents uploaded. Upload a medical document to begin." /> : (
        <div className="grid gap-3 md:grid-cols-2">
          {docs.map((d) => (
            <Card key={d.id} className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-ai-100 text-ai-700"><FileText className="h-5 w-5" /></div>
                  <div><p className="font-semibold text-slate-900">Document #{d.id}</p><p className="text-xs text-slate-500">{d.document_type} · {formatDateTime(d.date)}</p></div></div>
                <StatusBadge status={d.ocr_status} />
              </div>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" variant="secondary" loading={processing === d.id} onClick={() => process(d.id)}><ScanText className="h-4 w-4" />{d.ocr_status.toLowerCase() === 'pending' ? 'Process OCR' : 'Re-process'}</Button>
                <Link to={`/reviews?doc=${d.id}`}><Button size="sm" variant="ai"><ClipboardCheck className="h-4 w-4" />Review extractions</Button></Link>
              </div>
            </Card>
          ))}
        </div>
      )}
      <p className="text-xs text-slate-500">The document list comes from the patient timeline (the backend has no document list or file viewer).</p>
    </div>
  );
}
