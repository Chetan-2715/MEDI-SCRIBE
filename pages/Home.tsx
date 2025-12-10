import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Prescription } from '../types';
import { FileText, ChevronRight, Plus, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Home: React.FC = () => {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);

  const fetchPrescriptions = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/prescriptions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        // Map DB columns to Frontend Types
        const mapped: Prescription[] = data.map((p: any) => ({
          id: p.id,
          imageUrl: p.image_url,
          createdAt: p.created_at,
          doctorName: p.doctor_name,
          patientName: p.patient_name,
          medicines: p.medicines?.map((m: any) => ({ ...m, medicine_name: m.name })) || [] // Handle medicines if joined
        }));
        setPrescriptions(mapped);
      }
    } catch (error) {
      console.error("Failed to fetch prescriptions", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchPrescriptions();
  }, [token]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!token) return;

    if (window.confirm('Are you sure you want to delete this prescription?')) {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/prescriptions/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          setPrescriptions(prev => prev.filter(p => p.id !== id));
        } else {
          alert("Failed to delete");
        }
      } catch (err) {
        console.error("Delete failed", err);
        alert("Failed to delete");
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-linear-to-r from-teal-600 to-teal-500 rounded-2xl p-6 lg:p-10 text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold mb-2">Welcome Back, {user?.name?.split(' ')[0] || "User"}!</h2>
          <p className="opacity-90">You have {prescriptions.length} saved prescriptions.</p>
        </div>
        <button
          onClick={() => navigate('/scan')}
          className="bg-white text-teal-600 px-6 py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 shadow-sm hover:bg-teal-50 transition-colors w-full md:w-auto"
        >
          <Plus size={18} />
          Scan New Prescription
        </button>
      </div>

      <div>
        <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-6">Recent Uploads</h3>

        {loading ? (
          <div className="text-center py-20 text-slate-400">Loading prescriptions...</div>
        ) : prescriptions.length === 0 ? (
          <div className="text-center py-20 bg-white dark:bg-slate-900 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-800">
            <div className="w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
              <FileText size={32} />
            </div>
            <p className="text-slate-600 dark:text-slate-300 font-medium text-lg">No prescriptions yet</p>
            <p className="text-slate-400 mt-1">Tap 'Scan' to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {prescriptions.map((p) => (
              <div
                key={p.id}
                onClick={() => navigate(`/prescription/${p.id}`)}
                className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4 hover:border-teal-500 dark:hover:border-teal-500 hover:shadow-md transition-all cursor-pointer group relative"
              >
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-lg overflow-hidden shrink-0 relative">
                  <img src={p.imageUrl} alt="Prescription" className="w-full h-full object-cover" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-bold text-slate-800 dark:text-white truncate group-hover:text-teal-700 dark:group-hover:text-teal-400 transition-colors">
                    {p.doctorName ? `Dr. ${p.doctorName}` : 'Prescription'}
                  </h4>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    {new Date(p.createdAt).toLocaleDateString()}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {p.medicines.length} Medicines
                  </p>
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    onClick={(e) => handleDelete(e, p.id)}
                    className="p-2 rounded-full text-slate-400 hover:bg-red-50 hover:text-red-500 transition-colors z-10"
                    title="Delete Prescription"
                  >
                    <Trash2 size={18} />
                  </button>

                  <div className="p-2 rounded-full group-hover:bg-teal-50 dark:group-hover:bg-teal-900/30 text-slate-400 group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">
                    <ChevronRight size={20} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
