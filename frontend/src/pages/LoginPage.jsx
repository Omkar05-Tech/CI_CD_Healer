import React, { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, ShieldCheck, Activity } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from '../authStore';
import { API_BASE_URL } from "../api/apiConfig";

const BackgroundEffects = ({ isMobile }) => {
  if (isMobile) {
    return <div className="fixed inset-0 z-0 bg-[#00080a]" />;
  }

  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none bg-[#000507]">
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent_50%,rgba(0,255,225,0.03)_50%)] bg-[length:100%_4px] animate-pulse" />
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `linear-gradient(#00ffe1 1px, transparent 1px), linear-gradient(90deg, #00ffe1 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
          transform: 'perspective(500px) rotateX(60deg) translateY(0)',
          animation: 'grid-move 20s linear infinite'
        }}
      />
      <style>{`
        @keyframes grid-move {
          from { background-position: 0 0; }
          to { background-position: 0 500px; }
        }
      `}</style>
    </div>
  );
};

const LoginPage = () => {
  const navigate = useNavigate();
  
  // Destructure exactly what we need
  const loginWithToken = useAuthStore((state) => state.loginWithToken);
  const isLoading = useAuthStore((state) => state.loading);
  
  const [email, setEmail] = useState("user@example.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkRes = () => setIsMobile(window.innerWidth < 1024);
    checkRes();
    window.addEventListener('resize', checkRes);
    return () => window.removeEventListener('resize', checkRes);
  }, []);

  const playSound = useCallback((type) => {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    if (type === 'click') {
      oscillator.type = 'square';
      oscillator.frequency.setValueAtTime(150, audioCtx.currentTime);
      gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
      oscillator.start();
      oscillator.stop(audioCtx.currentTime + 0.1);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    playSound('click');
    setError(null);

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Invalid credentials");
      }

      loginWithToken(data.access_token);
      navigate("/app/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Invalid credentials");
    }
  };

  const handleGoogleLogin = () => {
    playSound('click');
    const backendUrl = `${API_BASE_URL}/api/auth/login/google`;
    window.open(backendUrl, "oauth-login", "width=500,height=600");
  };

  // ✅ FIXED: Listener uses a clean event handler and specific logic to stop loops
  useEffect(() => {
    const handleAuthMessage = (event) => {
      // Check if the data exists and contains a token
      if (event.data && event.data.token) {
        loginWithToken(event.data.token);
        // Using replace: true prevents the user from going back to the login page via history
        navigate("/app/dashboard", { replace: true });
      }
    };

    window.addEventListener("message", handleAuthMessage);
    return () => window.removeEventListener("message", handleAuthMessage);
  }, [navigate, loginWithToken]); // Stable references

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 sm:p-6 font-['Exo_2'] selection:bg-[#00ffe120] antialiased">
      <BackgroundEffects isMobile={isMobile} />

      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 w-full max-w-sm sm:max-w-md"
      >
        <div className={`
          bg-[#000d12]/95 border border-[#002a35] rounded-3xl p-6 sm:p-10 shadow-2xl overflow-hidden
          ${!isMobile ? 'backdrop-blur-3xl' : 'shadow-[#00ffe105]'}
        `}>
          
          <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#00ffe1] to-transparent opacity-50" />
          
          <div className="flex flex-col items-center mb-6 sm:mb-10">
            <div className="bg-[#00ffe110] p-3 sm:p-4 rounded-full border border-[#00ffe130] mb-3 sm:mb-5 shadow-[0_0_20px_rgba(0,255,225,0.05)]">
              <ShieldCheck className="h-8 w-8 sm:h-12 sm:w-12 text-[#00ffe1]" />
            </div>
            <h1 className="text-2xl sm:text-4xl font-bold font-['Rajdhani'] tracking-[0.15em] uppercase text-white text-center leading-tight">
              Authorized <br className="lg:hidden" /> Access
            </h1>
            <div className="flex items-center gap-2 mt-2">
              <Activity className="h-3 w-3 text-[#38bdf8] animate-pulse" />
              <p className="text-[10px] sm:text-sm font-mono text-[#4a7a8a] tracking-widest uppercase">
                Verification Protocol
              </p>
            </div>
          </div>

          <form onSubmit={handleLogin} className="space-y-4 sm:space-y-7">
            <div className="space-y-1.5 sm:space-y-3">
              <label className="text-[10px] sm:text-sm font-mono text-[#4a7a8a] tracking-widest uppercase ml-1 block">
                Terminal ID / Email
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#00ffe140] group-focus-within:text-[#00ffe1] transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#001312] border border-[#002a35] rounded-xl px-10 py-3 sm:py-5 text-xs sm:text-base text-[#c8e6f0] focus:border-[#00ffe1] outline-none font-mono transition-all placeholder:opacity-30"
                  placeholder="USER_NAME@DOMAIN.COM"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5 sm:space-y-3">
              <div className="flex justify-between items-center px-1">
                <label className="text-[10px] sm:text-sm font-mono text-[#4a7a8a] tracking-widest uppercase block">
                  Access Key / Password
                </label>
                <button type="button" onClick={() => navigate("/forgot-email")} className="text-[10px] font-mono text-[#38bdf8] uppercase tracking-tighter hover:text-[#00ffe1] transition-colors">
                  RECOVERY
                </button>
              </div>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#00ffe140] group-focus-within:text-[#00ffe1] transition-colors" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#001312] border border-[#002a35] rounded-xl px-10 py-3 sm:py-5 text-xs sm:text-base text-[#c8e6f0] focus:border-[#00ffe1] outline-none font-mono transition-all"
                  placeholder="••••••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 sm:py-6 bg-gradient-to-r from-[#00ffe1] to-[#38bdf8] text-black font-black font-['Rajdhani'] tracking-[0.2em] sm:tracking-[0.3em] rounded-xl transition-all hover:shadow-[0_0_30px_rgba(0,255,225,0.4)] disabled:opacity-50 active:scale-95 uppercase text-xs sm:text-base shadow-lg shadow-[#00ffe110]"
            >
              {isLoading ? "Verifying..." : "Initialize Session"}
            </button>
          </form>

          <div className="mt-6 sm:mt-10">
            <div className="flex items-center gap-4 mb-4 sm:mb-8 text-[#4a7a8a]">
              <div className="h-[1px] flex-1 bg-[#002a35]" />
              <span className="text-[10px] font-mono tracking-widest uppercase opacity-60">External Auth</span>
              <div className="h-[1px] flex-1 bg-[#002a35]" />
            </div>

            <button 
              type="button"
              onClick={handleGoogleLogin}
              className="w-full flex items-center justify-center gap-3 py-3 border border-[#002a35] rounded-xl text-[10px] sm:text-sm font-mono uppercase tracking-[0.1em] sm:tracking-[0.2em] text-[#00ffe1] hover:bg-[#00ffe105] transition-all"
            >
              Google Auth Interface
            </button>
          </div>

          <p className="text-center text-[10px] sm:text-sm font-mono text-[#4a7a8a] mt-6 sm:mt-10 tracking-widest uppercase">
            New Entity? <Link to="/signup" className="text-[#00ffe1] font-bold border-b border-[#00ffe1]/30 hover:border-[#00ffe1] transition-colors">Register ID</Link>
          </p>

          <AnimatePresence>
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 p-3 border border-red-500/30 bg-red-500/10 rounded-lg text-center"
              >
                 <p className="text-[10px] font-mono text-red-400 uppercase tracking-tighter">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;