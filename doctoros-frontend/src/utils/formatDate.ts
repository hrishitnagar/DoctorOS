const toDate = (v: string): Date => new Date(v.length === 10 ? `${v}T00:00:00` : v);

/** "MMM DD, YYYY" */
export function formatDate(v?: string | null): string {
  if (!v) return '—';
  const d = toDate(v);
  if (Number.isNaN(d.getTime())) return v;
  return d.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
}

export function formatDateTime(v?: string | null): string {
  if (!v) return '—';
  const d = toDate(v);
  if (Number.isNaN(d.getTime())) return v;
  return `${formatDate(v)} · ${d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
}

export function calcAge(dob?: string | null): string {
  if (!dob) return '—';
  const d = toDate(dob);
  if (Number.isNaN(d.getTime())) return '—';
  const now = new Date();
  let age = now.getFullYear() - d.getFullYear();
  const m = now.getMonth() - d.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < d.getDate())) age -= 1;
  return `${age} yrs`;
}

/** value of <input type="datetime-local"> -> ISO string with timezone (backend requires tz) */
export function localToIso(local: string): string {
  return new Date(local).toISOString();
}
