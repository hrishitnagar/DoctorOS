import { useEffect, useRef, type CSSProperties, type ReactNode } from 'react';

/** True only on devices with a real hover pointer and when the user has not asked for reduced motion. */
export const canTilt = (): boolean =>
  typeof window !== 'undefined' &&
  window.matchMedia('(hover: hover) and (pointer: fine)').matches &&
  !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/** 3D tilt-on-hover wrapper with a moving light glare. Does nothing on touch screens. */
export function Tilt({ children, className = '', max = 9, lift = 10, style }: { children: ReactNode; className?: string; max?: number; lift?: number; style?: CSSProperties }) {
  const ref = useRef<HTMLDivElement>(null);
  const on = useRef(false);
  useEffect(() => { on.current = canTilt(); }, []);

  const move = (e: React.PointerEvent<HTMLDivElement>) => {
    const el = ref.current;
    if (!el || !on.current) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width;
    const y = (e.clientY - r.top) / r.height;
    el.style.transform = `perspective(900px) rotateX(${(0.5 - y) * max}deg) rotateY(${(x - 0.5) * max}deg) translateZ(${lift}px)`;
    el.style.setProperty('--mx', `${x * 100}%`);
    el.style.setProperty('--my', `${y * 100}%`);
    el.classList.add('is-active');
  };
  const leave = () => {
    const el = ref.current;
    if (!el) return;
    el.style.transform = '';
    el.classList.remove('is-active');
  };

  return <div ref={ref} onPointerMove={move} onPointerLeave={leave} className={`tilt ${className}`} style={style}>{children}</div>;
}
