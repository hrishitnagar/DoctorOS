import { useEffect, useRef, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { FileSearch, ShieldCheck, Sparkles } from 'lucide-react';
import { Button, Input } from '@/components/ui/ui';
import { CaduceusCoin, Logo } from '@/components/ui/Brand';
import { canTilt } from '@/components/ui/Tilt';
import { useAuth } from '@/hooks/useAuth';
import { getErrorMessage, getStatus } from '@/api/client';
import { SESSION_EXPIRED_KEY } from '@/utils/constants';
import { IMG } from '@/utils/assets';

interface Form { email: string; password: string }

const features = [
  { icon: FileSearch, text: 'OCR turns scanned reports into searchable records' },
  { icon: Sparkles, text: 'Ask AI about any patient history, with cited sources' },
  { icon: ShieldCheck, text: 'Appointment-based access and a full audit trail' },
];

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const scene = useRef<HTMLDivElement>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<Form>();

  useEffect(() => {
    if (sessionStorage.getItem(SESSION_EXPIRED_KEY)) {
      sessionStorage.removeItem(SESSION_EXPIRED_KEY);
      toast.error('Session expired. Please sign in again.');
    }
  }, []);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  // Pointer parallax for the artwork plate (desktop only)
  const onMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const el = scene.current;
    if (!el || !canTilt()) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty('--px', String(((e.clientX - r.left) / r.width - 0.5) * 2));
    el.style.setProperty('--py', String(((e.clientY - r.top) / r.height - 0.5) * 2));
  };

  const onSubmit = async (f: Form) => {
    setError(null);
    try {
      await login(f.email, f.password);
      navigate('/dashboard', { replace: true });
    } catch (e) {
      setError(getStatus(e) === 401 ? 'Invalid email or password' : getErrorMessage(e));
    }
  };

  return (
    <div className="grid min-h-[100svh] lg:grid-cols-[1.15fr_1fr]">
      {/* ---------- artwork panel (3D parallax) ---------- */}
      <section ref={scene} onPointerMove={onMove} className="persp relative h-56 overflow-hidden bg-ink-900 sm:h-72 lg:h-auto"
        style={{ ['--px' as string]: 0, ['--py' as string]: 0 }}>
        <img src={IMG.hero} srcSet={`${IMG.heroSm} 800w, ${IMG.hero} 1440w`} sizes="(min-width:1024px) 58vw, 100vw" alt="Vintage anatomical illustration of a human head and neck"
          fetchPriority="high" decoding="async"
          className="absolute inset-[-4%] h-[108%] w-[108%] max-w-none object-cover object-[25%_50%] transition-transform duration-200 ease-out"
          style={{ transform: 'translate3d(calc(var(--px) * -14px), calc(var(--py) * -10px), 0) scale(1.03)' }} />
        <div className="absolute inset-0 bg-gradient-to-t from-ink-900/85 via-ink-900/10 to-transparent lg:bg-gradient-to-r lg:from-transparent lg:via-transparent lg:to-ink-900/30" />

        <div className="absolute left-4 top-4 sm:left-6 sm:top-6" style={{ transform: 'translateZ(60px)' }}><Logo light /></div>
        <div className="absolute right-4 top-4 hidden animate-float sm:block lg:right-10 lg:top-10"><CaduceusCoin size={92} /></div>

        <div className="absolute inset-x-0 bottom-0 hidden p-8 lg:block">
          <h1 className="max-w-md font-display text-4xl font-bold leading-[1.1] text-paper-50 drop-shadow-lg xl:text-5xl">
            Your patient history,<br /><span className="italic text-ai-200">understood in seconds.</span>
          </h1>
          <ul className="mt-6 grid max-w-xl gap-3 xl:grid-cols-1">
            {features.map(({ icon: Icon, text }, i) => (
              <li key={text} className="flex items-center gap-3 rounded-2xl border border-white/15 bg-ink-900/55 p-3.5 backdrop-blur-md transition-transform duration-200"
                style={{ transform: `translate3d(calc(var(--px) * ${6 + i * 4}px), calc(var(--py) * ${3 + i * 2}px), ${30 + i * 10}px)` }}>
                <Icon className="h-5 w-5 shrink-0 text-ai-200" aria-hidden /><span className="text-sm font-semibold text-paper-100">{text}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* ---------- form panel ---------- */}
      <section className="relative flex items-center justify-center px-4 py-8 sm:py-10">
        <img src={IMG.collage} alt="" aria-hidden loading="lazy" className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-[.07] sepia" />
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="relative w-full max-w-md animate-fadeUp space-y-5 rounded-3xl border border-paper-300 bg-white/90 p-6 shadow-deep backdrop-blur sm:p-8">
          <div className="text-center">
            <div className="mx-auto mb-3 flex justify-center sm:hidden"><CaduceusCoin size={64} /></div>
            <p className="font-label text-[11px] font-bold uppercase tracking-[0.35em] text-brand-700">Doctor Portal</p>
            <h2 className="mt-1 text-3xl font-bold text-ink-900">Welcome back</h2>
            <p className="text-sm text-slate-500">Sign in to DoctorOS AI</p>
          </div>
          <Input label="Email" type="email" autoComplete="email" inputMode="email" placeholder="dr.smith@clinic.com"
            error={errors.email?.message} {...register('email', { required: 'Email is required', pattern: { value: /^\S+@\S+\.\S+$/, message: 'Enter a valid email' } })} />
          <Input label="Password" type="password" autoComplete="current-password" placeholder="••••••••"
            error={errors.password?.message} {...register('password', { required: 'Password is required' })} />
          {error && <p role="alert" className="rounded-xl bg-rust-50 p-3 text-sm font-semibold text-rust-700">{error}</p>}
          <Button type="submit" loading={isSubmitting} className="w-full py-3">Sign In</Button>
          <p className="text-center text-xs text-slate-500">Accounts are created by your administrator.</p>
        </form>
      </section>
    </div>
  );
}
