import React from "react";

const LogEntry = ({ time, text, color }) => (
  <div className="flex gap-8 items-start group">
    <div className="flex flex-col items-center">
      {/* Precision Node - Matching your current state visual */}
      <div 
        className="w-3 h-3 rounded-full mt-1.5 transition-all group-hover:scale-125 z-10" 
        style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}` }} 
      />
      <div className="w-[2px] h-14 bg-white/5 group-last:hidden" />
    </div>
    <div className="space-y-1.5 pb-8">
      <span className="text-[12px] font-mono text-[#4a7a8a] font-black tracking-widest">{time}</span>
      <p className="text-[16px] text-white/90 font-bold tracking-wide leading-tight group-hover:text-white transition-colors">
        {text}
      </p>
    </div>
  </div>
);

const AgentActivityLog = () => {
  return (
    <div className="relative h-[380px]">
      <style>{`
        /* 1. Refined Scrollbar Look */
        .hud-scroll-area::-webkit-scrollbar {
          width: 4px;
        }
        .hud-scroll-area::-webkit-scrollbar-track {
          background: transparent;
        }
        .hud-scroll-area::-webkit-scrollbar-thumb {
          background: #002a35;
          border-radius: 10px;
          opacity: 0;
          transition: background 0.3s ease;
        }
        
        /* Show and glow on hover */
        .hud-scroll-area:hover::-webkit-scrollbar-thumb {
          background: #00ffe1;
          box-shadow: 0 0 10px #00ffe1;
        }

        /* 2. Top and Bottom Fading Masks */
        .log-fade-mask {
          mask-image: linear-gradient(to bottom, transparent 0%, black 10%, black 90%, transparent 100%);
          -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 10%, black 90%, transparent 100%);
        }
      `}</style>

      {/* 3. Optimized Scroll Behavior 
          By using 'overflow-y-auto' with the custom scrollbar, 
          the component will now scroll naturally whenever your mouse 
          is positioned over the area.
      */}
      <div className="hud-scroll-area log-fade-mask h-full overflow-y-auto pr-6 scroll-smooth">
        <LogEntry time="10:02:10" text="Repository cloned successfully" color="#38bdf8" />
        <LogEntry time="10:02:45" text="Test suite initialization executed" color="#38bdf8" />
        <LogEntry time="10:03:12" text="6 critical failures identified" color="#ff4d6d" />
        <LogEntry time="10:03:20" text="Autonomous Fixer Agent activated" color="#facc15" />
        <LogEntry time="10:06:44" text="5 security patches committed" color="#00ffe1" />
        <LogEntry time="10:11:58" text="Final pipeline validation passed ✓" color="#00ffe1" />
        <LogEntry time="10:12:05" text="Branch RIFT_SAIYAM_AI_Fix pushed [cite: 52]" color="#00ffe1" />
        <LogEntry time="10:12:30" text="Deployment sync initiated [cite: 83]" color="#38bdf8" />
        
        {/* Buffer for bottom fade */}
        <div className="h-10" />
      </div>
    </div>
  );
};

export default AgentActivityLog;