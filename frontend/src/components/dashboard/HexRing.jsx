import React from "react";

const HexRing = ({ size = 300, color = "#00ffe1" }) => (
  <div className="relative pointer-events-none" style={{ width: size, height: size }}>
    {[1, 0.7, 0.4].map((s, i) => (
      <div key={i} className="absolute inset-0 border rounded-full animate-spin-slow"
        style={{ borderColor: `${color}${i === 0 ? "20" : "0a"}`, transform: `scale(${s})`, animationDuration: `${20 + i * 10}s` }} />
    ))}
  </div>
);

export default HexRing;