import React, { useState } from 'react';
import { Upload, Loader2, CheckCircle, AlertTriangle, XCircle, Search, RefreshCw } from 'lucide-react';
import { medicineService, VerificationResult } from '../services/medicineService';
import { useAuth } from '../context/AuthContext';

interface Props {
    prescriptionId: string;
}

const MedicineVerifier: React.FC<Props> = ({ prescriptionId }) => {
    const { token } = useAuth();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState<VerificationResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
            setResult(null);
            setError(null);
        }
    };

    const handleVerify = async () => {
        if (!selectedFile || !token) return;

        setAnalyzing(true);
        setError(null);

        try {
            const data = await medicineService.verifyMedicine(selectedFile, prescriptionId, token);
            setResult(data);
        } catch (err: any) {
            console.error(err);
            setError(err.message || 'Verification failed. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    const reset = () => {
        setSelectedFile(null);
        setPreviewUrl(null);
        setResult(null);
        setError(null);
    };

    return (
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 mt-6 relative z-10">
            <div className="flex items-center gap-2 mb-4">
                <div className="bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 p-2 rounded-lg">
                    <Search size={20} />
                </div>
                <div>
                    <h3 className="font-bold text-slate-900 dark:text-white">Verify Tablet</h3>
                    <p className="text-xs text-slate-500">Check if a medicine matches this prescription</p>
                </div>
            </div>

            {!selectedFile ? (
                <div className="border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl p-6 text-center hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer relative">
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <Upload className="mx-auto text-slate-400 mb-2" size={24} />
                    <p className="text-sm text-slate-600 dark:text-slate-300 font-medium">Click to upload tablet image</p>
                    <p className="text-xs text-slate-400 mt-1">Supports JPG, PNG</p>
                </div>
            ) : (
                <div className="space-y-4">
                    <div className="relative rounded-lg overflow-hidden h-40 bg-slate-100 dark:bg-slate-800">
                        <img src={previewUrl!} alt="Tablet" className="w-full h-full object-contain" />
                        <button
                            onClick={reset}
                            className="absolute top-2 right-2 bg-white/90 dark:bg-black/50 text-slate-600 dark:text-slate-200 p-1.5 rounded-full hover:bg-red-50 hover:text-red-500 transition"
                            title="Remove image"
                        >
                            <RefreshCw size={16} />
                        </button>
                    </div>

                    {!result && !analyzing && (
                        <button
                            onClick={handleVerify}
                            className="w-full py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                        >
                            <Search size={18} /> Verify Medicine
                        </button>
                    )}

                    {analyzing && (
                        <div className="text-center py-6 bg-slate-50 dark:bg-slate-800/50 rounded-lg flex flex-col items-center justify-center">
                            <div className="relative mb-3">
                                <div className="absolute inset-0 bg-purple-200 dark:bg-purple-900 rounded-full animate-ping opacity-75"></div>
                                <div className="relative bg-white dark:bg-slate-800 p-3 rounded-full shadow-sm border border-purple-100 dark:border-purple-900/50">
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        className="w-8 h-8 text-purple-600 animate-bounce"
                                    >
                                        <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z" />
                                        <path d="m8.5 8.5 7 7" />
                                    </svg>
                                </div>
                            </div>
                            <p className="text-sm font-bold text-slate-700 dark:text-slate-200">Analyzing molecular composition...</p>
                            <p className="text-xs text-slate-500 mt-1">Comparing with your prescription</p>
                        </div>
                    )}

                    {error && (
                        <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg flex items-start gap-2">
                            <XCircle size={16} className="mt-0.5 shrink-0" />
                            {error}
                        </div>
                    )}

                    {result && (
                        <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                            {/* Status Header */}
                            <div className={`
                 p-3 rounded-lg flex items-center gap-3 mb-3
                 ${result.status === 'prescribed' ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : ''}
                 ${result.status === 'replacement' ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400' : ''}
                 ${result.status === 'not_prescribed' ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400' : ''}
               `}>
                                {result.status === 'prescribed' && <CheckCircle className="shrink-0" />}
                                {result.status === 'replacement' && <AlertTriangle className="shrink-0" />}
                                {result.status === 'not_prescribed' && <XCircle className="shrink-0" />}

                                <div>
                                    <p className="font-bold capitalize">
                                        {result.status.replace('_', ' ')}
                                    </p>
                                    <p className="text-xs opacity-90">
                                        {result.status === 'prescribed' && 'Match found in prescription'}
                                        {result.status === 'replacement' && 'Suitable alternative identified'}
                                        {result.status === 'not_prescribed' && 'Dangerous / mismatch'}
                                    </p>
                                </div>
                            </div>

                            {/* Details */}
                            <div className="space-y-3 text-sm text-slate-700 dark:text-slate-300">
                                <div>
                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Identified As</p>
                                    <p className="font-semibold text-base">{result.identified_medicine_name}</p>
                                </div>

                                {result.replacement_for && (
                                    <div className="bg-amber-50 dark:bg-amber-900/10 p-2 rounded border border-amber-100 dark:border-amber-800/30">
                                        <p className="text-xs text-amber-800 dark:text-amber-300">
                                            <span className="font-bold">Potential replacement for:</span> {result.replacement_for}
                                        </p>
                                    </div>
                                )}

                                <div>
                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Purpose</p>
                                    <p>{result.purpose}</p>
                                </div>

                                <div>
                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Explanation</p>
                                    <p className="bg-slate-50 dark:bg-slate-800 p-2 rounded text-slate-600 dark:text-slate-400">
                                        {result.explanation}
                                    </p>
                                </div>

                                {result.status !== 'prescribed' && (
                                    <div className="flex gap-2 items-start mt-2 text-xs text-slate-500 italic">
                                        <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                                        Always consult your doctor before taking new medication.
                                    </div>
                                )}
                            </div>

                            <button
                                onClick={reset}
                                className="w-full mt-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-600 hover:bg-slate-50 transition-colors"
                            >
                                Verify Another
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default MedicineVerifier;
