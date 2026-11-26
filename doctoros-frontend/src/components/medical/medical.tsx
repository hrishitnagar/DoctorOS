import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, Info, Sparkles } from 'lucide-react';
import type { RagCitation } from '@/types';
import { AI_DISCLAIMER, AI_LABEL } from '@/utils/constants';
import { formatDate } from '@/utils/formatDate';
import { labFlag, showValue } from '@/utils/formatMedical';

export function AILabel({ compact }: { compact?: boolean }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-gradient-to-r from-ai-600 to-rust-500 px-3 py-1 text-xs font-bold text-white shadow">
      <Sparkles className="h-3.5 w-3.5" aria-hidden />
      {compact ? 'AI-Generated' : AI_LABEL}
    </span>
  );
}

export function AIDisclaimer({ text = AI_DISCLAIMER }: { text?: string }) {
  return (
    <p className="flex items-start gap-2 rounded-xl border border-ai-200 bg-ai-50 p-3 text-xs text-ai-700">
      <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />{text}
    </p>
  );
}

export function CitationBadge({ id, citation }: { id: string; citation?: RagCitation }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-block align-baseline">
      <button type="button" onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-label={`Citation ${id}`}
        className="mx-0.5 rounded-md bg-ai-100 px-1.5 py-0.5 text-xs font-bold text-ai-700 hover:bg-ai-200">[{id}]</button>
      {open && (
        <span role="dialog" className="absolute left-0 top-full z-20 mt-1 block w-56 rounded-xl border border-ai-200 bg-white p-3 text-left text-xs shadow-xl">
          {citation ? (
            <>
              <strong className="block text-slate-900">Document #{citation.document_id}</strong>
              <span className="block text-slate-600">Page: {citation.page_no ?? 'n/a'}</span>
              <span className="block text-slate-600">Date: {formatDate(citation.document_date)}</span>
              <span className="block text-slate-500">Chunk {citation.chunk_index} (id {citation.chunk_id})</span>
            </>
          ) : <span className="text-slate-600">No details were returned for this reference.</span>}
        </span>
      )}
    </span>
  );
}

/** Renders markdown and turns [S1] markers into clickable citation badges. */
export function CitedMarkdown({ content, citations = [] }: { content: string; citations?: RagCitation[] | null }) {
  const list = citations ?? [];
  const text = content.replace(/\[(S\d+)\]/g, '[$1](#cite-$1)');
  return (
    <div className="md-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
        a: ({ href, children }) => {
          if (href?.startsWith('#cite-')) {
            const id = href.slice(6);
            return <CitationBadge id={id} citation={list.find((c) => c.source_id === id)} />;
          }
          return <a href={href} target="_blank" rel="noopener noreferrer" className="text-brand-700 underline">{children}</a>;
        },
      }}>{text}</ReactMarkdown>
    </div>
  );
}

export function CitationList({ citations }: { citations?: RagCitation[] | null }) {
  if (!citations || citations.length === 0) return null;
  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <p className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">Sources</p>
      <ul className="flex flex-wrap gap-2">
        {citations.map((c) => (
          <li key={`${c.source_id}-${c.chunk_id}`} className="flex items-center gap-1.5 rounded-lg bg-ai-50 px-2.5 py-1.5 text-xs text-ai-700 ring-1 ring-ai-200">
            <FileText className="h-3.5 w-3.5" aria-hidden />
            <strong>[{c.source_id}]</strong> Doc #{c.document_id} · p.{c.page_no ?? '—'} · {formatDate(c.document_date)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function LabValue({ value, unit, range }: { value: number; unit: string | null; range: string | null }) {
  const flag = labFlag(value, range);
  const color = flag === 'abnormal' ? 'text-rust-600' : flag === 'normal' ? 'text-moss-600' : 'text-slate-800';
  return (
    <span className="font-mono">
      <span className={`text-base font-bold ${color}`}>{showValue(value)}</span>
      <span className="ml-1 text-slate-500">{showValue(unit) === '—' ? '' : unit}</span>
      {flag === 'abnormal' && <span className="ml-2 rounded bg-rust-100 px-1.5 py-0.5 text-[10px] font-bold text-rust-700">OUT OF RANGE</span>}
    </span>
  );
}
