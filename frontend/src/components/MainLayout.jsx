import React from 'react';
import { Outlet } from 'react-router-dom';
import Chatbot from './Chatbot';

const MainLayout = () => {
  return (
    /* Changed bg-gray-50 to #03060f to match the DevOps track theme */
    <div className="flex h-screen w-full bg-[#03060f] text-slate-200 overflow-hidden font-sans">
      
      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto h-full relative custom-scrollbar">
        
        {/* Subtle background ambient glows for better visual depth */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
            <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-blue-600/5 rounded-full blur-[120px]" />
            <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-purple-600/5 rounded-full blur-[120px]" />
        </div>

        {/* Render the specific page content (AutonomousDashboard, etc.) 
           The p-8 ensures the Dashboard content isn't touching the screen edges.
        */}
        <div className="relative z-10 p-8 max-w-7xl mx-auto">
            <Outlet />
        </div>
      </main>

      {/* Keep Chatbot at the global level as per your existing structure */}
      <Chatbot />
    </div>
  );
};

export default MainLayout;