import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../authStore";
import { 
  FallingDataStreams, 
  ElectronReactor, 
  StatCard, 
  ScoreArc, 
  RadarChart, 
  FixesTable, 
  Terminal,
  CITimeline 
} from "../components/dashboard";
import AgentConfigCard from "../components/AgentConfigCard";
import PerformanceMetrics from "../components/dashboard/PerformanceMetrics";
import AgentActivityLog from "../components/dashboard/AgentActivityLog";

// Summary field component for the Run Summary grid
const SummaryField = ({ label, value, color = "text-white" }) => (
  <div className="space-y-2">
    <p className="text-[8px] font-mono text-[#4a7a8a] tracking-[0.3em] uppercase">{label}</p>
    <div className={`text-xs font-mono ${color} truncate`}>{value}</div>
  </div>
);

const AutonomousDashboard = () => {
  const user = useAuthStore((state) => state.user);
  const [phase, setPhase] = useState("idle");
  const [showResult, setShowResult] = useState(false);
  const [activeFormData, setActiveFormData] = useState(null);
  const resultRef = useRef(null);

  // Scoring Data
  const scoreData = { base: 100, speed: 10, penalty: "-0", total: 110 };

  const handleLaunch = (formData) => {
    if (phase === "running") return;
    setActiveFormData(formData);
    setShowResult(false);
    setPhase("running");
  };

  const handleDone = () => {
    setPhase("done");
    setTimeout(() => {
      setShowResult(true);
      // Ensure smooth scroll to results once they are ready
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 800);
  };

  const branchName = activeFormData 
    ? `${activeFormData.teamName}_${activeFormData.leaderName}`.toUpperCase().replace(/\s+/g, "_").replace(/[^A-Z0-9_]/g, "") + "_AI_Fix"
    : "PENDING_INITIALIZATION";

  return (
    <div className="relative min-h-screen bg-[#000507] text-[#c8e6f0] font-['Exo_2'] overflow-x-hidden">
      {/* BACKGROUND LAYERS */}
      <ElectronReactor />
      <FallingDataStreams />
      
      {/* HUD Scanline Effect */}
      <div className="fixed inset-0 pointer-events-none z-10">
        <div className="absolute left-0 right-0 h-[3px] bg-gradient-to-r from-transparent via-[#00ffe110] to-transparent animate-[scan_12s_linear_infinite]" />
      </div>

      <main className="relative z-20 max-w-7xl mx-auto p-8 pt-10">
        {/* HERO SECTION */}
        <div className="text-center mb-16">
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
            <h2 className="text-7xl font-bold font-['Rajdhani'] tracking-[0.2em] bg-gradient-to-r from-white via-[#00ffe1] to-[#38bdf8] bg-clip-text text-transparent uppercase drop-shadow-[0_0_15px_rgba(0,255,225,0.3)]">
              Autonomous
            </h2>
            <p className="text-3xl font-light tracking-[0.6em] text-[#c8e6f0]/30 font-['Rajdhani'] uppercase italic">
              CI/CD Healing Agent
            </p>
          </motion.div>
        </div>

        {/* AGENT CONFIGURATION */}
        <AgentConfigCard user={user} phase={phase} onLaunch={handleLaunch} />

        {/* TERMINAL OUTPUT */}
        <AnimatePresence>
          {(phase === "running" || phase === "done") && (
            <Terminal active={phase === "running"} onDone={handleDone} />
          )}
        </AnimatePresence>

        {/* EVALUATION RESULTS SECTION */}
        <div ref={resultRef}>
          <AnimatePresence>
            {showResult && (
              <motion.div initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} className="space-y-10 pt-10 pb-20">
                
                {/* 1. TOP STATS GRID */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                  <StatCard label="Total Detected" value={6} accent="#ff4d6d" icon="🔍" subLabel="Failures Found" />
                  <StatCard label="Auto-Patched" value={5} accent="#00ffe1" icon="🔧" subLabel="Fixes Applied" />
                  <StatCard label="Total Runtime" value="3m 57s" accent="#38bdf8" icon="⏱" subLabel="Time Elapsed" />
                  <StatCard label="Of 5 Limit" value="3" accent="#a78bfa" icon="🔁" subLabel="CI Iterations" />
                </div>

                {/* 2. MAIN RESULTS BLOCK (Summary & Final Score) */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
                  
                  {/* Run Summary Card */}
                  <div className="lg:col-span-2 bg-[#000d12]/80 border border-[#002a35] p-10 rounded-2xl backdrop-blur-xl shadow-2xl relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-10 border-l-4 border-[#38bdf8] pl-4">
                      <h3 className="text-[11px] font-bold tracking-[0.4em] text-[#38bdf8] uppercase font-['Rajdhani']">Run Summary</h3>
                    </div>
                    
                    <div className="space-y-12">
                      <div className="grid grid-cols-2 gap-x-12 gap-y-8">
                        <SummaryField label="Repository" value={activeFormData?.repoUrl} />
                        <SummaryField label="Branch" value={branchName} color="text-[#00ffe1]" />
                        <SummaryField label="Team" value={activeFormData?.teamName} />
                        <SummaryField label="Leader" value={activeFormData?.leaderName} />
                      </div>

                      {/* Pipeline Status Bar */}
                      <div className="bg-[#00ffe108] border border-[#00ffe120] p-6 rounded-xl flex items-center gap-6">
                        <div className="relative">
                          <div className="w-4 h-4 rounded-full bg-[#00ffe1] shadow-[0_0_15px_#00ffe1] animate-pulse" />
                          <div className="absolute inset-[-6px] rounded-full border border-[#00ffe130] animate-ping" />
                        </div>
                        <div className="space-y-1">
                          <div className="text-sm font-bold font-['Rajdhani'] text-[#00ffe1] tracking-[0.5em] uppercase">CI/CD Pipeline — Passed</div>
                          <div className="text-[9px] font-mono text-[#4a7a8a] tracking-widest uppercase">5 commits • branch protected • tests green</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Final Score Card */}
                  <div className="bg-[#000d12]/90 border border-[#00ffe120] p-8 rounded-2xl flex flex-col items-center backdrop-blur-xl shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-[2px] bg-[#00ffe1]" />
                    <h3 className="text-[#00ffe1] font-['Rajdhani'] font-bold tracking-[0.4em] mb-8 uppercase text-[10px] mt-2">Final Score</h3>
                    
                    <div className="mb-4 scale-110">
                      <ScoreArc score={scoreData.total} />
                    </div>

                    <div className="w-full space-y-4 mt-8 pt-8 border-t border-[#00ffe110]">
                      <div className="flex justify-between text-[11px] font-mono tracking-widest">
                        <span className="text-[#4a7a8a] uppercase">Base Score</span>
                        <span className="text-[#38bdf8] font-bold">+{scoreData.base}</span>
                      </div>
                      <div className="flex justify-between text-[11px] font-mono tracking-widest">
                        <span className="text-[#4a7a8a] uppercase">Speed Bonus</span>
                        <span className="text-[#00ffe1] font-bold">+{scoreData.speed}</span>
                      </div>
                      <div className="flex justify-between text-[11px] font-mono tracking-widest">
                        <span className="text-[#4a7a8a] uppercase">Efficiency Penalty</span>
                        <span className="text-[#ff4d6d] font-bold">{scoreData.penalty}</span>
                      </div>
                      <div className="pt-6 mt-2 border-t border-[#00ffe120] flex justify-between items-end">
                        <span className="text-[10px] font-mono text-white uppercase tracking-[0.4em]">Total</span>
                        <span className="text-3xl font-bold font-['Rajdhani'] text-[#00ffe1] drop-shadow-[0_0_10px_#00ffe1]">{scoreData.total}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 3. LOWER SECTION (History & Timeline) */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2 bg-[#000d12]/80 border border-[#002a35] p-10 rounded-2xl backdrop-blur-xl shadow-2xl relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-10 border-l-4 border-[#ff4d6d] pl-4">
                      <h3 className="text-[11px] font-bold tracking-[0.4em] text-[#ff4d6d] uppercase font-['Rajdhani']">Fixes Applied</h3>
                    </div>
                    <FixesTable />
                  </div>
                  
                  <div className="bg-[#000d12]/80 border border-[#002a35] p-10 rounded-2xl backdrop-blur-xl shadow-2xl">
                    <div className="flex items-center gap-3 mb-10 border-l-4 border-[#a78bfa] pl-4">
                      <h3 className="text-[11px] font-bold tracking-[0.4em] text-[#a78bfa] uppercase font-['Rajdhani']">CI/CD Timeline</h3>
                    </div>
                    <CITimeline />
                  </div>
                </div>

                {/* FINAL HUD SECTION */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pt-10 pb-20">
                
                {/* Bug Distribution (Radar) */}
                <div className="bg-[#000d12]/80 border border-[#002a35] p-10 rounded-2xl backdrop-blur-xl shadow-2xl">
                    <div className="flex items-center gap-3 mb-10 border-l-4 border-[#38bdf8] pl-4">
                    <h3 className="text-[11px] font-bold tracking-[0.4em] text-[#38bdf8] uppercase font-['Rajdhani']">Bug Distribution</h3>
                    </div>
                    <RadarChart />
                </div>

                {/* Performance Metrics */}
                <div className="bg-[#000d12]/80 border border-[#002a35] p-10 rounded-2xl backdrop-blur-xl shadow-2xl relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-10 border-l-4 border-[#facc15] pl-4">
                    <h3 className="text-[11px] font-bold tracking-[0.4em] text-[#facc15] uppercase font-['Rajdhani']">Performance Metrics</h3>
                    </div>
                    <PerformanceMetrics />
                </div>

                {/* Agent Activity Log */}
                <div className="bg-[#000d12]/80 border border-[#002a35] p-10 rounded-2xl backdrop-blur-xl shadow-2xl">
                    <div className="flex items-center gap-3 mb-10 border-l-4 border-[#00ffe1] pl-4">
                    <h3 className="text-[11px] font-bold tracking-[0.4em] text-[#00ffe1] uppercase font-['Rajdhani']">Agent Activity Log</h3>
                    </div>
                    <AgentActivityLog />
                </div>

                </div>

              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};

export default AutonomousDashboard;