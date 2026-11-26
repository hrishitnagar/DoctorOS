import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { appointmentApi } from '@/api/appointmentApi';
import { getErrorMessage } from '@/api/client';
import { Button, Input, Modal, Select, StatusBadge, Textarea } from '@/components/ui/ui';
import type { Appointment, UpdatableStatus } from '@/types';
import { formatDateTime, localToIso } from '@/utils/formatDate';

/** Change status buttons. Backend only allows updating "scheduled" appointments. */
export function StatusUpdater({ appointment, onChanged }: { appointment: Appointment; onChanged: (a: Appointment) => void }) {
  const [busy, setBusy] = useState<UpdatableStatus | null>(null);
  const set = async (s: UpdatableStatus) => {
    setBusy(s);
    try { const a = await appointmentApi.updateStatus(appointment.id, s); toast.success(`Marked ${s}`); onChanged(a); }
    catch (e) { toast.error(getErrorMessage(e)); } finally { setBusy(null); }
  };
  return (
    <div className="space-y-3 rounded-xl bg-slate-50 p-4">
      <p className="text-sm font-semibold">Appointment #{appointment.id} · {formatDateTime(appointment.appointment_datetime)} · {appointment.duration_minutes} min</p>
      <div className="flex items-center gap-2 text-sm">Status: <StatusBadge status={appointment.status} /></div>
      {appointment.status === 'scheduled' ? (
        <div className="flex flex-wrap gap-2">
          <Button size="sm" variant="success" loading={busy === 'completed'} onClick={() => set('completed')}>Completed</Button>
          <Button size="sm" variant="secondary" loading={busy === 'cancelled'} onClick={() => set('cancelled')}>Cancelled</Button>
          <Button size="sm" variant="secondary" loading={busy === 'no-show'} onClick={() => set('no-show')}>No-show</Button>
        </div>
      ) : <p className="text-xs text-slate-500">Only scheduled appointments can be updated.</p>}
    </div>
  );
}

interface Form { when: string; duration: string; reason: string }

export function AppointmentModal({ open, onClose, patientId, onCreated }: { open: boolean; onClose: () => void; patientId: number; onCreated: () => void }) {
  const [created, setCreated] = useState<Appointment | null>(null);
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<Form>({ defaultValues: { duration: '30' } });
  const close = () => { setCreated(null); reset(); onClose(); };

  const submit = async (f: Form) => {
    try {
      const a = await appointmentApi.create({
        patient_id: patientId, appointment_datetime: localToIso(f.when),
        duration_minutes: Number(f.duration) as 15 | 30 | 60, reason: f.reason.trim() || null,
      });
      toast.success('Appointment scheduled');
      setCreated(a); onCreated();
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  return (
    <Modal open={open} onClose={close} title={created ? 'Appointment created' : 'New Appointment'}>
      {created ? (
        <div className="space-y-4">
          <StatusUpdater appointment={created} onChanged={(a) => { setCreated(a); onCreated(); }} />
          <div className="flex justify-end"><Button onClick={close}>Done</Button></div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(submit)} noValidate className="space-y-4">
          <Input label="Date & time *" type="datetime-local" hint="Must be in the future" error={errors.when?.message}
            {...register('when', { required: 'Date and time are required', validate: (v) => new Date(v).getTime() > Date.now() || 'Must be in the future' })} />
          <Select label="Duration" {...register('duration')}><option value="15">15 minutes</option><option value="30">30 minutes</option><option value="60">60 minutes</option></Select>
          <Textarea label="Reason for visit" maxLength={1000} {...register('reason')} />
          <div className="flex justify-end gap-2"><Button type="button" variant="secondary" onClick={close}>Cancel</Button><Button type="submit" loading={isSubmitting}>Schedule</Button></div>
        </form>
      )}
    </Modal>
  );
}
