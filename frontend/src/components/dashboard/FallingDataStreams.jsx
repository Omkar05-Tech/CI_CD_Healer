import React from 'react';

const FallingDataStreams = () => {
  // Updated total stream count to 8
  const streamCount = 8; 
  // Constant speed for all streams (12 seconds per cycle)
  const constantDur = 12; 

  const streams = Array.from({ length: streamCount }, (_, i) => {
    // Calculated positioning to ensure proper distance (Grid-based)
    // We divide the screen into 8 sections and place one in each
    const sectionWidth = 100 / streamCount;
    const basePosition = i * sectionWidth;
    // Add a small controlled jitter (±2%) so it's not perfectly robotic but never overlaps
    const horizontalPos = basePosition + (Math.random() * 4);

    return {
      id: i,
      left: `${horizontalPos}%`, 
      chars: "01アイウエオカキ←→↑↓◈◆▸▹",
      dur: constantDur, 
      // Negative delay for random vertical starting positions
      delay: -(Math.random() * constantDur), 
      opacity: 0.06 + Math.random() * 0.14 
    };
  });

  return (
    <div className="fixed inset-0 pointer-events-none z-10 overflow-hidden">
      <style>{`
        @keyframes data-stream {
          0% { transform: translateY(-100%); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(110vh); opacity: 0; }
        }
      `}</style>
      
      {streams.map((s) => (
        <div 
          key={s.id} 
          className="absolute font-mono text-[14px] text-[#00ffe1] whitespace-nowrap leading-[3]"
          style={{ 
            left: s.left, 
            opacity: s.opacity,
            animation: `data-stream ${s.dur}s ${s.delay}s linear infinite`, 
            writingMode: "vertical-rl",
            filter: "drop-shadow(0 0 8px #00ffe180)" 
          }}
        >
          <span style={{ display: 'block' }}>
            {s.chars}
          </span>
        </div>
      ))}
    </div>
  );
};

export default FallingDataStreams;