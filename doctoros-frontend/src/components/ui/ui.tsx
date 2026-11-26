import {
  forwardRef, useEffect, useId, useRef,
  type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode,
  type SelectHTMLAttributes, type TextareaHTMLAttributes,
} from 'react';
import { AlertTriangle, Loader2, X } from 'lucide-react';
import { IMG } from '@/utils/assets';
import { Tilt } from './Tilt';

/* ---------- Button ---------- */
type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success' | 'ai';
const variants: Record<Variant, string> = {
  primary: 'bg-gradient-to-b from-brand-500 to-brand-700 text-white shadow-[0_3px_0_#1B3739,0_12px_18px_-8px_rgba(27,55,57,.65)] active:translate-y-[3px] active:shadow-[0_0_0_#1B3739] hover:brightness-110',
  secondary: 'bg-white text-slate-800 border border-slate-300 shadow-[0_2px_0_#CFC1A3] active:translate-y-[2px] active:shadow-none hover:bg-paper-50',
  ghost: 'text-slate-700 hover:bg-slate-200/60',
  danger: 'bg-gradient-to-b from-rust-500 to-rust-700 text-white shadow-[0_3px_0_#5a1812,0_12px_18px_-8px_rgba(120,32,25,.6)] active:translate-y-[3px] active:shadow-[0_0_0_#5a1812] hover:brightness-110',
  success: 'bg-gradient-to-b from-moss-500 to-moss-700 text-white shadow-[0_3px_0_#1e3a24,0_12px_18px_-8px_rgba(45,86,54,.6)] active:translate-y-[3px] active:shadow-[0_0_0_#1e3a24] hover:brightness-110',
  ai: 'bg-gradient-to-b from-ai-500 to-ai-700 text-white shadow-[0_3px_0_#4a3106,0_12px_18px_-8px_rgba(122,80,12,.7)] active:translate-y-[3px] active:shadow-[0_0_0_#4a3106] hover:brightness-110',
};
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> { variant?: Variant; loading?: boolean; size?: 'sm' | 'md' }

export function Button({ variant = 'primary', loading, size = 'md', className = '', children, disabled, ...rest }: ButtonProps) {
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 rounded-xl font-bold tracking-wide transition disabled:cursor-not-allowed disabled:opacity-50 ${
        size === 'sm' ? 'px-3 py-1.5 text-xs' : 'px-4 py-2.5 text-sm'
      } ${variants[variant]} ${className}`}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
      {children}
    </button>
  );
}

/* ---------- Card ---------- */
export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-2xl border border-paper-300/70 bg-white/85 p-5 shadow-soft backdrop-blur-sm ${className}`}>{children}</div>;
}

