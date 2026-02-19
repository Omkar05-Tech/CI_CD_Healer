import React from "react";
import { motion } from "framer-motion";

const CITimeline = () => {
  const events = [
    { s: "FAILED", t: "10:02:14", n: "Initial scan — 6 critical failures", run: "run 1/5", color: "#ff4d6d", active: false },
    { s: "FAILED", t: "10:07:31", n: "Linting & syntax patched — 2 remain", run: "run 2/5", color: "#ff4d6d", active: false },
    { s: "PASSED", t: "10:11:58", n: "All tests green — pipeline clear ✓", run: "run 3/5", color: "#00ffe1", active: true }
  ];

  return (
    <div className="relative pl-12 py-6">
      <style>{`
        @keyframes scan-line {
          0% { top: 0%; opacity: 0; }
          15% { opacity: 1; }
          85% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
        /* The fading mask for the timeline track */
        .timeline-track-fade {
          mask-image: linear-gradient(to bottom, black 70%, transparent 100%);
          -webkit-mask-image: linear-gradient(to bottom, black 70%, transparent 100%);
        }
      `}</style>

      {/* 1. Vertical Track with Fading Effect */}
      <div className="absolute left-[24px] top-0 bottom-0 w-[3px] timeline-track-fade z-0">
        {/* The Colored Gradient Line */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#ff4d6d] via-[#ff4d6d] to-[#00ffe1]" />
        
        {/* Scanning Pulse */}
        <div 
          className="absolute left-0 w-full h-24 bg-gradient-to-b from-transparent via-[#00ffe1] to-transparent z-10"
          style={{ animation: 'scan-line 3.5s linear infinite' }}
        />
      </div>
      
      <div className="space-y-14 relative z-10">
        {events.map((e, i) => (
          <div key={i} className="relative group">
            
            {/* 2. Glowing Status Node */}
            <div 
              className="absolute -left-[36px] top-2 w-[28px] h-[28px] rounded-full border-[5px] border-[#000507] z-20 transition-all duration-500"
              style={{ 
                backgroundColor: e.color, 
                boxShadow: e.active 
                  ? `0 0 25px ${e.color}, 0 0 10px ${e.color}` 
                  : `0 0 15px ${e.color}40` 
              }}
            >
              {/* Pulsing Aura for Active State */}
              {e.active && (
                <div className="absolute inset-[-12px] rounded-full border-2 border-[#00ffe140] animate-ping" />
              )}
            </div>
            
            {/* 3. Event Card */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.2 }}
              className={`bg-[#000d12]/80 border ${e.active ? 'border-[#00ffe150]' : 'border-[#00ffe110]'} p-6 rounded-2xl backdrop-blur-xl shadow-2xl transition-all group-hover:border-[#00ffe140]`}
            >
              <div className="flex justify-between items-start mb-4">
                <span 
                  className="px-5 py-1.5 rounded-lg text-[12px] font-black tracking-[0.25em] border-2 uppercase"
                  style={{ borderColor: `${e.color}40`, color: e.color, backgroundColor: `${e.color}15` }}
                >
                  {e.s}
                </span>
                
                <div className="flex gap-4 text-[11px] font-mono text-[#4a7a8a] tracking-widest font-black uppercase">
                  <span>{e.t}</span>
                  <span className="opacity-30">|</span>
                  <span>{e.run}</span>
                </div>
              </div>
              
              <p className="text-[16px] text-white font-bold leading-relaxed tracking-wide">
                {e.n}
              </p>
            </motion.div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CITimeline;