
import React from 'react';
import { Pill, Clock, Calendar, Info, Syringe, Droplet, FlaskConical, Download } from 'lucide-react';
import { Medicine } from '../types';

interface MedicineCardProps {
  medicine: Medicine;
  onAddToCalendar?: () => void;
}

const TargetIcon = ({ size = 20, className = "" }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    width={size}
    height={size}
    className={className}
  >
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
    <path d="M22 2 12 12" />
  </svg>
);

const SyrupIcon = ({ size = 20, className = "" }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    width={size}
    height={size}
    className={className}
  >
    <path d="M9 3h6v4H9z" />
    <path d="M12 3v4" />
    <path d="M15 7h-6L5 13a4 4 0 0 0 4 4h6a4 4 0 0 0 4-4l-4-6Z" />
    <path d="M14 13h-4" />
  </svg>
);

const OintmentIcon = ({ size = 20, className = "" }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    width={size}
    height={size}
    className={className}
  >
    <path d="m14 2 4 4L7 17H3v-4L14 2Z" />
    <path d="m10 6 4 4" />
    <path d="m16 22 4-4" />
    <path d="M2 22h4" />
  </svg>
);

const MedicineCard: React.FC<MedicineCardProps> = ({ medicine, onAddToCalendar }) => {

  const getMedicineIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'injection':
        return <Syringe size={20} />;
      case 'syrup':
        return <SyrupIcon size={20} />;
      case 'ointment':
      case 'cream':
      case 'gel':
        return <OintmentIcon size={20} />;
      case 'tablet':
      default:
        return <Pill size={20} />;
    }
  };

  const getMedicineTypeLabel = (type?: string) => {
    if (!type) return 'Medicine';
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  const getTypeColor = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'injection': return 'bg-red-50 text-red-700';
      case 'syrup': return 'bg-amber-50 text-amber-700';
      case 'ointment':
      case 'cream':
      case 'gel':
        return 'bg-purple-50 text-purple-700';
      default: return 'bg-blue-50 text-blue-700';
    }
  };

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-100 mb-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="text-lg font-bold text-slate-800">{medicine.medicine_name}</h3>
          <div className="flex gap-2 mt-1">
            {/* Removed badge as duplicate info */}
            {medicine.medicine_type && (
              <span className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium border border-opacity-20 ${getTypeColor(medicine.medicine_type).replace('bg-', 'border-').replace('text-', 'text-slate-500 ')}`}>
                {getMedicineTypeLabel(medicine.medicine_type)}
              </span>
            )}
          </div>
        </div>
        <div className={`p-2 rounded-lg ${getTypeColor(medicine.medicine_type)}`}>
          {getMedicineIcon(medicine.medicine_type)}
        </div>
      </div>

      <p className="text-slate-500 text-sm mb-4 leading-relaxed">
        {medicine.description}
      </p>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-slate-50 p-2 rounded-lg flex items-center gap-2">
          <Clock size={16} className="text-slate-400" />
          <div>
            <p className="text-xs text-slate-400">Dosage</p>
            <p className="text-sm font-semibold text-slate-700">{medicine.dosage_pattern}</p>
          </div>
        </div>
        <div className="bg-slate-50 p-2 rounded-lg flex items-center gap-2">
          <Calendar size={16} className="text-slate-400" />
          <div>
            <p className="text-xs text-slate-400">Duration</p>
            <p className="text-sm font-semibold text-slate-700">{medicine.duration_days} Days</p>
          </div>
        </div>
      </div>

      <div className="space-y-2 mb-4 bg-slate-50 p-3 rounded-lg border border-slate-100">
        <div className="flex items-start gap-2 text-xs text-slate-600">
          <Info size={14} className="mt-0.5 text-blue-500 shrink-0" />
          <p><span className="font-bold text-slate-700 uppercase tracking-wide text-[10px]">Usage:</span> {medicine.instructions || 'As advised'}</p>
        </div>
        <div className="flex items-start gap-2 text-xs text-slate-600">
          <TargetIcon size={14} className="mt-0.5 text-purple-500 shrink-0" />
          <p><span className="font-bold text-slate-700 uppercase tracking-wide text-[10px]">Purpose:</span> {medicine.purpose || 'General Health'}</p>
        </div>
      </div>

      {onAddToCalendar && (
        <button
          onClick={onAddToCalendar}
          className="w-full py-2 bg-white border border-teal-600 text-teal-600 rounded-lg text-sm font-semibold hover:bg-teal-50 transition-colors flex items-center justify-center gap-2 group"
        >
          <Calendar size={16} className="group-hover:hidden" />
          <Download size={16} className="hidden group-hover:block" />
          Add to Google Calendar
        </button>
      )}
    </div>
  );
};

export default MedicineCard;