/* ---------- Badge ---------- */
export type Tone = 'gray' | 'blue' | 'green' | 'red' | 'amber' | 'orange' | 'purple' | 'teal';
const tones: Record<Tone, string> = {
  gray: 'bg-slate-100 text-slate-700 ring-slate-300',
  blue: 'bg-azure-50 text-azure-700 ring-azure-100',
  green: 'bg-moss-50 text-moss-700 ring-moss-100',
  red: 'bg-rust-50 text-rust-700 ring-rust-100',
  amber: 'bg-ai-50 text-ai-700 ring-ai-200',
  orange: 'bg-orange-50 text-orange-700 ring-orange-200',
  purple: 'bg-ai-50 text-ai-700 ring-ai-200',
  teal: 'bg-brand-50 text-brand-700 ring-brand-200',
};
export function Badge({ tone = 'gray', children, className = '' }: { tone?: Tone; children: ReactNode; className?: string }) {
  return <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${tones[tone]} ${className}`}>{children}</span>;
}

const statusTone: Record<string, Tone> = {
  pending: 'gray', processing: 'blue', done: 'green', completed: 'green', failed: 'red', skipped: 'amber',
  scheduled: 'blue', cancelled: 'gray', 'no-show': 'orange', approved: 'green', rejected: 'red',
};
export function StatusBadge({ status }: { status: string }) {
  const s = status.toLowerCase();
  return (
    <Badge tone={statusTone[s] ?? 'gray'}>
      {s === 'processing' && <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-azure-500" />}
      <span className="sr-only">Status: </span>
      {status}
    </Badge>
  );
}

/* ---------- Form fields ---------- */
const fieldBase = 'w-full rounded-xl border bg-white px-3 py-2.5 text-base sm:text-sm shadow-[inset_0_2px_3px_rgba(70,50,20,.08)] transition placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200';
function Field({ label, error, hint, id, children }: { label?: string; error?: string; hint?: string; id: string; children: ReactNode }) {
  return (
    <div className="space-y-1.5">
      {label && <label htmlFor={id} className="block font-label text-[11px] font-bold uppercase tracking-[0.14em] text-slate-600">{label}</label>}
      {children}
      {hint && !error && <p className="text-xs text-slate-500">{hint}</p>}
      {error && <p role="alert" className="text-xs font-medium text-rust-600">{error}</p>}
    </div>
  );
}
interface FieldProps { label?: string; error?: string; hint?: string }

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & FieldProps>(
  ({ label, error, hint, className = '', id, ...rest }, ref) => {
    const uid = useId(); const fid = id ?? uid;
    return (
      <Field label={label} error={error} hint={hint} id={fid}>
        <input ref={ref} id={fid} aria-invalid={!!error} className={`${fieldBase} ${error ? 'border-rust-500' : 'border-slate-200'} ${className}`} {...rest} />
      </Field>
    );
  },
);
Input.displayName = 'Input';

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement> & FieldProps>(
  ({ label, error, hint, className = '', id, ...rest }, ref) => {
    const uid = useId(); const fid = id ?? uid;
    return (
      <Field label={label} error={error} hint={hint} id={fid}>
        <textarea ref={ref} id={fid} rows={3} aria-invalid={!!error} className={`${fieldBase} ${error ? 'border-rust-500' : 'border-slate-200'} ${className}`} {...rest} />
      </Field>
    );
  },
);
Textarea.displayName = 'Textarea';

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement> & FieldProps>(
  ({ label, error, hint, className = '', id, children, ...rest }, ref) => {
    const uid = useId(); const fid = id ?? uid;
    return (
      <Field label={label} error={error} hint={hint} id={fid}>
        <select ref={ref} id={fid} className={`${fieldBase} ${error ? 'border-rust-500' : 'border-slate-200'} ${className}`} {...rest}>{children}</select>
      </Field>
    );
  },
);
Select.displayName = 'Select';

/* ---------- Modal ---------- */
export function Modal({ open, onClose, title, children, wide }: { open: boolean; onClose: () => void; title: string; children: ReactNode; wide?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const prev = document.activeElement as HTMLElement | null;
    ref.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    return () => { document.removeEventListener('keydown', onKey); prev?.focus(); };
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/60 p-3 backdrop-blur-sm sm:p-4" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={title}
        className={`max-h-[92vh] w-full overflow-y-auto rounded-2xl border border-paper-300 bg-white p-5 shadow-deep animate-fadeUp sm:p-6 ${wide ? 'max-w-2xl' : 'max-w-lg'}`}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-xl font-bold text-slate-900">{title}</h2>
          <button onClick={onClose} aria-label="Close dialog" className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100"><X className="h-5 w-5" /></button>
        </div>
        {children}
      </div>
    </div>
  );
}

/* ---------- Loading / empty / error ---------- */
export function Spinner({ label = 'Loading…' }: { label?: string }) {
  return <div role="status" className="flex items-center justify-center gap-2 py-10 text-sm text-slate-500"><Loader2 className="h-5 w-5 animate-spin text-brand-600" />{label}</div>;
}
export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-xl bg-gradient-to-r from-slate-100 via-slate-200 to-slate-100 ${className}`} aria-hidden />;
}
export function SkeletonList({ rows = 4 }: { rows?: number }) {
  return <div className="space-y-3" role="status" aria-label="Loading">{Array.from({ length: rows }, (_, i) => <Skeleton key={i} className="h-16 w-full" />)}</div>;
}
const ART = [IMG.heart, IMG.lungs, IMG.brain, IMG.digestive];

export function EmptyState({ icon, title, text, action, art }: { icon: ReactNode; title?: string; text: string; action?: ReactNode; art?: string }) {
  const src = art ?? ART[(text.length + (title?.length ?? 0)) % ART.length];
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/55 px-5 py-10 text-center sm:px-6 sm:py-12">
      <Tilt className="mb-4" max={14}>
        <div className="relative">
          <div className="plate -rotate-3"><img src={src} alt="" loading="lazy" decoding="async" className="sepia-print h-28 w-24 rounded-[3px] object-cover sm:h-32 sm:w-28" /></div>
          <div className="absolute -bottom-3 -right-4 flex h-11 w-11 items-center justify-center rounded-full bg-ink-900 text-ai-200 shadow-lg ring-4 ring-paper-100">{icon}</div>
        </div>
      </Tilt>
      {title && <h3 className="font-display text-lg font-bold text-slate-900">{title}</h3>}
      <p className="mt-1 max-w-md text-sm text-slate-600">{text}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-center rounded-2xl border border-rust-100 bg-rust-50 px-6 py-8 text-center">
      <AlertTriangle className="mb-2 h-8 w-8 text-rust-500" aria-hidden />
      <p className="text-sm font-semibold text-rust-700">{message}</p>
      {onRetry && <Button variant="secondary" size="sm" className="mt-3" onClick={onRetry}>Try again</Button>}
    </div>
  );
}
export function PageHeader({ title, subtitle, actions, art }: { title: string; subtitle?: string; actions?: ReactNode; art?: string }) {
  return (
    <div className="relative mb-6 flex flex-wrap items-end justify-between gap-3 overflow-hidden rounded-2xl border border-paper-300/70 bg-white/60 px-5 py-5 shadow-soft">
      {art && (
        <img src={art} alt="" loading="lazy" decoding="async" aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 hidden h-full w-1/2 object-cover opacity-40 sepia-print md:block"
          style={{ WebkitMaskImage: 'linear-gradient(to left, #000 20%, transparent)', maskImage: 'linear-gradient(to left, #000 20%, transparent)' }} />
      )}
      <div className="relative">
        <p className="font-label text-[10px] font-bold uppercase tracking-[0.3em] text-brand-700">DoctorOS</p>
        <h1 className="text-3xl font-bold text-ink-900 sm:text-4xl">{title}</h1>
        {subtitle && <p className="mt-1 max-w-xl text-sm text-slate-600">{subtitle}</p>}
      </div>
      {actions && <div className="relative flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}
