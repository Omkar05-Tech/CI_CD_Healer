import React from "react";

const FixesTable = () => {
  const fixes = [
    { file: "src/utils.py", type: "LINTING", line: 15, msg: "[AI-AGENT] Remove unused import 'os'", status: "FIXED", color: "#00ffe1" },
    { file: "src/validator.py", type: "SYNTAX", line: 8, msg: "[AI-AGENT] Add missing colon after if block", status: "FIXED", color: "#ff4d6d" },
    { file: "src/models.py", type: "TYPE_ERROR", line: 42, msg: "[AI-AGENT] Cast str→int in return value", status: "FIXED", color: "#facc15" },
    { file: "src/api.py", type: "IMPORT", line: 3, msg: "[AI-AGENT] Resolve circular import in api", status: "FIXED", color: "#38bdf8" },
    { file: "src/helpers.py", type: "LOGIC", line: 77, msg: "[AI-AGENT] Fix off-by-one in loop range", status: "FAILED", color: "#a78bfa" },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-separate border-spacing-y-6">
        <thead>
          <tr className="text-[14px] font-mono text-[#4a7a8a] uppercase tracking-[0.4em]">
            <th className="px-6 pb-4">File</th>
            <th className="px-6 pb-4">Bug Type</th>
            <th className="px-6 pb-4">Line</th>
            <th className="px-6 pb-4">Commit Message</th>
            <th className="px-6 pb-4 text-center">Status</th>
          </tr>
        </thead>
        <tbody className="text-[15px] font-mono">
          {fixes.map((f, i) => (
            <tr key={i} className="group transition-all hover:bg-white/5 border-b border-white/5">
              <td className="py-6 px-6 text-[#c8e6f0]/80 font-medium">{f.file}</td>
              <td className="py-6 px-6">
                <span 
                  className="px-5 py-2 rounded-full border-2 text-[12px] font-black tracking-widest uppercase"
                  style={{ borderColor: `${f.color}60`, color: f.color, backgroundColor: `${f.color}15` }}
                >
                  {f.type}
                </span>
              </td>
              <td className="py-6 px-6 text-[#38bdf8] font-black text-lg">{f.line}</td>
              <td className="py-6 px-6 max-w-[300px]">
                <p className="text-[#00ffe1] font-black mb-1 text-[16px]">{f.msg.split(']')[0]}]</p>
                <p className="text-[#4a7a8a] text-[13px] font-medium leading-relaxed">{f.msg.split(']')[1]}</p>
              </td>
              <td className="py-6 px-6">
                <div className="flex flex-col items-center justify-center gap-1">
                  <span className="text-2xl" style={{ color: f.status === "FIXED" ? "#00ffe1" : "#ff4d6d" }}>
                    {f.status === "FIXED" ? "✓" : "X"}
                  </span>
                  <span className="tracking-[0.3em] font-black uppercase text-[10px]" style={{ color: f.status === "FIXED" ? "#00ffe1" : "#ff4d6d" }}>
                    {f.status}
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FixesTable;