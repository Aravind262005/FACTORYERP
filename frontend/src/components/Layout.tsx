import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { 
  LayoutDashboard, 
  PlusSquare, 
  History, 
  BookOpen, 
  ScrollText, 
  Settings, 
  User,
  Bell
} from 'lucide-react';

export const Layout = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'New Query', path: '/query/new', icon: <PlusSquare size={20} /> },
    { name: 'Query History', path: '/history', icon: <History size={20} /> },
    { name: 'Knowledge Base', path: '/knowledge', icon: <BookOpen size={20} /> },
    { name: 'Audit Trail', path: '/audit', icon: <ScrollText size={20} /> },
    { name: 'Settings', path: '/settings', icon: <Settings size={20} /> },
  ];

  return (
    <div className="flex h-screen bg-[#F8FAFC]">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-[#E2E8F0] flex flex-col justify-between">
        <div>
          <div className="p-6">
            <h1 className="text-xl font-bold text-slate-900">DecisionSupport</h1>
            <p className="text-xs text-slate-500 font-semibold tracking-wider mt-1">MANUFACTURING INTELLIGENCE</p>
          </div>
          <nav className="mt-4 px-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                <span className="mr-3">{item.icon}</span>
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-[#E2E8F0]">
          <button className="flex items-center px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 w-full rounded-md hover:bg-slate-50">
            <User size={20} className="mr-3" />
            Profile
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-[#E2E8F0] flex items-center justify-between px-8">
          <div className="flex-1">
             {/* Global Search could go here */}
          </div>
          <div className="flex items-center space-x-4 text-slate-600">
            <button className="hover:text-slate-900"><Bell size={20} /></button>
            <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center text-sm font-medium">
              US
            </div>
          </div>
        </header>

        {/* Main Body */}
        <main className="flex-1 overflow-auto p-8">
          <div className="max-w-6xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
