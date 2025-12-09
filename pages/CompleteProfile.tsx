import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Loader2, ArrowRight } from 'lucide-react';
import { authService } from '../services/authService';
import { useAuth } from '../context/AuthContext';

const CompleteProfile: React.FC = () => {
    const navigate = useNavigate();
    const { user, login } = useAuth();
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;

        setLoading(true);
        setError('');

        try {
            if (!user?.id) throw new Error("User not authenticated");
            const updatedUser = await authService.updateProfile(user.id, name);
            // Update local context/storage with new user data
            if (user && updatedUser) {
                // We need to re-login to update context or just update user part
                // But authService.updateProfile returns User object
                // We can mock a login or update context if exposed.
                // Since login() takes AuthResponse, we construct it.
                // Ideally updateAuth() would be better but login works if token persists.
                const token = localStorage.getItem('auth_token') || '';
                login({ user: updatedUser, token });
            }
            navigate('/dashboard');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-6">
            <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 bg-teal-600 rounded-xl flex items-center justify-center text-white mb-4">
                        <User size={28} />
                    </div>
                    <h1 className="text-2xl font-bold text-slate-800">Complete Profile</h1>
                    <p className="text-slate-500">Please provide your full name to continue</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-6 text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                        <input
                            type="text"
                            required
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="block w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
                            placeholder="John Doe"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-teal-600 text-white py-3 rounded-xl font-bold hover:bg-teal-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loading ? <Loader2 className="animate-spin" size={20} /> : 'Save & Continue'}
                        {!loading && <ArrowRight size={18} />}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CompleteProfile;
