import React from 'react';

const ElectronNode = ({ angle, color = "#00ffe1", delay = "0s" }) => {
  const x = Math.cos((angle * Math.PI) / 180) * 50 + 50;
  const y = Math.sin((angle * Math.PI) / 180) * 50 + 50;

  return (
    <div 
      className="absolute w-[6px] h-[6px] rounded-full z-10" 
      style={{ 
        left: `${x}%`,
        top: `${y}%`,
        backgroundColor: color, 
        transform: 'translate(-50%, -50%)',
        animation: `fluid-glow 4s ease-in-out infinite`,
        animationDelay: delay,
        '--glow-color': color,
      }} 
    />
  );
};

const OrbitRing = ({ size, top, left, color, nodeColor, ringDelay = "0s" }) => {
  const nodeAngles = [0, 60, 120, 180, 240, 300];

  return (
    <div 
      className="absolute pointer-events-none"
      style={{ 
        width: size, 
        height: size, 
        top: top, 
        left: left,
        transform: 'translate(-50%, -50%)',
      }}
    >
      <div 
        className="w-full h-full rounded-full border relative"
        style={{ 
          borderColor: color,
          borderWidth: '1.5px',
          boxShadow: `0 0 15px ${color}30`, 
          animation: `ring-fade 4s ease-in-out infinite`,
          animationDelay: ringDelay
        }}
      >
        {nodeAngles.map((angle, i) => (
          <ElectronNode 
            key={i} 
            angle={angle} 
            color={nodeColor} 
            delay={`${i * 0.5}s`} 
          />
        ))}
      </div>
    </div>
  );
};

const ElectronReactor = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden bg-transparent">
      <style>{`
        @keyframes fluid-glow {
          0%, 100% { 
            opacity: 0.4; 
            box-shadow: 0 0 4px var(--glow-color), 0 0 8px var(--glow-color);
            transform: translate(-50%, -50%) scale(0.9);
          }
          50% { 
            opacity: 1; 
            box-shadow: 0 0 12px var(--glow-color), 0 0 24px var(--glow-color);
            transform: translate(-50%, -50%) scale(1.2);
          }
        }
        @keyframes ring-fade {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 0.6; }
        }
      `}</style>

      {/* Hero Section Main Ring */}
      <OrbitRing size="780px" top="42%" left="50%" color="rgba(0, 255, 225, 0.4)" nodeColor="#00ffe1" />
      
      {/* Top Left Accent */}
      <OrbitRing size="450px" top="25%" left="5%" color="rgba(56, 189, 248, 0.3)" nodeColor="#38bdf8" ringDelay="1s" />
      
      {/* Bottom Right - Adjusted for Patch Execution History Visibility */}
      <OrbitRing size="550px" top="85%" left="92%" color="rgba(0, 255, 225, 0.25)" nodeColor="#00ffe1" ringDelay="2s" />
    </div>
  );
};

export default ElectronReactor;