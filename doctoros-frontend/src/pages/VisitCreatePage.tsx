import { Link, useNavigate, useParams } from 'react-router-dom';
import { useFieldArray, useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { ArrowLeft, Pill, Plus, Trash2 } from 'lucide-react';
import { getErrorMessage } from '@/api/client';
import { patientApi } from '@/api/patientApi';
import { visitApi } from '@/api/visitApi';
import { Button, Card, ErrorState, Input, PageHeader, Skeleton, Textarea } from '@/components/ui/ui';
import { useApi } from '@/hooks/useApi';
import { IMG } from '@/utils/assets';
import type { MedicationCreate, VisitCreate } from '@/types';
import { localToIso } from '@/utils/formatDate';

interface Form {
  appointment_id: string; visit_date: string; observations: string; diagnosis: string; prescription_notes: string;
  medications: { drug: string; dose: string; frequency: string; duration: string; instructions: string }[];
}
const nul = (v: string): string | null => (v.trim() ? v.trim() : null);
const nowLocal = (): string => { const d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 16); };

export default function VisitCreatePage() {
  const patientId = Number(useParams().id);
  const navigate = useNavigate();
  const patient = useApi(() => patientApi.get(patientId), [patientId]);
  const { register, control, handleSubmit, formState: { errors, isSubmitting } } = useForm<Form>({
    defaultValues: { visit_date: nowLocal(), medications: [] },
  });
  const { fields, append, remove } = useFieldArray({ control, name: 'medications' });

  const onSubmit = async (f: Form) => {
    const medications: MedicationCreate[] = f.medications.map((m) => ({
      drug: m.drug.trim(), dose: nul(m.dose), frequency: nul(m.frequency), duration: nul(m.duration), instructions: nul(m.instructions),
    }));
    const body: VisitCreate = {
      patient_id: patientId, appointment_id: f.appointment_id ? Number(f.appointment_id) : null,
      observations: nul(f.observations), diagnosis: nul(f.diagnosis), prescription_notes: nul(f.prescription_notes),
      visit_date: localToIso(f.visit_date), medications,
    };
    try {
      await visitApi.create(body);
      toast.success('Visit recorded');
      navigate(`/patients/${patientId}`);
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  return (
    <div>
      <Link to={`/patients/${patientId}`} className="mb-3 inline-flex items-center gap-1 text-sm font-semibold text-brand-700 hover:underline"><ArrowLeft className="h-4 w-4" />Back to patient</Link>
      <PageHeader title="Record Visit" art={IMG.heart} subtitle={patient.data ? `${patient.data.name} · ${patient.data.patient_uid}` : undefined} />
      {patient.loading ? <Skeleton className="h-64" /> : patient.error ? <ErrorState message={patient.error} onRetry={patient.reload} /> : (
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
          <Card className="grid gap-4 sm:grid-cols-2">
            <Input label="Visit date & time *" type="datetime-local" error={errors.visit_date?.message} {...register('visit_date', { required: 'Visit date is required' })} />
            <Input label="Appointment ID (optional)" type="number" min={1} hint="Link this visit to an appointment" {...register('appointment_id')} />
            <div className="sm:col-span-2"><Textarea label="Observations" {...register('observations')} /></div>
            <Textarea label="Diagnosis" {...register('diagnosis')} />
            <Textarea label="Prescription notes" {...register('prescription_notes')} />
          </Card>

          <Card>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="flex items-center gap-2 font-bold text-slate-900"><Pill className="h-5 w-5 text-brand-600" />Medications</h2>
              <Button type="button" variant="secondary" size="sm" onClick={() => append({ drug: '', dose: '', frequency: '', duration: '', instructions: '' })}><Plus className="h-4 w-4" />Add Medication</Button>
            </div>
            {fields.length === 0 && <p className="text-sm text-slate-500">No medications added.</p>}
            <div className="space-y-4">
              {fields.map((field, i) => (
                <div key={field.id} className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-4">
                  <div className="sm:col-span-2"><Input label="Drug *" error={errors.medications?.[i]?.drug?.message}
                    {...register(`medications.${i}.drug`, { required: 'Drug name is required', maxLength: { value: 200, message: 'Max 200 characters' } })} /></div>
                  <Input label="Dose" className="font-mono" placeholder="500mg" {...register(`medications.${i}.dose`)} />
                  <Input label="Frequency" placeholder="Twice daily" {...register(`medications.${i}.frequency`)} />
                  <Input label="Duration" placeholder="7 days" {...register(`medications.${i}.duration`)} />
                  <div className="sm:col-span-2"><Input label="Instructions" {...register(`medications.${i}.instructions`)} /></div>
                  <div className="flex items-end justify-end"><Button type="button" variant="ghost" size="sm" onClick={() => remove(i)} aria-label={`Remove medication ${i + 1}`}><Trash2 className="h-4 w-4 text-rust-500" />Remove</Button></div>
                </div>
              ))}
            </div>
          </Card>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="secondary" onClick={() => navigate(`/patients/${patientId}`)}>Cancel</Button>
            <Button type="submit" loading={isSubmitting}>Save Visit</Button>
          </div>
        </form>
      )}
    </div>
  );
}
