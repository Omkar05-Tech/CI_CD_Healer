import React, { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { User, Mail, Lock, Activity, ShieldPlus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import { useAuthStore } from '../authStore';
import { API_BASE_URL } from "../api/apiConfig";

// --- Decrypting Text Hook ---
const useScrambleText = (text, isScrambling) => {
  const [displayText, setDisplayText] = useState(text);
  const chars = "!<>-_\\/[]{}—=+*^?#________";

  useEffect(() => {
    if (!isScrambling) {
      setDisplayText(text);
      return;
    }
    let iteration = 0;
    const interval = setInterval(() => {
      setDisplayText(prev => 
        text.split("").map((letter, index) => {
          if (index < iteration) return text[index];
          return chars[Math.floor(Math.random() * chars.length)];
        }).join("")
      );
      iteration += 1 / 3;
      if (iteration >= text.length) clearInterval(interval);
    }, 30);
    return () => clearInterval(interval);
  }, [isScrambling, text]);

  return displayText;
};

// --- Background HUD Component ---
const BackgroundHUD = ({ isMobile }) => {
  if (isMobile) {
    return <div className="fixed inset-0 z-0 bg-[#00080a]" />;
  }

  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none bg-[#000507]">
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent_50%,rgba(0,255,225,0.02)_50%)] bg-[length:100%_4px] animate-pulse" />
      <div 
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `linear-gradient(#00ffe1 1px, transparent 1px), linear-gradient(90deg, #00ffe1 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          transform: 'perspective(600px) rotateX(65deg) translateY(0)',
          animation: 'grid-advance 15s linear infinite'
        }}
      />
      <style>{`
        @keyframes grid-advance {
          from { background-position: 0 0; }
          to { background-position: 0 600px; }
        }
      `}</style>
    </div>
  );
};

const SignupPage = () => {
  const navigate = useNavigate();
  const loginWithToken = useAuthStore((state) => state.loginWithToken);
  
  const [full_name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [init, setInit] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  const scrambledButtonText = useScrambleText("INITIALIZING...", isLoading);

  useEffect(() => {
    const checkRes = () => setIsMobile(window.innerWidth < 1024);
    checkRes();
    window.addEventListener('resize', checkRes);
    
    if (!isMobile) {
      initParticlesEngine(async (engine) => {
        await loadSlim(engine);
      }).then(() => setInit(true));
    }

    return () => window.removeEventListener('resize', checkRes);
  }, [isMobile]);

  const playSound = (type) => {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    if (type === 'click') {
      oscillator.type = 'square';
      oscillator.frequency.setValueAtTime(120, audioCtx.currentTime);
      gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime);
      oscillator.start();
      oscillator.stop(audioCtx.currentTime + 0.1);
    }
  };

  /**
   * ✅ BACKEND MAPPING: REGISTER USER
   * Endpoint: POST /api/users/ (from user_routes.py)
   * Schema: UserCreate { email, password, full_name }
   */
  const handleSignup = async (e) => {
    e.preventDefault();
    playSound('click');
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    const userData = { full_name, email, password };
    try {
      // Corrected API path to match your user_routes.py tags
      const response = await fetch(`${API_BASE_URL}/api/users/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        let errorMsg = `Error: ${response.status}`;
        try {
          const errorData = await response.json();
          // FastAPI returns errors in a "detail" field
          errorMsg = errorData.detail || errorMsg;
        } catch (jsonError) {}
        throw new Error(errorMsg);
      }

      setSuccess("PROTOCOL_SUCCESS: Entity Created. Redirecting to Login...");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * ✅ BACKEND MAPPING: GOOGLE OAUTH
   * Endpoint: GET /api/auth/login/google (from auth_routes.py)
   */
  const handleGoogleSignup = () => {
    playSound('click');
    // Mapped to the specific OAuth login route in your auth_routes.py
    const backendUrl = `${API_BASE_URL}/api/auth/login/google`;
    window.open(backendUrl, "oauth-login", "width=500,height=600");
  };

  useEffect(() => {
    const handleAuthMessage = (event) => {
      // Security: Validate message origin if needed
      const { token } = event.data;
      if (token) {
        const user = loginWithToken(token);
        if (user) navigate("/app/dashboard", { replace: true });
      }
    };
    window.addEventListener("message", handleAuthMessage);
    return () => window.removeEventListener("message", handleAuthMessage);
  }, [loginWithToken, navigate]);

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 sm:p-6 font-['Exo_2'] selection:bg-[#00ffe120] antialiased">
      <BackgroundHUD isMobile={isMobile} />
      
      {init && !isMobile && (
        <Particles
          id="tsparticles"
          options={{
            fullScreen: { enable: false },
            particles: {
              number: { value: 50, density: { enable: true, area: 1000 } },
              color: { value: "#00ffe1" },
              shape: { type: "square" },
              opacity: { value: { min: 0.1, max: 0.3 } },
              size: { value: { min: 1, max: 2 } },
              move: { enable: true, speed: 0.6, direction: "top", outModes: "out" },
            }
          }}
          className="absolute inset-0 z-0"
        />
      )}

      <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="relative z-10 w-full max-w-sm sm:max-w-md">
        <div className={`
          bg-[#000d12]/95 border border-[#002a35] rounded-3xl p-6 sm:p-10 shadow-2xl overflow-hidden
          ${!isMobile ? 'backdrop-blur-3xl' : 'shadow-[#00ffe105]'}
        `}>
          
          <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#a78bfa] to-transparent" />
          
          <div className="flex flex-col items-center mb-6 sm:mb-10">
            <div className="bg-[#a78bfa10] p-3 sm:p-4 rounded-full border border-[#a78bfa30] mb-3 sm:mb-5 shadow-[0_0_20px_rgba(167,139,250,0.1)]">
              <ShieldPlus className="h-8 w-8 sm:h-12 sm:w-12 text-[#a78bfa]" />
            </div>
            <h1 className="text-2xl sm:text-4xl font-black font-['Rajdhani'] tracking-[0.15em] uppercase text-white text-center leading-tight">Create Entity</h1>
            <div className="flex items-center gap-2 mt-2">
              <Activity className="h-3 w-3 text-[#00ffe1] animate-pulse" />
              <p className="text-[10px] sm:text-sm font-mono text-[#4a7a8a] tracking-widest uppercase">Registration Protocol</p>
            </div>
          </div>

          <form onSubmit={handleSignup} className="space-y-4 sm:space-y-7">
            {/* FULL NAME */}
            <div className="space-y-1.5 sm:space-y-3">
              <label className="text-[10px] sm:text-sm font-mono text-[#4a7a8a] tracking-widest uppercase ml-1 block">Full Name</label>
              <div className="relative group">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#a78bfa60] group-focus-within:text-[#a78bfa] transition-colors" />
                <input
                  type="text"
                  value={full_name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#001312] border border-[#002a35] rounded-xl px-10 py-3 sm:py-5 text-xs sm:text-base text-[#c8e6f0] focus:border-[#a78bfa] outline-none font-mono transition-all placeholder:opacity-20"
                  placeholder="USER_NAME"
                  required
                />
              </div>
            </div>

            {/* EMAIL */}
            <div className="space-y-1.5 sm:space-y-3">
              <label className="text-[10px] sm:text-sm font-mono text-[#4a7a8a] tracking-widest uppercase ml-1 block">Terminal ID / Email</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#00ffe160] group-focus-within:text-[#00ffe1] transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#001312] border border-[#002a35] rounded-xl px-10 py-3 sm:py-5 text-xs sm:text-base text-[#c8e6f0] focus:border-[#00ffe1] outline-none font-mono transition-all placeholder:opacity-20"
                  placeholder="EMAIL_IDENTIFIER"
                  required
                />
              </div>
            </div>

            {/* PASSWORD */}
            <div className="space-y-1.5 sm:space-y-3">
              <label className="text-[10px] sm:text-sm font-mono text-[#4a7a8a] tracking-widest uppercase ml-1 block">Security Key / Password</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#38bdf860] group-focus-within:text-[#38bdf8] transition-colors" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#001312] border border-[#002a35] rounded-xl px-10 py-3 sm:py-5 text-xs sm:text-base text-[#c8e6f0] focus:border-[#38bdf8] outline-none font-mono transition-all placeholder:opacity-20"
                  placeholder="PASS_PHRASE"
                  required
                  minLength="5"
                />
              </div>
            </div>

            <AnimatePresence>
              {(error || success) && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className={`p-3 border rounded-lg text-center ${error ? 'bg-red-900/20 border-red-500/50' : 'bg-green-900/20 border-green-500/50'}`}>
                  <p className={`text-[10px] font-mono uppercase tracking-tighter ${error ? 'text-red-400' : 'text-green-400'}`}>
                    {error ? `ERROR: ${error}` : success}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 sm:py-6 bg-gradient-to-r from-[#a78bfa] to-[#38bdf8] text-black font-black font-['Rajdhani'] tracking-[0.2em] sm:tracking-[0.3em] rounded-xl relative group overflow-hidden transition-all hover:shadow-[0_0_30px_rgba(167,139,250,0.4)] active:scale-95 disabled:opacity-50 uppercase text-xs sm:text-base"
            >
              <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              <span className="relative z-10">
                {isLoading ? scrambledButtonText : "Initialize Entity"}
              </span>
            </button>
          </form>

          {/* SOCIAL SYNC */}
          <div className="mt-6 sm:mt-10">
            <div className="flex items-center gap-4 mb-4 sm:mb-8 text-[#4a7a8a]">
              <div className="h-[1px] flex-1 bg-[#002a35]" />
              <span className="text-[10px] font-mono tracking-widest uppercase opacity-60">Federated Sync</span>
              <div className="h-[1px] flex-1 bg-[#002a35]" />
            </div>

            <button 
              onClick={handleGoogleSignup}
              className="w-full flex items-center justify-center gap-3 py-3 border border-[#00ffe130] rounded-xl text-[10px] sm:text-sm font-mono uppercase tracking-[0.1em] sm:tracking-[0.2em] text-[#00ffe1] hover:bg-[#00ffe105] hover:border-[#00ffe1] transition-all"
            >
              Synchronize with Google
            </button>
          </div>

          <p className="text-center text-[10px] sm:text-sm font-mono text-[#4a7a8a] mt-6 sm:mt-10 tracking-widest uppercase">
            Already Recognized?{" "}
            <Link to="/login" className="text-[#00ffe1] font-bold border-b border-[#00ffe1]/30 hover:border-[#00ffe1] transition-colors">
              Log In
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default SignupPage;