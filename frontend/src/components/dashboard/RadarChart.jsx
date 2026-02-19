import React from "react";

const RadarChart = () => {
  const points = "100,25 165,62.5 165,137.5 100,175 35,137.5 35,62.5";
  const dataPoints = "100,45 155,75 145,125 100,155 55,115 65,75";
  const labels = [
    { name: "LINTING", x: 100, y: 15, color: "#00ffe1" },
    { name: "SYNTAX", x: 185, y: 65, color: "#ff4d6d" },
    { name: "LOGIC", x: 185, y: 145, color: "#a78bfa" },
    { name: "TYPE_ERROR", x: 100, y: 195, color: "#facc15" },
    { name: "IMPORT", x: 15, y: 145, color: "#38bdf8" },
    { name: "INDENTATION", x: 15, y: 65, color: "#ff4d6d" },
  ];

  return (
    <div className="relative flex items-center justify-center h-[300px] w-full group">
      <svg viewBox="0 0 200 200" className="w-full h-full">
        {/* Background Grid Hexagons */}
        {[0.2, 0.4, 0.6, 0.8, 1].map((scale, i) => (
          <polygon
            key={i}
            points={points}
            fill="none"
            stroke="rgba(255, 255, 255, 0.05)"
            strokeWidth="1"
            style={{ transform: `scale(${scale})`, transformOrigin: 'center' }}
          />
        ))}
        {/* Axis Lines */}
        <line x1="100" y1="100" x2="100" y2="25" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
        <line x1="100" y1="100" x2="165" y2="62.5" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
        <line x1="100" y1="100" x2="165" y2="137.5" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
        <line x1="100" y1="100" x2="100" y2="175" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
        <line x1="100" y1="100" x2="35" y2="137.5" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
        <line x1="100" y1="100" x2="35" y2="62.5" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
        
        {/* Active Data Area */}
        <polygon
          points={dataPoints}
          fill="rgba(0, 255, 225, 0.1)"
          stroke="#00ffe1"
          strokeWidth="2"
          className="drop-shadow-[0_0_8px_rgba(0,255,225,0.5)] transition-all group-hover:fill-rgba(0, 255, 225, 0.2)"
        />
        
        {/* Radar Labels */}
        {labels.map((l, i) => (
          <text key={i} x={l.x} y={l.y} fill={l.color} fontSize="8" fontFamily="mono" textAnchor="middle" className="font-black tracking-widest uppercase">
            {l.name}
          </text>
        ))}
      </svg>
    </div>
  );
};

export default RadarChart;