import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { ClipboardCheck, LayoutDashboard, LogOut, Menu, Users, X } from 'lucide-react';
import { Logo } from '@/components/ui/Brand';
import { useAuth } from '@/hooks/useAuth';
import { IMG } from '@/utils/assets';

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/patients', label: 'Patients', icon: Users },
  { to: '/reviews', label: 'Review Dashboard', icon: ClipboardCheck },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);

  const sidebar = (
    <nav aria-label="Main navigation" className="relative flex h-full flex-col overflow-hidden bg-ink-900 p-4 text-paper-100">
      <img src={IMG.collage} alt="" aria-hidden loading="lazy" decoding="async"
        className="pointer-events-none absolute inset-x-0 bottom-0 h-3/5 w-full object-cover opacity-[.16] sepia"
        style={{ WebkitMaskImage: 'linear-gradient(to top, #000 30%, transparent)', maskImage: 'linear-gradient(to top, #000 30%, transparent)' }} />
      <div className="relative mb-8 px-2 pt-2"><Logo light /></div>
      <ul className="relative space-y-1.5">
        {nav.map(({ to, label, icon: Icon }) => (
          <li key={to}>
            <NavLink to={to} onClick={() => setOpen(false)}
              className={({ isActive }) => `group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold transition ${
                isActive ? 'bg-gradient-to-r from-ai-500 to-ai-700 text-white shadow-[0_3px_0_#4a3106]' : 'text-paper-200/80 hover:bg-white/10 hover:text-white'}`}>
              <Icon className="h-5 w-5" aria-hidden />{label}
            </NavLink>
          </li>
        ))}
      </ul>
      <div className="relative mt-auto rounded-2xl border border-white/10 bg-white/5 p-3 text-[11px] leading-relaxed text-paper-200/80 backdrop-blur">
        Synthetic-data demo. AI output assists doctors and never replaces clinical judgment.
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 shadow-deep lg:block">{sidebar}</aside>
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-ink-900/70 backdrop-blur-sm" onClick={() => setOpen(false)} />
          <div className="relative h-full w-[78%] max-w-xs animate-fadeUp">{sidebar}
            <button aria-label="Close menu" onClick={() => setOpen(false)} className="absolute right-2 top-2 rounded-lg p-2 text-white hover:bg-white/10"><X className="h-5 w-5" /></button>
          </div>
        </div>
      )}
      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex items-center justify-between gap-2 border-b border-paper-300/70 bg-paper-100/80 px-3 py-2.5 pt-[max(0.625rem,env(safe-area-inset-top))] backdrop-blur-md sm:px-4 lg:px-8">
          <div className="flex items-center gap-2">
            <button className="rounded-lg p-2 text-slate-800 hover:bg-slate-200/60 lg:hidden" aria-label="Open menu" onClick={() => setOpen(true)}><Menu className="h-5 w-5" /></button>
            <div className="lg:hidden"><Logo compact /></div>
            <p className="hidden font-label text-xs font-bold uppercase tracking-[0.25em] text-slate-500 lg:block">Clinical Management System</p>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-ink-600 to-ink-900 font-display text-sm font-bold text-ai-200 ring-2 ring-ai-500/60">
                {user?.doctor_name.replace(/^Dr\.?\s*/i, '').charAt(0).toUpperCase() ?? 'D'}
              </div>
              <span className="hidden max-w-[10rem] truncate text-sm font-bold text-slate-800 sm:block">{user?.doctor_name}</span>
            </div>
            <button onClick={logout} className="flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-bold text-slate-700 shadow-[0_2px_0_#CFC1A3] active:translate-y-[2px] active:shadow-none">
              <LogOut className="h-4 w-4" aria-hidden /><span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>
        <main className="mx-auto max-w-[1280px] px-3 py-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] sm:px-4 lg:px-8"><Outlet /></main>
      </div>
    </div>
  );
}
