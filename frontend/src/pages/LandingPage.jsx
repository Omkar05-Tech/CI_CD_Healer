import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Terminal, ShieldCheck, Zap, Cpu, Activity, Globe, 
  ArrowRight, Github, Menu, X 
} from 'lucide-react';
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";

const LandingPage = () => {
  const [init, setInit] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    }).then(() => setInit(true));
  }, []);

  return (
    <div className="relative min-h-screen bg-[#030712] text-slate-300 font-['Inter'] overflow-x-hidden">
      
      {/* Background Mesh (Dynamic Density) */}
      {init && (
        <Particles
          id="tsparticles"
          options={{
            fullScreen: { enable: false },
            particles: {
              number: { value: 30, density: { enable: true, area: 800 } },
              color: { value: "#3b82f6" },
              links: {
                enable: true,
                distance: 150,
                color: "#1e40af",
                opacity: 0.1,
              },
              move: { enable: true, speed: 0.4 },
              opacity: { value: 0.2 },
              size: { value: 1 },
            }
          }}
          className="absolute inset-0 z-0"
        />
      )}

      {/* --- Navigation --- */}
      <nav className="relative z-[100] w-full flex items-center justify-between px-6 lg:px-10 py-5 border-b border-white/5 bg-[#030712]/50 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 lg:h-10 lg:w-10 bg-gradient-to-tr from-blue-700 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
            <Cpu className="h-5 w-5 lg:h-6 lg:w-6 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg lg:text-xl font-bold tracking-tight text-white uppercase font-['Rajdhani']">CICD Healer</span>
            <span className="text-[8px] lg:text-[9px] font-bold text-blue-400 uppercase tracking-[0.3em] leading-none">Autonomous DevOps</span>
          </div>
        </div>

        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="lg:hidden p-2 text-slate-400">
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>

        <div className="hidden lg:flex items-center gap-8">
          <Link to="/login" className="text-sm font-semibold text-slate-400 hover:text-white transition-colors uppercase font-['Rajdhani'] tracking-widest">Login</Link>
          <Link to="/signup" className="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-500 transition-all font-['Rajdhani'] uppercase tracking-widest text-xs">Register ID</Link>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className="fixed inset-0 z-[90] bg-[#030712] flex flex-col items-center justify-center gap-10 lg:hidden"
          >
            <Link onClick={() => setMobileMenuOpen(false)} to="/login" className="text-2xl font-bold font-['Rajdhani'] tracking-[0.3em] uppercase">Login</Link>
            <Link onClick={() => setMobileMenuOpen(false)} to="/signup" className="px-10 py-4 bg-blue-600 text-white font-bold rounded-xl font-['Rajdhani'] tracking-[0.3em] uppercase">Register ID</Link>
          </motion.div>
        )}
      </AnimatePresence>

      {/* --- Main Hero Content --- */}
      <main className="relative z-20 max-w-7xl mx-auto px-6 lg:px-10 pt-12 lg:pt-32 pb-20">
        <div className="flex flex-col lg:grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          
          <div className="space-y-6 lg:space-y-10 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/30 border border-blue-500/20">
              <Activity className="h-3 w-3 text-blue-400 animate-pulse" />
              <span className="text-[8px] lg:text-[10px] font-bold text-blue-300 uppercase tracking-widest">Autonomous Healing Active</span>
            </div>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-tight">
              Kill the <br className="hidden lg:block" />
              <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent">Debugging Loop.</span>
            </h1>

            <p className="text-sm lg:text-lg text-slate-400 max-w-lg mx-auto lg:mx-0 leading-relaxed">
              Developers spend 40-60% of their time fixing pipeline failures. 
              CICD Healer utilizes multi-agent intelligence to detect, patch, and verify code issues autonomously.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 lg:gap-5 items-center justify-center lg:justify-start">
              <Link to="/signup" className="w-full sm:w-auto group flex items-center justify-between gap-6 lg:gap-12 px-8 py-4 lg:py-5 bg-white text-black text-xs lg:text-[14px] font-black font-['Rajdhani'] rounded-xl transition-all shadow-xl">
                Deploy Agent 
                <ArrowRight className="h-4 w-4 lg:h-5 lg:w-5 group-hover:translate-x-2 transition-transform" />
              </Link>
              <Link to="/login" className="w-full sm:w-auto flex items-center justify-center px-10 py-4 lg:py-5 bg-[#0a101f] text-white text-xs lg:text-[14px] font-black font-['Rajdhani'] rounded-xl border border-white/10 transition-all uppercase tracking-[0.2em]">
                Connect Repository
              </Link>
            </div>
          </div>

          <div className="w-full relative group lg:block mt-8 lg:mt-0">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl blur opacity-20"></div>
            <div className="relative bg-[#000d12] border border-white/10 rounded-xl p-5 lg:p-8 font-mono text-[10px] lg:text-[13px] shadow-2xl overflow-hidden">
              <div className="flex gap-2 mb-4 lg:mb-6">
                <div className="w-2 h-2 lg:w-3 lg:h-3 rounded-full bg-red-500/40"></div>
                <div className="w-2 h-2 lg:w-3 lg:h-3 rounded-full bg-yellow-500/40"></div>
                <div className="w-2 h-2 lg:w-3 lg:h-3 rounded-full bg-green-500/40"></div>
              </div>
              <div className="space-y-1 lg:space-y-2">
                <p className="text-blue-400"># Initializing CICD_Healer_Agent...</p>
                <p className="text-red-400">! Failure: TYPE_ERROR in src/validator.py</p>
                <p className="text-green-400">✓ Patch Committed: [AI-AGENT] Fixed Type Error</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* --- FIXED RESPONSIVE FOOTER --- */}
      <footer id="specs" className="relative z-20 bg-[#030712] py-12 lg:py-24 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          
          {/* Responsive Stat Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10 lg:gap-16 mb-12 lg:mb-20">
            <StatBlock label="BASE SCORE" value="100 POINTS" />
            <StatBlock label="RETRY LIMIT" value="5 ITERATIONS" />
            <StatBlock label="BRANCH FORMAT" value="AI_FIX" />
          </div>

          {/* Bottom Branding Bar */}
          <div className="flex flex-col lg:flex-row justify-between items-center gap-6 pt-10 border-t border-white/5 text-center lg:text-left">
            <div className="flex flex-col lg:flex-row items-center gap-4 opacity-50">
              <div className="h-8 w-8 bg-slate-800 rounded flex items-center justify-center mb-2 lg:mb-0">
                <ShieldCheck className="h-4 w-4 text-slate-400" />
              </div>
              <span className="text-[10px] lg:text-[11px] font-mono tracking-[0.3em] uppercase">
                CICD Healer // Agentic Systems // Nominal State
              </span>
            </div>
            
            <p className="text-slate-700 text-[10px] font-mono tracking-widest uppercase">
              &copy; {new Date().getFullYear()} Deployment Active
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

const StatBlock = ({ label, value }) => (
  <div className="flex flex-col border-l border-blue-500/20 pl-6 group transition-all hover:border-blue-500">
    <span className="text-[9px] lg:text-[10px] font-bold text-blue-500/60 uppercase tracking-widest mb-2 font-['Rajdhani']">
      {label}
    </span>
    <span className="text-sm lg:text-base font-bold text-slate-200 tracking-wider uppercase font-mono group-hover:text-blue-400 transition-colors">
      {value}
    </span>
  </div>
);

export default LandingPage;