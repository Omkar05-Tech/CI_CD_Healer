import React, { useState } from "react";
import { KeyRound, ArrowLeft, ShieldCheck, Activity } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [pwd, setPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleReset = () => {
    setError("");
    if (!pwd || pwd.length < 8) return setError("SECURITY_CRITICAL: MIN 8 CHARACTERS REQUIRED");
    if (pwd !== confirmPwd) return setError("VALIDATION_ERROR: KEY_MISMATCH");
    
    setIsLoading(true);
    // Simulate encryption/reset process
    setTimeout(() => {
      alert("Access Key Updated Successfully!");
      navigate("/login");
    }, 1500);
  };

  return (
    <div className="relative min-h-screen bg-[#030712] text-slate-300 font-['Inter'] flex items-center justify-center px-4 overflow-hidden">
      
      {/* --- Ambient Background Glow --- */}
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 w-full max-w-md p-1"
      >
        <div className="bg-[#000d12]/90 border border-white/10 backdrop-blur-2xl rounded-2xl p-8 shadow-2xl relative overflow-hidden">
          
          {/* HUD Header Accent */}
          <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50" />

          <button
            onClick={() => navigate("/verify-otp")}
            className="flex items-center gap-2 text-[10px] font-mono text-blue-400 hover:text-blue-300 uppercase tracking-widest mb-8 transition-colors"
          >
            <ArrowLeft className="h-3" /> Previous_Step
          </button>

          <div className="flex flex-col items-center mb-8">
            <div className="bg-blue-500/10 p-3 rounded-full border border-blue-500/20 mb-4">
              <ShieldCheck className="h-8 w-8 text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold font-['Rajdhani'] tracking-[0.2em] text-white uppercase">Reset Access Key</h2>
            <div className="flex items-center gap-2 mt-1">
              <Activity className="h-3 w-3 text-blue-500 animate-pulse" />
              <p className="text-[9px] font-mono text-slate-500 tracking-widest uppercase">Protocol: Override_Sequence</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* New Password */}
            <div className="space-y-2">
              <label className="text-[10px] font-mono text-slate-500 tracking-widest uppercase ml-1">New Security Key</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <KeyRound className="h-4 w-4 text-blue-500/40 group-focus-within:text-blue-400 transition-colors" />
                </div>
                <input
                  type="password"
                  placeholder="NEW_IDENTIFIER"
                  className={`w-full bg-[#001312] border ${error ? "border-red-500/50" : "border-white/10"} rounded-lg pl-12 pr-4 py-4 text-sm text-slate-200 focus:border-blue-500/50 outline-none font-mono transition-all`}
                  value={pwd}
                  onChange={e => [setPwd(e.target.value), setError("")]}
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <label className="text-[10px] font-mono text-slate-500 tracking-widest uppercase ml-1">Verify Identifier</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <KeyRound className="h-4 w-4 text-blue-500/40 group-focus-within:text-blue-400 transition-colors" />
                </div>
                <input
                  type="password"
                  placeholder="CONFIRM_SEQUENCE"
                  className={`w-full bg-[#001312] border ${error ? "border-red-500/50" : "border-white/10"} rounded-lg pl-12 pr-4 py-4 text-sm text-slate-200 focus:border-blue-500/50 outline-none font-mono transition-all`}
                  value={confirmPwd}
                  onChange={e => [setConfirmPwd(e.target.value), setError("")]}
                />
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  className="p-3 bg-red-900/20 border border-red-500/30 rounded-lg"
                >
                  <p className="text-[10px] font-mono text-red-400 text-center uppercase tracking-tighter">{error}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              onClick={handleReset}
              disabled={isLoading}
              className="w-full relative py-4 bg-blue-600 text-white font-black font-['Rajdhani'] tracking-[0.4em] rounded-lg overflow-hidden transition-all hover:bg-blue-500 hover:shadow-[0_0_25px_rgba(59,130,246,0.3)] disabled:opacity-50 group"
            >
              <div className="absolute inset-0 bg-white/10 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              <span className="relative z-10 uppercase">
                {isLoading ? "Encrypting..." : "Commit_New_Key"}
              </span>
            </button>
          </div>

        </div>
      </motion.div>
    </div>
  );
};

export default ResetPasswordPage;