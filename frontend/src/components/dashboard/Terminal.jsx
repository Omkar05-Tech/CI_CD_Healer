import React, { useState, useEffect, useRef } from "react";

const Terminal = ({ active, onDone }) => {
  const [lines, setLines] = useState([]);
  const ref = useRef(null);

  useEffect(() => {
    if (!active) return;
    
    // Ensure all objects have the text and color keys defined
    const mockLogs = [
      { text: "✓ [AI-AGENT] SYNTAX src/validator.py:8 patched", color: "text-[#00ffe1]" },
      { text: "✓ [AI-AGENT] TYPE_ERROR src/models.py:42 patched", color: "text-[#00ffe1]" },
      { text: "✓ [AI-AGENT] IMPORT src/api.py:3 patched", color: "text-[#00ffe1]" },
      { text: "X [AI-AGENT] LOGIC src/helpers.py:77 failed", color: "text-[#ff4d6d]" },
      { text: "✓ [AI-AGENT] INDENTATION src/config.py:21 patched", color: "text-[#00ffe1]" },
      { text: "$ git push origin INVINCIBLE_USER_AI_Fix", color: "text-[#38bdf8]" },
      { text: "→ Monitoring Actions pipeline... iteration 3/5", color: "text-[#facc15]" },
      { text: "— ✓ ALL TESTS PASSED — 5 fixes in 3m 57s —", color: "text-[#00ffe1] font-bold" },
      { text: "$ Writing results.json... complete.", color: "text-[#4a7a8a]" }
    ];

    let i = 0;
    const interval = setInterval(() => {
      // Safety check: ensure mockLogs[i] exists before setting state
      if (mockLogs[i]) {
        setLines(p => [...p, mockLogs[i]]);
        i++;
      }
      
      if (i >= mockLogs.length) {
        clearInterval(interval);
        onDone();
      }
    }, 800);

    return () => clearInterval(interval);
  }, [active, onDone]);

  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, [lines]);

  return (
    <div className="bg-[#000d12]/80 border border-[#002a35] rounded-xl overflow-hidden backdrop-blur-xl shadow-2xl mb-8 font-mono">
      {/* Header matched to your screenshot */}
      <div className="bg-[#001a22] px-4 py-2 flex justify-between items-center border-b border-[#002a35]">
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-[#ff4d6d]" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#facc15]" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#00ffe1]" />
          <span className="text-[10px] text-[#4a7a8a] ml-4 tracking-widest uppercase opacity-60">
            agent@rift-2026:~ -- bash
          </span>
        </div>
        {!active && lines.length > 0 && (
          <span className="text-[10px] text-[#facc15] font-bold tracking-[0.3em] animate-pulse">
            COMPLETE
          </span>
        )}
      </div>

      <div 
        ref={ref}
        className="p-6 h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-[#002a35] scrollbar-track-transparent"
      >
        {lines.map((l, i) => {
          // ADDED NULL CHECK HERE TO PREVENT THE ERROR
          if (!l) return null;
          
          return (
            <div key={i} className={`${l.color || 'text-white'} text-xs mb-2 tracking-wide flex gap-3`}>
              <span className="opacity-40">{i + 1}</span>
              <span>{l.text}</span>
            </div>
          );
        })}
        {active && (
          <div className="flex gap-3 items-center">
            <span className="opacity-40">{lines.length + 1}</span>
            <span className="w-2 h-4 bg-[#00ffe1] animate-pulse shadow-[0_0_10px_#00ffe1]" />
          </div>
        )}
      </div>
    </div>
  );
};

export default Terminal;