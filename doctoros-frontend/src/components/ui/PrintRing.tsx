import { PRINTS } from '@/utils/assets';

/** A rotating 3D ring built from the four anatomy prints. Pure CSS, no canvas. */
export function PrintRing({ width = 120, className = '' }: { width?: number; className?: string }) {
  const height = Math.round(width * 1.27);
  const radius = Math.round(width * 0.82);
  return (
    <div className={`persp ${className}`} style={{ width, height, perspective: 900 }} aria-hidden>
      <div className="ring3d h-full w-full" style={{ transform: 'rotateX(-9deg)' }}>
        <div className="ring3d h-full w-full animate-ring">
          {PRINTS.map((src, i) => (
            <div key={src} className="ring3d-card" style={{ ['--i' as string]: i, ['--r' as string]: `${radius}px` }}>
              <div className="plate h-full"><img src={src} alt="" decoding="async" className="sepia-print h-full w-full rounded-[3px] object-cover" /></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
