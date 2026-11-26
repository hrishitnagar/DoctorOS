import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { ChevronLeft, ChevronRight, Search, UserPlus, Users } from 'lucide-react';
import { getErrorMessage } from '@/api/client';
import { patientApi } from '@/api/patientApi';
import { Badge, Button, Card, EmptyState, ErrorState, Input, Modal, PageHeader, Select, SkeletonList } from '@/components/ui/ui';
import { useApi } from '@/hooks/useApi';
import { IMG } from '@/utils/assets';
import type { PatientCreate } from '@/types';
import { formatDate } from '@/utils/formatDate';

interface Form { name: string; dob: string; gender: string; phone: string; email: string; address: string; blood_group: string; emergency_contact: string }
const blank = (v: string): string | null => (v.trim() === '' ? null : v.trim());

export default function PatientListPage() {
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState('');
  const [debounced, setDebounced] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [open, setOpen] = useState(params.get('create') === '1');

  useEffect(() => { const t = setTimeout(() => { setDebounced(search); setPage(0); }, 350); return () => clearTimeout(t); }, [search]);
  const { data, loading, error, reload } = useApi(() => patientApi.list({ search: debounced, skip: page * pageSize, limit: pageSize }), [debounced, page, pageSize]);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<Form>();
  const close = () => { setOpen(false); reset(); if (params.get('create')) { params.delete('create'); setParams(params, { replace: true }); } };

  const onCreate = async (f: Form) => {
    const body: PatientCreate = {
      name: f.name.trim(), dob: blank(f.dob), gender: blank(f.gender), phone: blank(f.phone), email: blank(f.email),
      address: blank(f.address), blood_group: blank(f.blood_group), emergency_contact: blank(f.emergency_contact),
    };
    try {
      const p = await patientApi.create(body);
      toast.success('Patient created');
      navigate(`/patients/${p.id}`);
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const total = data?.total ?? 0;
  const pages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div>
      <PageHeader title="Patients" subtitle="Search, open and register patients" art={IMG.brain}
        actions={<Button onClick={() => setOpen(true)}><UserPlus className="h-4 w-4" />Create Patient</Button>} />
      <Card>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden />
          <input aria-label="Search patients by name" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name…"
            className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-9 pr-3 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" />
        </div>
        {loading ? <SkeletonList rows={5} /> : error ? <ErrorState message={error} onRetry={reload} />
          : !data || data.items.length === 0 ? (
            <EmptyState icon={<Users className="h-7 w-7" />}
              text={debounced ? 'No patients match your search.' : 'No patients yet. Create your first patient to get started.'}
              action={!debounced && <Button onClick={() => setOpen(true)}>Create Patient</Button>} />
          ) : (
            <>
              <div className="hidden overflow-x-auto md:block">
                <table className="w-full text-left text-sm">
                  <thead><tr className="bg-slate-50 font-label text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500">
                    {['Patient ID', 'Name', 'DOB', 'Gender', 'Phone', 'Email'].map((h) => <th key={h} className="px-4 py-3 font-semibold">{h}</th>)}
                  </tr></thead>
                  <tbody>
                    {data.items.map((p, i) => (
                      <tr key={p.id} tabIndex={0} onClick={() => navigate(`/patients/${p.id}`)} onKeyDown={(e) => e.key === 'Enter' && navigate(`/patients/${p.id}`)}
                        className={`cursor-pointer transition hover:bg-brand-50 ${i % 2 ? 'bg-slate-50/60' : ''}`}>
                        <td className="px-4 py-3 font-mono text-xs text-brand-700">{p.patient_uid}</td>
                        <td className="px-4 py-3 font-semibold text-slate-900">{p.name}</td>
                        <td className="px-4 py-3">{formatDate(p.dob)}</td>
                        <td className="px-4 py-3">{p.gender ?? '—'}</td>
                        <td className="px-4 py-3 font-mono text-xs">{p.phone ?? '—'}</td>
                        <td className="px-4 py-3">{p.email ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <ul className="space-y-3 md:hidden">
                {data.items.map((p) => (
                  <li key={p.id}><button onClick={() => navigate(`/patients/${p.id}`)} className="w-full rounded-xl border border-slate-200 bg-white p-4 text-left">
                    <p className="font-semibold">{p.name}</p><Badge tone="teal">{p.patient_uid}</Badge>
                    <p className="mt-1 text-xs text-slate-500">{formatDate(p.dob)} · {p.gender ?? '—'} · {p.phone ?? '—'}</p>
                  </button></li>
                ))}
              </ul>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-600">
                <span>{total} patient{total === 1 ? '' : 's'} · page {page + 1} of {pages}</span>
                <div className="flex items-center gap-2">
                  <select aria-label="Page size" value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(0); }} className="rounded-lg border border-slate-200 bg-white px-2 py-1.5">
                    {[10, 20, 50].map((n) => <option key={n} value={n}>{n} / page</option>)}
                  </select>
                  <Button variant="secondary" size="sm" disabled={page === 0} onClick={() => setPage((p) => p - 1)} aria-label="Previous page"><ChevronLeft className="h-4 w-4" />Prev</Button>
                  <Button variant="secondary" size="sm" disabled={page + 1 >= pages} onClick={() => setPage((p) => p + 1)} aria-label="Next page">Next<ChevronRight className="h-4 w-4" /></Button>
                </div>
              </div>
            </>
          )}
      </Card>

      <Modal open={open} onClose={close} title="Create Patient" wide>
        <form onSubmit={handleSubmit(onCreate)} noValidate className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2"><Input label="Full name *" error={errors.name?.message}
            {...register('name', { required: 'Name is required', minLength: { value: 2, message: 'At least 2 characters' }, maxLength: { value: 150, message: 'Max 150 characters' } })} /></div>
          <Input label="Date of birth" type="date" {...register('dob')} />
          <Select label="Gender" {...register('gender')}><option value="">Select…</option><option>Male</option><option>Female</option><option>Other</option></Select>
          <Input label="Phone" inputMode="tel" hint="7–15 digits" error={errors.phone?.message}
            {...register('phone', { validate: (v) => v === '' || /^\+?\d{7,15}$/.test(v.replace(/[\s-]/g, '')) || 'Phone must be 7–15 digits' })} />
          <Input label="Email" type="email" error={errors.email?.message}
            {...register('email', { validate: (v) => v === '' || /^\S+@\S+\.\S+$/.test(v) || 'Enter a valid email' })} />
          <Select label="Blood group" {...register('blood_group')}><option value="">Select…</option>{['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map((b) => <option key={b}>{b}</option>)}</Select>
          <Input label="Emergency contact" placeholder="Name - phone" {...register('emergency_contact', { maxLength: { value: 100, message: 'Max 100 characters' } })} error={errors.emergency_contact?.message} />
          <div className="sm:col-span-2"><Input label="Address" {...register('address')} /></div>
          <div className="flex justify-end gap-2 sm:col-span-2">
            <Button type="button" variant="secondary" onClick={close}>Cancel</Button>
            <Button type="submit" loading={isSubmitting}>Create Patient</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
