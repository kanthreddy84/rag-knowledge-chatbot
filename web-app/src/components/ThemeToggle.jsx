import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export const ThemeToggle = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg transition-all duration-200 hover:bg-datafacz-gray-800 dark:hover:bg-datafacz-gray-700 text-datafacz-gray-400 hover:text-datafacz-orange focus:outline-none focus:ring-2 focus:ring-datafacz-orange"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Sun size={20} className="text-datafacz-gray-400" />
      ) : (
        <Moon size={20} className="text-datafacz-gray-600" />
      )}
    </button>
  );
};
