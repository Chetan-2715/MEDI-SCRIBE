
import React from 'react';
import { Settings, LogOut, Shield, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

const Profile: React.FC = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleDeleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone and all your data (prescriptions, medicines) will be lost.')) {
      try {
        if (token) {
          await authService.deleteAccount(token);
          logout();
          navigate('/login');
        }
      } catch (error) {
        console.error("Failed to delete account:", error);
        alert("Failed to delete account. Please try again.");
      }
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-800 dark:text-white">My Profile</h2>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Profile Card */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 w-full md:w-80 flex flex-col items-center text-center">
          <div className="w-24 h-24 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden mb-4">
            <img src={`https://ui-avatars.com/api/?name=${user?.name || 'User'}&background=0d9488&color=fff`} alt="Profile" className="w-full h-full object-cover" />
          </div>
          <h3 className="text-xl font-bold text-slate-800 dark:text-white">{user?.name || 'User'}</h3>
          <p className="text-slate-500 dark:text-slate-400 mb-6">{user?.email}</p>

          <div className="w-full space-y-3">
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors font-medium"
            >
              <LogOut size={18} />
              Logout
            </button>

            <button
              onClick={handleDeleteAccount}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors font-medium"
            >
              <Trash2 size={18} />
              Delete Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
