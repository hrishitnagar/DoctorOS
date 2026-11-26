import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { Bot, MessageSquarePlus, MessagesSquare, Send, Sparkles, User } from 'lucide-react';
import { conversationApi } from '@/api/conversationApi';
import { getErrorMessage } from '@/api/client';
import { ragApi } from '@/api/ragApi';
import { Button, Card, EmptyState, ErrorState, Spinner, Textarea } from '@/components/ui/ui';
import { AIDisclaimer, AILabel, CitationList, CitedMarkdown } from '@/components/medical/medical';
import { useApi } from '@/hooks/useApi';
import type { ChatMessage, RagAnswer } from '@/types';
import { formatDate } from '@/utils/formatDate';
import { IMG } from '@/utils/assets';

/* ---------------- Ask (RAG) ---------------- */
function AskPanel({ patientId }: { patientId: number }) {
  const [q, setQ] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<{ q: string; a: RagAnswer }[]>([]);

  const ask = async () => {
    if (!q.trim()) return;
    setBusy(true); setError(null);
    try { const a = await ragApi.ask(patientId, q.trim()); setHistory((h) => [{ q: q.trim(), a }, ...h]); setQ(''); }
    catch (e) { setError(getErrorMessage(e)); toast.error(getErrorMessage(e)); } finally { setBusy(false); }
  };

  return (
    <div className="space-y-4">
      <Card className="space-y-3">
        <Textarea label="Ask about this patient’s records" maxLength={2000} value={q} onChange={(e) => setQ(e.target.value)}
          placeholder="e.g. What were the patient's last blood glucose readings?" onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) void ask(); }} />
        <div className="flex items-center justify-between"><span className="text-xs text-slate-500">Ctrl/⌘ + Enter to send</span>
          <Button variant="ai" loading={busy} onClick={ask} disabled={!q.trim()}><Sparkles className="h-4 w-4" />Ask</Button></div>
      </Card>
      {busy && <Spinner label="Searching records and generating an answer…" />}
      {error && <ErrorState message={error} />}
      {!busy && history.length === 0 && !error && <EmptyState icon={<Sparkles className="h-7 w-7" />} text="Ask a question to get an answer with cited sources from this patient’s documents." />}
      {history.map((h, i) => (
        <Card key={i} className="space-y-3 border-ai-200">
          <p className="text-sm font-semibold text-slate-900">Q: {h.q}</p>
          <AILabel />
          <CitedMarkdown content={h.a.answer} citations={h.a.citations} />
          <CitationList citations={h.a.citations} />
          <p className="text-xs text-slate-500">{h.a.retrieved_chunks} passage(s) retrieved</p>
          <AIDisclaimer />
        </Card>
      ))}
    </div>
  );
}

