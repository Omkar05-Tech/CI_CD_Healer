import React from "react";
import ScoreArc from "./ScoreArc";

const FinalScorePanel = ({ scoreData }) => {
  return (
    <div className="bg-[#000d12]/90 border border-[#00ffe120] p-8 rounded-2xl flex flex-col items-center backdrop-blur-xl shadow-[0_0_40px_rgba(0,255,225,0.1)] relative overflow-hidden h-full">
      {/* Top HUD Accent */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-[2px] bg-[#00ffe1]" />
      <div className="absolute top-2 left-1/2 -translate-x-1/2 text-[8px] font-mono text-[#00ffe160] tracking-[0.5em] uppercase">
        Final Score
      </div>

      {/* The Glow Gauge */}
      <div className="mt-8 mb-4 scale-110">
        <ScoreArc score={scoreData.total} />
      </div>

      {/* Points Breakdown Section */}
      <div className="w-full space-y-4 mt-8 pt-8 border-t border-[#00ffe110]">
        <div className="flex justify-between items-center text-[11px] font-mono tracking-widest">
          <span className="text-[#4a7a8a] uppercase">Base Score</span>
          <span className="text-[#38bdf8] font-bold">+{scoreData.base}</span>
        </div>
        <div className="flex justify-between items-center text-[11px] font-mono tracking-widest">
          <span className="text-[#4a7a8a] uppercase">Speed Bonus &lt;5 min</span>
          <span className="text-[#00ffe1] font-bold">+{scoreData.speed}</span>
        </div>
        <div className="flex justify-between items-center text-[11px] font-mono tracking-widest">
          <span className="text-[#4a7a8a] uppercase">Efficiency Penalty</span>
          <span className="text-[#ff4d6d] font-bold">{scoreData.penalty}</span>
        </div>
        
        {/* Total Aggregate */}
        <div className="pt-6 mt-2 border-t border-[#00ffe120] flex justify-between items-end">
          <span className="text-[10px] font-mono text-white uppercase tracking-[0.4em]">Total</span>
          <span className="text-3xl font-bold font-['Rajdhani'] text-[#00ffe1] leading-none drop-shadow-[0_0_10px_#00ffe1]">
            {scoreData.total}
          </span>
        </div>
      </div>
    </div>
  );
};

export default FinalScorePanel;