import React, { useState } from "react";
import { Mail, Lock, Activity, ChevronLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { API_BASE_URL } from "../api/apiConfig";

const ForgotEmailPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendOtp = async (e) => {
    if (e) e.preventDefault();
    
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      return setError("SIGNAL_ERROR: Invalid Terminal ID");
    }

    setIsLoading(true);
    setError("");

    try {
      // ✅ ENSURE API_BASE_URL points to the correct backend port (e.g., http://localhost:8000)
      const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json" 
        },
        body: JSON.stringify({ email: email }), // Must match ForgotPasswordRequest schema
      });

      // Handle cases where the server is down or unreachable
      if (!response) {
        throw new Error("CONNECTION_LOST: Server Unreachable");
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "RECOVERY_LINK_FAILED");
      }

      // ✅ SUCCESS: The backend prints the OTP in its terminal now
      navigate("/verify-otp", { state: { email } });

    } catch (err) {
      // Catch "Failed to fetch" specifically to give a clearer error
      if (err.message === "Failed to fetch") {
        setError("NETWORK_FAILURE: Check if Backend is running at " + API_BASE_URL);
      } else {
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 bg-[#000507] font-['Exo_2']">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="relative z-10 w-full max-w-md">
        <div className="bg-[#000d12]/95 border border-[#002a35] rounded-3xl p-10 shadow-2xl backdrop-blur-3xl">
          <div className="flex flex-col items-center mb-8">
            <div className="bg-[#38bdf810] p-4 rounded-full border border-[#38bdf830] mb-5 shadow-[0_0_20px_rgba(56,189,248,0.1)]">
              <Lock className="h-10 w-10 text-[#38bdf8]" />
            </div>
            <h1 className="text-3xl font-black font-['Rajdhani'] tracking-widest uppercase text-white">Identity Recovery</h1>
          </div>

          <form onSubmit={handleSendOtp} className="space-y-6">
            <div className="space-y-3">
              <label className="text-xs font-mono text-[#4a7a8a] tracking-widest uppercase">Registered Terminal ID</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#38bdf860]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError(""); }}
                  className="w-full bg-[#001312] border border-[#002a35] rounded-xl px-10 py-4 text-[#c8e6f0] focus:border-[#38bdf8] outline-none font-mono"
                  placeholder="USER_EMAIL@DOMAIN.COM"
                  required
                />
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} className="p-3 border border-red-500/30 bg-red-900/20 rounded-lg">
                  <p className="text-[10px] font-mono uppercase text-red-400 text-center">{error}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-5 bg-gradient-to-r from-[#38bdf8] to-[#00ffe1] text-black font-black font-['Rajdhani'] tracking-[0.2em] rounded-xl transition-all hover:shadow-[0_0_30px_rgba(56,189,248,0.4)] disabled:opacity-50"
            >
              {isLoading ? "Broadcasting..." : "Initialize OTP Transfer"}
            </button>
          </form>

          <button onClick={() => navigate("/login")} className="w-full mt-8 flex items-center justify-center gap-2 text-[10px] font-mono text-[#4a7a8a] hover:text-[#00ffe1] transition-all uppercase tracking-widest">
            <ChevronLeft className="h-3 w-3" /> Return to Login
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default ForgotEmailPage;