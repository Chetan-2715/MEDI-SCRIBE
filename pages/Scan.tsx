import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Upload, Loader2, X } from 'lucide-react';
import { analyzePrescription } from '../services/geminiService';
import { savePrescription } from '../services/storageService';
import { v4 as uuidv4 } from 'uuid';
import { ProcessingState } from '../types';

const Scan: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [state, setState] = useState<ProcessingState>({ status: 'idle' });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const processImage = async () => {
    if (!preview) return;

    setState({ status: 'processing' });

    try {
      const result = await analyzePrescription(preview);

      const newPrescription = {
        id: uuidv4(),
        imageUrl: preview,
        medicines: result.medicines || [],
        doctorName: result.doctorName || 'Unknown',
        patientName: result.patientName || 'User',
        createdAt: new Date().toISOString()
      };

      savePrescription(newPrescription);
      setState({ status: 'complete' });
      navigate(`/prescription/${newPrescription.id}`);

    } catch (error) {
      console.error(error);
      setState({ status: 'error', message: 'Failed to analyze prescription. Please try again.' });
    }
  };

  return (
    <div className="h-full flex flex-col">
      <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6">Scan Prescription</h2>

      {state.status === 'processing' ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8 bg-slate-50 dark:bg-slate-900 overflow-hidden relative">

          <div className="w-full max-w-lg mb-8 relative">
            <svg viewBox="0 0 500 150" className="w-full h-full text-teal-600 dark:text-teal-400 drop-shadow-lg">
              <polyline
                points="0,75 100,75 120,45 140,75 160,75 180,110 200,20 220,130 240,75 260,75 280,55 320,75 500,75"
                fill="none"
                stroke="currentColor"
                strokeWidth="6"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="animate-ekg"
              />
            </svg>
            <div className="absolute inset-0 bg-linear-to-r from-slate-50 via-transparent to-slate-50 dark:from-slate-900 dark:to-slate-900 opacity-20"></div>
          </div>

          <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-2 animate-pulse">Analyzing Prescription...</h3>
          <p className="text-slate-500 dark:text-slate-400 max-w-md">
            Our AI is deciphering the handwriting and extracting structured data.
            <br /><span className="text-xs opacity-70 mt-2 block">Powered by Gemini 1.5 Flash</span>
          </p>
        </div>
      ) : (
        <>
          <div className="flex-1 bg-white rounded-2xl border-2 border-dashed border-slate-300 flex flex-col items-center justify-center p-6 relative overflow-hidden group">
            {preview ? (
              <>
                <img src={preview} alt="Preview" className="max-h-full max-w-full object-contain z-10" />
                <button
                  onClick={() => setPreview(null)}
                  className="absolute top-4 right-4 bg-white/90 p-2 rounded-full shadow-lg z-20 hover:bg-red-50 text-slate-700 hover:text-red-500"
                >
                  <X size={20} />
                </button>
              </>
            ) : (
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-teal-50 text-teal-600 rounded-full flex items-center justify-center mx-auto">
                  <Camera size={32} />
                </div>
                <div>
                  <p className="text-lg font-semibold text-slate-700">Take a photo</p>
                  <p className="text-sm text-slate-400">or upload from gallery</p>
                </div>
              </div>
            )}

            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              className="absolute inset-0 opacity-0 cursor-pointer z-0"
              onChange={handleFileChange}
              disabled={!!preview}
            />
          </div>

          <div className="mt-6 space-y-3">
            {preview ? (
              <button
                onClick={processImage}
                className="w-full bg-teal-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-teal-600/20 hover:bg-teal-700 transition-colors flex items-center justify-center gap-2"
              >
                Analyze Prescription
              </button>
            ) : (
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full bg-slate-900 text-white py-4 rounded-xl font-bold text-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2"
              >
                <Upload size={20} />
                Select Image
              </button>
            )}

            {state.status === 'error' && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm text-center">
                {state.message}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Scan;