/* ---------------- Chat ---------------- */
function ChatPanel({ patientId }: { patientId: number }) {
  const convs = useApi(() => conversationApi.list(patientId), [patientId]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingConv, setLoadingConv] = useState(false);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, sending]);

  const open = async (id: number) => {
    setActiveId(id); setLoadingConv(true);
    try { setMessages((await conversationApi.detail(patientId, id)).messages); }
    catch (e) { toast.error(getErrorMessage(e)); } finally { setLoadingConv(false); }
  };
  const fresh = () => { setActiveId(null); setMessages([]); };

  const send = async () => {
    const question = text.trim();
    if (!question || sending) return;
    const tempId = -Date.now();
    setMessages((m) => [...m, { id: tempId, role: 'user', content: question, citations: [], created_at: new Date().toISOString() }]);
    setText(''); setSending(true);
    try {
      const r = await conversationApi.chat(patientId, question, activeId);
      setActiveId(r.conversation.id);
      setMessages((m) => [...m.filter((x) => x.id !== tempId), r.user_message, r.assistant_message]);
      convs.reload();
    } catch (e) {
      setMessages((m) => m.filter((x) => x.id !== tempId)); setText(question);
      toast.error(getErrorMessage(e));
    } finally { setSending(false); }
  };

  if (convs.status === 403 && convs.error) return <ErrorState message={convs.error} />;

  return (
    <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
      <Card className="h-fit space-y-3 p-4">
        <Button variant="ai" className="w-full" onClick={fresh}><MessageSquarePlus className="h-4 w-4" />New Conversation</Button>
        {convs.loading ? <Spinner /> : convs.error ? <p className="text-xs text-rust-600">{convs.error}</p>
          : !convs.data || convs.data.conversations.length === 0 ? <p className="text-sm text-slate-500">No conversations yet. Ask your first question.</p>
          : <ul className="max-h-[420px] space-y-1 overflow-y-auto">{convs.data.conversations.map((c) => (
              <li key={c.id}><button onClick={() => void open(c.id)} aria-current={activeId === c.id}
                className={`w-full rounded-xl px-3 py-2 text-left text-sm transition ${activeId === c.id ? 'bg-ai-100 text-ai-700' : 'hover:bg-slate-100'}`}>
                <span className="line-clamp-2 font-semibold">{c.title}</span><span className="text-xs text-slate-500">{formatDate(c.updated_at)}</span></button></li>))}</ul>}
      </Card>

      <Card className="flex min-h-[460px] flex-col p-0">
        <div className="flex-1 space-y-4 overflow-y-auto p-5" aria-live="polite">
          {loadingConv ? <Spinner /> : messages.length === 0 && !sending ? <EmptyState icon={<MessagesSquare className="h-7 w-7" />} text="Start a conversation about this patient’s history." /> :
            messages.map((m) => m.role === 'user' ? (
              <div key={m.id} className="flex justify-end gap-2"><div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-gradient-to-r from-brand-600 to-brand-500 px-4 py-2.5 text-sm text-white shadow">{m.content}</div>
                <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-700"><User className="h-4 w-4" aria-hidden /></span></div>
            ) : (
              <div key={m.id} className="flex gap-2"><span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ai-100 text-ai-700"><Bot className="h-4 w-4" aria-hidden /></span>
                <div className="max-w-[85%] space-y-2 rounded-2xl rounded-tl-sm border border-ai-200 bg-ai-50/60 px-4 py-3">
                  <AILabel compact /><CitedMarkdown content={m.content} citations={m.citations} /><CitationList citations={m.citations} /></div></div>
            ))}
          {sending && <div className="flex items-center gap-2 text-sm text-ai-700"><Spinner label="Assistant is thinking…" /></div>}
          <div ref={bottom} />
        </div>
        <div className="space-y-2 border-t border-slate-100 p-4">
          <AIDisclaimer />
          <div className="flex items-end gap-2">
            <textarea aria-label="Message" rows={2} value={text} maxLength={2000} onChange={(e) => setText(e.target.value)} placeholder="Type your question…"
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send(); } }}
              className="flex-1 resize-none rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-ai-500 focus:outline-none focus:ring-2 focus:ring-ai-200" />
            <Button variant="ai" onClick={send} loading={sending} disabled={!text.trim()} aria-label="Send message"><Send className="h-4 w-4" />Send</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default function AssistantTab({ patientId, patientName }: { patientId: number; patientName: string }) {
  const [mode, setMode] = useState<'ask' | 'chat'>('chat');
  return (
    <div className="space-y-4">
      <div className="relative overflow-hidden rounded-2xl border border-paper-300 bg-white shadow-soft">
        <img src={IMG.watercolor} alt="" aria-hidden loading="lazy" decoding="async" className="absolute inset-y-0 right-0 h-full w-3/4 object-cover object-[60%_30%] sm:w-2/3"
          style={{ WebkitMaskImage: 'linear-gradient(to left, #000 35%, transparent)', maskImage: 'linear-gradient(to left, #000 35%, transparent)' }} />
        <div className="relative px-5 py-5">
          <p className="font-label text-[10px] font-bold uppercase tracking-[0.3em] text-ai-700">Clinical AI</p>
          <h2 className="text-2xl font-bold text-ink-900">Ask {patientName}’s records</h2>
        </div>
      </div>
      <p className="text-sm text-slate-600">Answering only from <strong>{patientName}</strong>’s records. Requires a scheduled or completed appointment with this patient.</p>
      <div className="inline-flex rounded-xl bg-white p-1 ring-1 ring-slate-200" role="tablist">
        {(['chat', 'ask'] as const).map((m) => (
          <button key={m} role="tab" aria-selected={mode === m} onClick={() => setMode(m)}
            className={`rounded-lg px-4 py-1.5 text-sm font-semibold ${mode === m ? 'bg-gradient-to-b from-ai-500 to-ai-700 text-white' : 'text-slate-600'}`}>{m === 'chat' ? 'Chat' : 'Quick Q&A'}</button>
        ))}
      </div>
      {mode === 'ask' ? <AskPanel patientId={patientId} /> : <ChatPanel patientId={patientId} />}
    </div>
  );
}
