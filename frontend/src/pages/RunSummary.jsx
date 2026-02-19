import React from "react";

const SummaryField = ({ label, value, color = "text-white" }) => (
  <div className="space-y-2">
    <p className="text-[8px] font-mono text-[#4a7a8a] tracking-[0.3em] uppercase">{label}</p>
    <div className={`text-xs font-mono ${color} truncate`}>{value}</div>
  </div>
);

const RunSummary = ({ formData, branchName }) => {
  return (
    <div className="space-y-8">
      {/* 2x2 Info Grid */}
      <div className="grid grid-cols-2 gap-x-12 gap-y-8">
        <SummaryField label="Repository" value={formData.repoUrl} />
        <SummaryField label="Branch" value={branchName} color="text-[#00ffe1]" />
        <SummaryField label="Team" value={formData.teamName} />
        <SummaryField label="Leader" value={formData.leaderName} />
      </div>

      {/* CI/CD Status Bar */}
      <div className="bg-[#00ffe108] border border-[#00ffe120] p-6 rounded-xl flex items-center gap-6 shadow-[inset_0_0_20px_rgba(0,255,225,0.02)]">
        <div className="relative">
          <div className="w-4 h-4 rounded-full bg-[#00ffe1] shadow-[0_0_15px_#00ffe1] animate-pulse" />
          <div className="absolute inset-[-6px] rounded-full border border-[#00ffe130] animate-ping" />
        </div>
        <div className="space-y-1">
          <div className="text-sm font-bold font-['Rajdhani'] text-[#00ffe1] tracking-[0.5em] uppercase">
            CI/CD Pipeline — Passed
          </div>
          <div className="text-[9px] font-mono text-[#4a7a8a] tracking-widest">
            5 commits • branch protected • tests green
          </div>
        </div>
      </div>
    </div>
  );
};

export default RunSummary;