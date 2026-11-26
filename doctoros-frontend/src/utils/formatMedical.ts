/** Medical values are shown exactly as returned by the backend. Never round or truncate. */
export const showValue = (v: string | number | null | undefined): string =>
  v === null || v === undefined || v === '' ? '—' : String(v);

export type LabFlag = 'normal' | 'abnormal' | 'unknown';

/** Parses ranges such as "12.0-17.5" and flags values outside it (display only, no clinical advice). */
export function labFlag(value: number, range: string | null): LabFlag {
  if (!range) return 'unknown';
  const m = range.match(/^\s*(-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)\s*$/);
  if (!m) return 'unknown';
  const lo = parseFloat(m[1]);
  const hi = parseFloat(m[2]);
  return value < lo || value > hi ? 'abnormal' : 'normal';
}
