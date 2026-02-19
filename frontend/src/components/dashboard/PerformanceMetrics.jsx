import React from "react";

const ProgressBar = ({ label, value, color, unit = "%" }) => (
  <div className="space-y-4">
    <div className="flex justify-between items-center px-1">
      <span className="text-[14px] font-mono text-[#4a7a8a] tracking-[0.2em] uppercase font-black">{label}</span>
      <span className="text-[16px] font-mono font-black" style={{ color }}>{value}{unit}</span>
    </div>
    <div className="h-[8px] w-full bg-white/5 rounded-full overflow-hidden relative border border-white/5">
      {/* Glowing Progress Fill */}
      <div 
        className="h-full rounded-full transition-all duration-1000 ease-out"
        style={{ 
          width: `${unit === '%' ? value : (value/2)*100}%`, 
          backgroundColor: color,
          boxShadow: `0 0 15px ${color}80` 
        }}
      />
    </div>
  </div>
);

const PerformanceMetrics = () => (
  <div className="space-y-10 py-4">
    <ProgressBar label="Fix Success Rate" value={83} color="#00ffe1" />
    <ProgressBar label="Agent Accuracy" value={91} color="#38bdf8" />
    <ProgressBar label="Pipeline Coverage" value={100} color="#a78bfa" />
    <ProgressBar label="Response Latency" value={1.2} unit="s" color="#facc15" />
  </div>
);

export default PerformanceMetrics;