import React, { useState, useEffect } from "react";

const ScoreArc = ({ score = 110 }) => {
  const r = 75, circ = 2 * Math.PI * r;
  const [offset, setOffset] = useState(circ);

  useEffect(() => {
    // Score is relative to a 130 max
    setOffset(circ * (1 - score / 130));
  }, [score]);

  return (
    <div className="relative w-[200px] h-[200px] flex items-center justify-center">
      {/* Background Glow */}
      <div className="absolute inset-4 rounded-full bg-[#00ffe105] blur-xl" />
      
      <svg className="rotate-[-90deg] w-full h-full p-2">
        {/* Track */}
        <circle cx="100" cy="100" r={r} fill="none" stroke="#001a22" strokeWidth="6" />
        {/* Progress Arc */}
        <circle 
          cx="100" cy="100" r={r} fill="none" 
          stroke="#00ffe1" strokeWidth="8"
          strokeDasharray={circ} 
          style={{ 
            strokeDashoffset: offset, 
            transition: "stroke-dashoffset 2s cubic-bezier(0.4, 0, 0.2, 1)",
            filter: "drop-shadow(0 0 8px #00ffe180)"
          }} 
          strokeLinecap="round" 
        />
      </svg>
      
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-5xl font-bold font-['Rajdhani'] text-white drop-shadow-[0_0_15px_#00ffe140]">
          {score}
        </span>
        <span className="text-[9px] font-mono text-[#00ffe180] tracking-[0.4em] uppercase mt-1">
          Score
        </span>
      </div>
    </div>
  );
};

export default ScoreArc;