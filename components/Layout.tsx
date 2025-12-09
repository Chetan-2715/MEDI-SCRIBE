import React from 'react';
import { Home, PlusCircle, User, Activity } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ThemeToggle } from './ThemeToggle';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const isActive = (path: string) => location.pathname === path;

  const NavItem = ({ path, icon: Icon, label, mobileOnly = false }: any) => (
    <button
      onClick={() => navigate(path)}
      className={`
        ${mobileOnly ? 'lg:hidden' : ''}
        flex-col items-center gap-1
        ${isActive(path)
          ? 'text-teal-600'
          : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
        }
`}
    >
      <Icon size={24} />
      <span className="text-xs font-medium">{label}</span>
    </button>
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col lg:flex-row">

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 transition-colors duration-300">

        {/* Desktop Header */}
        <header className="hidden lg:flex bg-white/80 dark:bg-slate-900/80 backdrop-blur-md px-8 py-4 sticky top-0 z-20 border-b border-slate-200 dark:border-slate-800 justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/dashboard')}>
            <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center text-white font-bold shrink-0">
              <Activity size={20} />
            </div>
            <h1 className="text-xl font-bold text-slate-800 dark:text-white truncate whitespace-nowrap">Medi-Scribe</h1>
          </div>

          <div className="flex items-center gap-6">
            <nav className="flex items-center gap-4">
              <button onClick={() => navigate('/dashboard')} className={`text-sm font-medium transition-colors ${isActive('/dashboard') ? 'text-teal-600 dark:text-teal-400' : 'text-slate-600 dark:text-slate-400 hover:text-teal-600'}`}>Dashboard</button>
              <button onClick={() => navigate('/scan')} className={`text-sm font-medium transition-colors ${isActive('/scan') ? 'text-teal-600 dark:text-teal-400' : 'text-slate-600 dark:text-slate-400 hover:text-teal-600'}`}>Scan</button>
            </nav>

            <div className="flex items-center gap-4 pl-6 border-l border-slate-200 dark:border-slate-700">
              <ThemeToggle />
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-bold text-slate-700 dark:text-white leading-tight">{user?.name?.split(' ')[0] || 'User'}</p>
                </div>
                <div
                  className="w-10 h-10 rounded-full bg-teal-100 dark:bg-teal-900/50 flex items-center justify-center text-teal-700 dark:text-teal-300 font-bold border-2 border-white dark:border-slate-800 shadow-sm cursor-pointer hover:ring-2 hover:ring-teal-500 transition-all"
                  onClick={() => navigate('/profile')}
                >
                  {user?.name?.[0] || 'U'}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Mobile Header */}
        <header className="lg:hidden bg-white dark:bg-slate-900 p-4 sticky top-0 z-10 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
          <div className="flex items-center gap-2" onClick={() => navigate('/dashboard')}>
            <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center text-white font-bold">
              <Activity size={20} />
            </div>
            <h1 className="text-xl font-bold text-slate-800 dark:text-white">Medi-Scribe</h1>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden" onClick={() => navigate('/profile')}>
              <img src={`https://ui-avatars.com/api/?name=${user?.name || 'User'}&background=0d9488&color=fff`} alt="User" className="w-full h-full object-cover" />
            </div >
          </div >
        </header >

        {/* Scrollable Area */}
        < main className="flex-1 overflow-y-auto p-4 lg:p-8" >
          <div className="max-w-7xl mx-auto w-full">
            {children}
          </div>
        </main >
      </div >

      {/* Mobile Bottom Nav */}
      < nav className="lg:hidden fixed bottom-0 w-full bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex justify-around py-3 pb-5 z-20" >
        <NavItem path="/" icon={Home} label="Home" mobileOnly={true} />

        <button
          onClick={() => navigate('/scan')}
          className="flex flex-col items-center gap-1 -mt-8"
        >
          <div className="w-14 h-14 bg-teal-600 rounded-full flex items-center justify-center text-white shadow-lg ring-4 ring-white">
            <PlusCircle size={32} />
          </div>
          <span className="text-xs font-medium text-teal-700">Scan</span>
        </button>

        <NavItem path="/profile" icon={User} label="Profile" mobileOnly={true} />
      </nav >
    </div >
  );
};

export default Layout;
