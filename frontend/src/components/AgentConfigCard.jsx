import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, User, ShieldCheck, Activity, ChevronRight } from "lucide-react";
import { useAuthStore } from '../authStore';
import { API_BASE_URL } from "../api/apiConfig";
import { useNavigate } from 'react-router-dom'; 

const AgentConfigCard = ({ onLaunch, phase, user }) => {
  const navigate = useNavigate();
  
  // ✅ ACCESS AUTH STATE
  // We need the token to avoid the 500 error (null user_id) in the database
  const token = useAuthStore((state) => state.token);

  const [form, setForm] = useState({
    repoUrl: "https://github.com/rift2026/sample-broken-repo",
    teamName: "INVINCIBLE",
    leaderName: user?.full_name || "Saiyam Kumar"
  });

  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Dynamic Branch Preview
  const branchName = `${form.teamName}_${form.leaderName}`
    .toUpperCase()
    .replace(/\s+/g, "_")
    .replace(/[^A-Z0-9_]/g, "") + "_AI_Fix";

  /**
   * ✅ FIXED BACKEND MAPPING
   * Endpoint: POST /api/agent/run-agent
   * Schema: RunRequest { repo_url, team_name, leader_name }
   * Auth: Requires Bearer Token to populate user_id
   */
  const validateAndLaunch = async () => {
    if (!form.repoUrl || !form.teamName || !form.leaderName) {
      setError("CRITICAL_ERROR: ALL FIELDS MUST BE INITIALIZED");
      setTimeout(() => setError(null), 3000);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/agent/run-agent`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json",
          // ✅ AUTH HEADER: Fixes the 500 Internal Server Error by providing the user context
          "Authorization": `Bearer ${token}` 
        },
        body: JSON.stringify({
          repo_url: form.repoUrl,      // Matches RunRequest schema
          team_name: form.teamName,    // Matches RunRequest schema
          leader_name: form.leaderName // Matches RunRequest schema
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        // Handle specific 401 Unauthorized if token is expired
        if (response.status === 401) {
          throw new Error("SESSION_EXPIRED: Please log in again.");
        }
        throw new Error(result.detail || "AGENT_ORCHESTRATION_FAILED");
      }

      // ✅ SUCCESS: The agent has started
      if (onLaunch) onLaunch(result.data);

    } catch (err) {
      setError(`PROTOCOL_REJECTED: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="bg-[#000d12]/70 border border-[#002a35] rounded-2xl p-8 mb-8 backdrop-blur-xl shadow-[0_0_50px_rgba(0,0,0,0.5)] relative overflow-hidden group">
      {/* Decorative Corner Accents */}
      <div className="absolute top-0 left-0 w-10 h-10 border-t-2 border-l-2 border-[#00ffe1] rounded-tl-xl opacity-60" />
      <div className="absolute bottom-0 right-0 w-10 h-10 border-b-2 border-r-2 border-[#00ffe1] rounded-br-xl opacity-60" />
      
      {/* Header */}
      <div className="flex items-center gap-4 mb-10 border-l-4 border-[#00ffe1] pl-4">
        <div className="flex flex-col">
          <h3 className="text-lg md:text-xl font-bold tracking-[0.5em] text-[#38bdf8] uppercase font-['Rajdhani']">
            Configure Agent Run
          </h3>
          <span className="text-xs font-mono text-[#00ffe180] uppercase tracking-widest mt-1">
            System Initialization v2.0.26
          </span>
        </div>
      </div>
      
      {/* Input Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
        {[
          { id: 'repoUrl', label: 'GitHub Repository URL', ph: 'https://github.com/...' },
          { id: 'teamName', label: 'Team Name', ph: 'TEAM_ID' },
          { id: 'leaderName', label: 'Team Leader Name', ph: 'LEADER_ID' }
        ].map((field) => (
          <div key={field.id} className="space-y-4">
            <label className="text-sm font-mono text-[#6ba7bd] tracking-widest uppercase block font-bold">
              {field.label}
            </label>
            <input 
              className="w-full bg-[#001312] border border-[#002a35] rounded-lg p-4 text-base text-[#c8e6f0] focus:border-[#00ffe1] focus:ring-1 focus:ring-[#00ffe140] outline-none font-mono transition-all shadow-[inset_0_0_15px_rgba(0,0,0,0.6)]"
              value={form[field.id]}
              onChange={(e) => setForm({...form, [field.id]: e.target.value})}
              placeholder={field.ph}
              disabled={isLoading || phase === "running"}
            />
          </div>
        ))}
      </div>

      {/* Target Branch Preview Box */}
      <div className="mb-10 p-6 bg-[#00ffe105] border border-[#002a35] rounded-lg relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#00ffe140] to-transparent" />
        <label className="text-sm font-mono text-[#38bdf8] tracking-widest uppercase mb-4 block text-center font-extrabold">
          Generated Target Branch
        </label>
        <div className="text-center font-mono text-[#00ffe1] text-base tracking-[0.2em] drop-shadow-[0_0_10px_rgba(0,255,225,0.5)]">
          origin / <span className="font-bold">{branchName}</span>
        </div>
      </div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="mb-6 text-center text-red-500 font-mono text-xs tracking-tighter uppercase"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Launch Button */}
      <motion.button 
        onClick={validateAndLaunch}
        disabled={isLoading || phase === "running"}
        whileHover={{ scale: 1.01, boxShadow: "0 0 35px rgba(0,255,225,0.4)" }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-5 bg-gradient-to-r from-[#00ffe1] to-[#38bdf8] text-black font-black font-['Rajdhani'] tracking-[0.7em] rounded-lg transition-all disabled:opacity-50 relative overflow-hidden group/btn text-base"
      >
        <div className="absolute inset-0 bg-white/20 -translate-x-full group-hover/btn:translate-x-full transition-transform duration-700 ease-in-out" />
        <span className="relative z-10 flex items-center justify-center gap-3">
          {isLoading || phase === "running" ? "SYSTEM_ORCHESTRATING..." : "⚡ LAUNCH AGENT"}
        </span>
      </motion.button>
    </section>
  );
};

export default AgentConfigCard;