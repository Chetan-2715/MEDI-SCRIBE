import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className={`
        p-2 rounded-full transition-colors duration-200
        ${theme === 'dark'
                    ? 'bg-slate-800 text-teal-400 hover:bg-slate-700'
                    : 'bg-teal-50 text-teal-600 hover:bg-teal-100'
                }
      `}
            aria-label="Toggle theme"
        >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
    );
};
