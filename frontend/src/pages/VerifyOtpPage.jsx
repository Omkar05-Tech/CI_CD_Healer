import React, { useState, useRef, useEffect } from "react";
import { ArrowLeft } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { API_BASE_URL } from "../api/apiConfig";

const VerifyOtpPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Retrieve the email passed from the ForgotPassword page
  const email = location.state?.email || "";
  
  const OTP_LENGTH = 6;
  const otpRefs = useRef([]);
  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(""));
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Redirect back if no email is present in state
  useEffect(() => {
    if (!email) {
      navigate("/forgot-email");
    }
  }, [email, navigate]);

  /**
   * ✅ BACKEND MAPPING: VERIFY OTP
   * Endpoint: POST /api/auth/verify-otp (from auth_routes.py)
   * Schema: VerifyOtpRequest { email, otp }
   */
  const handleVerify = async () => {
    const otpCode = otp.join("");
    
    if (otpCode.length !== OTP_LENGTH) {
      return setError("Enter complete 6-digit OTP");
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email, // Required by backend schema
          otp: otpCode   // Required by backend schema
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Verification failed");
      }

      // ✅ SUCCESS: Move to reset password page and pass email/otp for the final step
      navigate("/reset-password", { 
        state: { email, otp: otpCode } 
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#000507] flex items-center justify-center px-4 font-['Exo_2']">
      <div className="w-full max-w-md bg-[#000d12]/95 border border-[#002a35] rounded-3xl p-8 shadow-2xl backdrop-blur-3xl">

        <button
          onClick={() => navigate("/forgot-email")}
          className="text-xs font-mono text-[#4a7a8a] uppercase tracking-widest flex items-center gap-2 mb-6 hover:text-[#00ffe1] transition-colors"
        >
          <ArrowLeft className="h-4" /> Back to Terminal
        </button>

        <h2 className="text-2xl font-bold font-['Rajdhani'] text-white uppercase tracking-wider mb-2">Verify Protocol</h2>
        <p className="text-sm font-mono text-[#4a7a8a] mb-8">Enter the 6-digit decryption key sent to {email || "your email"}</p>

        {/* OTP Inputs */}
        <div className="flex justify-between gap-2 my-6">
          {otp.map((val, idx) => (
            <input
              key={idx}
              ref={(el) => (otpRefs.current[idx] = el)}
              maxLength={1}
              inputMode="numeric"
              className="w-12 h-14 text-center text-2xl font-bold bg-[#001312] border-2 border-[#002a35] rounded-xl text-[#00ffe1] focus:border-[#00ffe1] focus:ring-1 focus:ring-[#00ffe1] outline-none transition-all"
              value={val}
              onChange={(e) => {
                const v = e.target.value.replace(/[^0-9]/g, "");
                if (!v && e.nativeEvent.inputType === "deleteContentBackward") return; // Handled by onKeyDown
                
                const arr = [...otp];
                arr[idx] = v.substring(v.length - 1);
                setOtp(arr);
                
                if (v && idx < OTP_LENGTH - 1) otpRefs.current[idx + 1].focus();
                setError("");
              }}
              onKeyDown={(e) => {
                if (e.key === "Backspace" && !otp[idx] && idx > 0) {
                  otpRefs.current[idx - 1].focus();
                }
              }}
            />
          ))}
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900/20 border border-red-500/50 rounded-lg">
            <p className="text-red-400 text-[10px] font-mono uppercase text-center">{error}</p>
          </div>
        )}

        <button
          onClick={handleVerify}
          disabled={isLoading}
          className="w-full py-4 bg-gradient-to-r from-[#00ffe1] to-[#38bdf8] text-black font-black font-['Rajdhani'] tracking-[0.2em] rounded-xl hover:shadow-[0_0_20px_rgba(0,255,225,0.3)] transition-all active:scale-95 disabled:opacity-50 uppercase"
        >
          {isLoading ? "Validating..." : "Execute Verification"}
        </button>
      </div>
    </div>
  );
};

export default VerifyOtpPage;