
import React from 'react';
import { Pill, Clock, Calendar, Info, Syringe, Droplet, FlaskConical, Download } from 'lucide-react';
import { Medicine } from '../types';

interface MedicineCardProps {
  medicine: Medicine;
  onAddToCalendar?: () => void;
}

const MedicineCard: React.FC<MedicineCardProps> = ({ medicine, onAddToCalendar }) => {
  
  const getMedicineIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'injection':
        return <Syringe size={20} />;
      case 'syrup':
        return <Droplet size={20} />;
      case 'ointment':
        return <FlaskConical size={20} />;
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
      case 'ointment': return 'bg-purple-50 text-purple-700';
      default: return 'bg-blue-50 text-blue-700';
    }
  };

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-100 mb-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="text-lg font-bold text-slate-800">{medicine.medicine_name}</h3>
          <div className="flex gap-2 mt-1">
            <span className="inline-block bg-teal-50 text-teal-700 text-xs px-2 py-0.5 rounded-full font-medium">
              {medicine.purpose}
            </span>
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

      <div className="flex items-center gap-2 text-sm text-slate-600 mb-4 bg-orange-50 p-2 rounded border border-orange-100">
        <Info size={16} className="text-orange-500 flex-shrink-0" />
        <span>{medicine.instructions}</span>
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
