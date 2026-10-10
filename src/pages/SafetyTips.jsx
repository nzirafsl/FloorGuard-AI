import { Shield, AlertTriangle, Package, Droplets } from "lucide-react";

const TIPS = [
  { Icon: AlertTriangle, title: "Monitor rainfall and official forecasts",       body: "Check MET Malaysia updates before travel."                              },
  { Icon: Droplets,      title: "Avoid entering floodwater",                     body: "Even shallow water can be dangerous. Ask local authorities first."       },
  { Icon: Package,       title: "Prepare essential supplies if flood-prone",     body: "Keep documents, medication, water and a charged phone ready."            },
  { Icon: Shield,        title: "Follow official JPS and NADMA instructions",    body: "AI guidance is not a substitute for official warnings."                  },
];

export default function SafetyTips() {
  return (
    <div style={{ padding: "20px 20px 20px" }}>
      <div style={{ fontSize: 22, fontWeight: 800, color: "#152d4b", marginBottom: 4 }}>AI Safety Tips</div>
      <div style={{ fontSize: 13, color: "#68788b", marginBottom: 20, lineHeight: 1.5 }}>
        Practical advice for changing conditions. AI guidance is not an official warning.
      </div>

      {/* Current risk card */}
      <div style={{ background: "#fff", borderRadius: 16, padding: 16, border: "1px solid #e4eaf0", marginBottom: 20, boxShadow: "0 2px 8px rgba(21,45,75,.05)" }}>
        <div style={{ fontWeight: 700, fontSize: 14, color: "#152d4b", marginBottom: 10 }}>Current flood risk</div>
        <span style={{ background: "#d64045", color: "#fff", padding: "5px 16px", borderRadius: 99, fontSize: 13, fontWeight: 700 }}>
          HIGH RISK
        </span>
        <span style={{ float: "right", fontSize: 12, color: "#68788b", marginTop: 4 }}>Estimated</span>
        <div style={{ clear: "both", marginTop: 10, fontSize: 12, color: "#68788b" }}>AI guidance is not an official warning.</div>
      </div>

      <div style={{ fontWeight: 700, fontSize: 14, color: "#152d4b", marginBottom: 6 }}>Practical safety tips</div>
      <div style={{ fontSize: 12, color: "#68788b", marginBottom: 14 }}>Practical advice for changing conditions.</div>

      {TIPS.map(({ Icon, title, body }) => (
        <div key={title} style={{ display: "flex", alignItems: "flex-start", gap: 14, background: "#fff", borderRadius: 14, padding: "14px 16px", marginBottom: 10, border: "1px solid #e4eaf0" }}>
          <div style={{ background: "#f4f7fa", borderRadius: 10, padding: 8, flexShrink: 0 }}>
            <Icon size={18} color="#152d4b" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, color: "#152d4b", lineHeight: 1.3 }}>{title}</div>
            <div style={{ fontSize: 12, color: "#68788b", marginTop: 3, lineHeight: 1.45 }}>{body}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
