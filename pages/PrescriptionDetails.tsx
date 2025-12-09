
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPrescriptionById } from '../services/storageService';
import { Prescription, Medicine } from '../types';
import MedicineCard from '../components/MedicineCard';
import { ArrowLeft, User, ExternalLink } from 'lucide-react';

const PrescriptionDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [prescription, setPrescription] = useState<Prescription | null>(null);

  useEffect(() => {
    if (id) {
      const data = getPrescriptionById(id);
      if (data) {
        setPrescription(data);
      } else {
        navigate('/');
      }
    }
  }, [id, navigate]);

  const getTimingConfig = (instructions: string) => {
    const isBeforeFood = instructions.toLowerCase().includes('before') ||
      instructions.toLowerCase().includes('empty stomach');

    // Returns HH:MM in 24h format
    if (isBeforeFood) {
      return { morning: '09:15', afternoon: '13:15', evening: '19:15' };
    } else {
      return { morning: '10:00', afternoon: '15:00', evening: '21:00' };
    }
  };

  const getDoseSlots = (pattern: string) => {
    const p = pattern.toUpperCase().trim();
    // Default fallback
    let slots = ['morning'];

    const tripleMatch = p.match(/(\d+)-(\d+)-(\d+)/);
    if (tripleMatch) {
      slots = [];
      if (parseInt(tripleMatch[1]) > 0) slots.push('morning');
      if (parseInt(tripleMatch[2]) > 0) slots.push('afternoon');
      if (parseInt(tripleMatch[3]) > 0) slots.push('evening');
    } else if (p === 'OD' || p === '1-0-0') {
      slots = ['morning'];
    } else if (p === 'BD' || p === 'BID' || p === '1-0-1') {
      slots = ['morning', 'evening'];
    } else if (p === 'TDS' || p === 'TID' || p === '1-1-1') {
      slots = ['morning', 'afternoon', 'evening'];
    } else if (p === '0-0-1' || p === 'HS') {
      slots = ['evening'];
    } else if (p === '0-1-1') {
      slots = ['afternoon', 'evening'];
    }

    // Ensure we have at least one slot
    if (slots.length === 0) slots = ['morning'];

    return slots;
  };

  const addToGoogleCalendar = (medicine: Medicine) => {
    const times = getTimingConfig(medicine.instructions);
    const slots = getDoseSlots(medicine.dosage_pattern);
    const duration = medicine.duration_days || 1;

    // We pick the first slot time to anchor the recurring event.
    // The description will contain the full details.
    const firstSlot = slots[0] as keyof typeof times;
    const timeStr = times[firstSlot]; // e.g., "10:00"

    const now = new Date();
    // Start tomorrow
    const startDate = new Date(now);
    startDate.setDate(startDate.getDate() + 1);

    // Parse timeStr
    const [hours, minutes] = timeStr.split(':').map(Number);
    startDate.setHours(hours, minutes, 0, 0);
    const endDate = new Date(startDate);
    endDate.setHours(hours, minutes + 15, 0, 0); // 15 min duration

    // Format to UTC string: YYYYMMDDTHHMMSSZ
    const toISOString = (date: Date) => date.toISOString().replace(/-|:|\.\d\d\d/g, "");

    const startUTC = toISOString(startDate);
    const endUTC = toISOString(endDate);

    const title = `Take ${medicine.medicine_name}`;
    const description = `
Medicine: ${medicine.medicine_name}
Type: ${medicine.medicine_type}
Dosage: ${medicine.dosage_pattern} (${slots.join(', ')})
Instructions: ${medicine.instructions}
Purpose: ${medicine.purpose}

Remember to take your medicine!
    `.trim();

    const url = new URL('https://calendar.google.com/calendar/render');
    url.searchParams.append('action', 'TEMPLATE');
    url.searchParams.append('text', title);
    url.searchParams.append('dates', `${startUTC}/${endUTC}`);
    url.searchParams.append('details', description);
    url.searchParams.append('recur', `RRULE:FREQ=DAILY;COUNT=${duration}`);

    window.open(url.toString(), '_blank');
  };

  if (!prescription) return null;

  return (
    <div className="pb-10">
      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center gap-2 text-slate-500 mb-6 hover:text-slate-800 transition-colors"
      >
        <ArrowLeft size={20} />
        Back to Dashboard
      </button>

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Prescription Details</h1>
          <p className="text-slate-500 dark:text-slate-400">Processed on {new Date(prescription.createdAt).toLocaleDateString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content: Medicines */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center shrink-0">
                <User size={24} />
              </div>
              <div>
                <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Doctor</p>
                <p className="font-bold text-lg text-slate-800 dark:text-white">{prescription.doctorName || "Unknown Doctor"}</p>
              </div>
            </div>
            <div className="sm:text-right border-t sm:border-t-0 border-slate-100 dark:border-slate-800 pt-4 sm:pt-0">
              <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Patient</p>
              <p className="font-bold text-lg text-slate-800 dark:text-white">{prescription.patientName || "You"}</p>
            </div>
          </div>

          <h2 className="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            Medicines Found
            <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-sm py-0.5 px-2 rounded-full">{prescription.medicines.length}</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {prescription.medicines.map((med, idx) => (
              <MedicineCard
                key={idx}
                medicine={med}
                onAddToCalendar={() => addToGoogleCalendar(med)}
              />
            ))}
          </div>
        </div>

        {/* Sidebar: Image */}
        <div className="lg:col-span-1">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm sticky top-24">
            <h3 className="text-sm font-bold text-slate-400 uppercase mb-4 tracking-wider">Original Scan</h3>
            <div className="rounded-lg overflow-hidden border border-slate-100 bg-slate-50 relative group cursor-pointer" onClick={() => window.open(prescription.imageUrl, '_blank')}>
              <img src={prescription.imageUrl} alt="Original" className="w-full h-auto object-cover" />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                <ExternalLink className="text-white drop-shadow-md" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrescriptionDetails;
