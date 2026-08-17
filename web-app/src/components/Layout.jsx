import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import clsx from 'clsx';

export const Layout = ({ children, sidebar, header }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-datafacz-dark text-datafacz-gray-50 overflow-hidden">
      {/* Sidebar */}
      {sidebar && (
        <>
          {/* Mobile overlay */}
          {sidebarOpen && (
            <div
              className="fixed inset-0 z-40 bg-black/50 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Sidebar panel */}
          <aside
            className={clsx(
              'fixed lg:static inset-y-0 left-0 z-50 w-64 bg-datafacz-gray-900 border-r border-datafacz-gray-800 transition-transform duration-300 flex flex-col',
              sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
            )}
          >
            {sidebar}
          </aside>
        </>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between h-16 px-6 border-b border-datafacz-gray-800 bg-datafacz-gray-900/50 backdrop-blur">
          {sidebar && (
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden text-datafacz-gray-50 hover:text-datafacz-orange transition-colors"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          )}
          {header}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};
