/** Caduceus drawn from the supplied symbol, recolourable through the text colour. */
export function Caduceus({ className = '', style }: { className?: string; style?: React.CSSProperties }) {
  return <span aria-hidden className={`caduceus inline-block ${className}`} style={style} />;
}

/** Spinning 3D coin with the caduceus. */
export function CaduceusCoin({ size = 84, className = '' }: { size?: number; className?: string }) {
  return (
    <div className={`persp ${className}`} style={{ width: size, height: size }} aria-hidden>
      <div className="preserve-3d h-full w-full animate-coin">
        <div className="absolute inset-0 flex items-center justify-center rounded-full bg-gradient-to-br from-ai-200 via-ai-500 to-ai-700 shadow-deep ring-4 ring-ai-700/40"
          style={{ backfaceVisibility: 'hidden' }}>
          <Caduceus className="text-ink-900" style={{ height: size * 0.62 }} />
        </div>
        <div className="absolute inset-0 flex items-center justify-center rounded-full bg-gradient-to-br from-ai-700 via-ai-500 to-ai-200 shadow-deep ring-4 ring-ai-700/40"
          style={{ transform: 'rotateY(180deg)', backfaceVisibility: 'hidden' }}>
          <Caduceus className="text-ink-900" style={{ height: size * 0.62 }} />
        </div>
      </div>
    </div>
  );
}

export function Logo({ light = false, compact = false }: { light?: boolean; compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`flex h-11 w-11 items-center justify-center rounded-xl shadow-lg ${light ? 'bg-ai-100 text-ink-900' : 'bg-ink-900 text-ai-200'}`}>
        <Caduceus style={{ height: 26 }} />
      </div>
      {!compact && (
        <div className="leading-none">
          <p className={`font-display text-xl font-bold ${light ? 'text-paper-50' : 'text-ink-900'}`}>DoctorOS</p>
          <p className={`mt-1 font-label text-[10px] font-semibold uppercase tracking-[0.28em] ${light ? 'text-ai-200' : 'text-brand-700'}`}>AI Clinic</p>
        </div>
      )}
    </div>
  );
}
