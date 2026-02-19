import React from "react";
import { motion } from "framer-motion";

const StatCard = ({ label, value, accent, icon, subLabel }) => (
  <motion.div 
    whileHover={{ y: -5, scale: 1.02 }} 
    className="bg-[#000d12]/80 border border-[#002a35] p-8 rounded-2xl relative overflow-hidden backdrop-blur-xl shadow-2xl group transition-all"
  >
    {/* Top Accent Line */}
    <div 
      className="absolute top-0 left-0 w-full h-[2px] opacity-40 group-hover:opacity-100 transition-opacity" 
      style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }} 
    />
    
    {/* Icon with glow */}
    <div className="text-3xl mb-6 filter drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]">
      {icon}
    </div>
    
    {/* Large Value */}
    <div 
      className="text-5xl font-bold font-['Rajdhani'] mb-2 tracking-tighter" 
      style={{ color: accent, textShadow: `0 0 20px ${accent}40` }}
    >
      {value}
    </div>
    
    {/* Labels */}
    <div className="flex flex-col gap-1">
      <div className="text-[10px] font-mono text-white/80 tracking-[0.3em] uppercase font-bold">
        {label}
      </div>
      <div className="text-[8px] font-mono text-[#4a7a8a] tracking-widest uppercase opacity-60">
        {subLabel}
      </div>
    </div>

    {/* Subtle Background Glow */}
    <div 
      className="absolute -bottom-4 -right-4 w-24 h-24 rounded-full blur-[40px] opacity-10 transition-opacity group-hover:opacity-20"
      style={{ backgroundColor: accent }}
    />
  </motion.div>
);

export default StatCard;