import React, { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const AgentChat = ({ messages }) => {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom as the agent "thinks"
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="bg-[#020810] border border-[#0a1628] rounded-xl p-4 h-[400px] flex flex-col shadow-2xl">
      <div className="flex items-center gap-2 text-[10px] font-mono text-[#38bdf8] tracking-widest mb-4 border-b border-[#0a1628] pb-2">
        <span className="w-2 h-2 bg-[#38bdf8] rounded-full animate-pulse"></span>
        AGENT_LOG_STREAM
      </div>
      
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin scrollbar-thumb-[#1e3a5f]"
      >
        <AnimatePresence mode="popLayout">
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.2 }}
              className={`flex ${msg.isAgent ? "justify-start" : "justify-end"}`}
            >
              <div className={`max-w-[85%] p-3 rounded-lg text-xs font-mono leading-relaxed ${
                msg.isAgent 
                  ? "bg-[#1e3a5f20] border border-[#38bdf830] text-[#38bdf8]" 
                  : "bg-[#00ff8810] border border-[#00ff8830] text-[#00ff88]"
              }`}>
                {msg.isAgent && <span className="text-[10px] opacity-50 block mb-1">AI_THOUGHT </span>}
                {msg.text}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AgentChat;