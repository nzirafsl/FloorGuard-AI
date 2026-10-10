import { useState } from "react";
import { Users, MessageSquare, ThumbsUp, MapPin, Clock, Send, AlertTriangle } from "lucide-react";

// ── Sample community reports ──────────────────────────────────────────────────
const INITIAL_REPORTS = [
  {
    id: 1,
    author: "Ahmad R.",
    avatar: "A",
    avatarColor: "#1565c0",
    location: "Serdang, Selangor",
    message: "Water level rising near Jalan Serdang Perdana. Road partially flooded.",
    time: "5 min ago",
    likes: 12,
    severity: "high",
  },
  {
    id: 2,
    author: "Nurul H.",
    avatar: "N",
    avatarColor: "#6a1b9a",
    location: "Kajang, Selangor",
    message: "Underpass at Jalan Semenyih is clear. Safe to pass through.",
    time: "18 min ago",
    likes: 8,
    severity: "safe",
  },
  {
    id: 3,
    author: "Lim K.W.",
    avatar: "L",
    avatarColor: "#00695c",
    location: "Bangi, Selangor",
    message: "Heavy rain for past 2 hours. Drains overflowing near Tesco.",
    time: "32 min ago",
    likes: 21,
    severity: "medium",
  },
  {
    id: 4,
    author: "Siti A.",
    avatar: "S",
    avatarColor: "#e65100",
    location: "Putrajaya",
    message: "Precinct 9 roads flooded waist-high. Avoid this area completely.",
    time: "1 hr ago",
    likes: 34,
    severity: "high",
  },
];

const SEVERITY_CONFIG = {
  high:   { color: "#c62828", bg: "#fdecea", label: "⚠ High Risk" },
  medium: { color: "#e65100", bg: "#fff3e0", label: "⚡ Moderate" },
  safe:   { color: "#2e7d32", bg: "#e8f5e9", label: "✓ Safe"     },
};

export default function CommunityHelp() {
  const [reports, setReports]   = useState(INITIAL_REPORTS);
  const [message, setMessage]   = useState("");
  const [location, setLocation] = useState("");
  const [severity, setSeverity] = useState("medium");
  const [liked, setLiked]       = useState(new Set());
  const [posting, setPosting]   = useState(false);

  function handleLike(id) {
    setLiked(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
        setReports(r => r.map(rep => rep.id === id ? { ...rep, likes: rep.likes - 1 } : rep));
      } else {
        next.add(id);
        setReports(r => r.map(rep => rep.id === id ? { ...rep, likes: rep.likes + 1 } : rep));
      }
      return next;
    });
  }

  function handlePost() {
    if (!message.trim() || !location.trim()) return;
    setPosting(true);
    setTimeout(() => {
      const newReport = {
        id:          Date.now(),
        author:      "You",
        avatar:      "Y",
        avatarColor: "#152d4b",
        location:    location.trim(),
        message:     message.trim(),
        time:        "Just now",
        likes:       0,
        severity,
      };
      setReports(prev => [newReport, ...prev]);
      setMessage("");
      setLocation("");
      setSeverity("medium");
      setPosting(false);
    }, 600);
  }

  return (
    <div style={container}>

      {/* ── Page header ── */}
      <div style={pageHeader}>
        <div style={headerIcon}>
          <Users size={22} color="#fff" strokeWidth={2} />
        </div>
        <div>
          <div style={headerTitle}>Community Reports</div>
          <div style={headerSub}>{reports.length} reports in your area</div>
        </div>
      </div>

      {/* ── Post a report ── */}
      <div style={card}>
        <div style={cardTitle}>
          <MessageSquare size={16} color="#152d4b" />
          Share a Report
        </div>

        <input
          style={input}
          placeholder="Your location (e.g. Serdang, Selangor)"
          value={location}
          onChange={e => setLocation(e.target.value)}
        />

        <textarea
          style={textarea}
          placeholder="Describe the flood situation near you…"
          rows={3}
          value={message}
          onChange={e => setMessage(e.target.value)}
        />

        {/* Severity picker */}
        <div style={severityRow}>
          {Object.entries(SEVERITY_CONFIG).map(([key, { color, bg, label }]) => (
            <button
              key={key}
              onClick={() => setSeverity(key)}
              style={{
                ...severityBtn,
                background:  severity === key ? bg : "#f4f7fa",
                color:       severity === key ? color : "#68788b",
                border:      `1.5px solid ${severity === key ? color : "transparent"}`,
                fontWeight:  severity === key ? 700 : 500,
              }}
            >
              {label}
            </button>
          ))}
        </div>

        <button
          onClick={handlePost}
          disabled={!message.trim() || !location.trim() || posting}
          style={{
            ...postBtn,
            opacity: (!message.trim() || !location.trim()) ? 0.5 : 1,
          }}
        >
          <Send size={15} strokeWidth={2.2} />
          {posting ? "Posting…" : "Post Report"}
        </button>
      </div>

      {/* ── Community feed ── */}
      <div style={feedSection}>
        <div style={feedTitle}>Recent Reports</div>
        {reports.map(rep => {
          const sev = SEVERITY_CONFIG[rep.severity] || SEVERITY_CONFIG.medium;
          return (
            <div key={rep.id} style={reportCard}>
              {/* Author row */}
              <div style={authorRow}>
                <div style={{ ...avatar, background: rep.avatarColor }}>
                  {rep.avatar}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={authorName}>{rep.author}</div>
                  <div style={metaRow}>
                    <MapPin size={11} color="#68788b" />
                    <span style={metaText}>{rep.location}</span>
                    <Clock size={11} color="#68788b" />
                    <span style={metaText}>{rep.time}</span>
                  </div>
                </div>
                <span style={{ ...badge, background: sev.bg, color: sev.color }}>
                  {sev.label}
                </span>
              </div>

              {/* Message */}
              <p style={reportMsg}>{rep.message}</p>

              {/* Like */}
              <div style={likeRow}>
                <button
                  onClick={() => handleLike(rep.id)}
                  style={{ ...likeBtn, color: liked.has(rep.id) ? "#1565c0" : "#68788b" }}
                  aria-label="Helpful"
                >
                  <ThumbsUp
                    size={15}
                    strokeWidth={2}
                    fill={liked.has(rep.id) ? "#1565c0" : "none"}
                  />
                  <span>{rep.likes} helpful</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Disclaimer ── */}
      <div style={disclaimer}>
        <AlertTriangle size={13} color="#e65100" />
        Reports are crowd-sourced. Always verify with official sources before acting.
      </div>

    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const container = {
  padding:       "16px 16px 8px",
  display:       "flex",
  flexDirection: "column",
  gap:           14,
};

const pageHeader = {
  display:    "flex",
  alignItems: "center",
  gap:        12,
};

const headerIcon = {
  width:          44,
  height:         44,
  borderRadius:   13,
  background:     "#152d4b",
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  flexShrink:     0,
};

const headerTitle = {
  fontWeight: 700,
  fontSize:   20,
  color:      "#152d4b",
  lineHeight: 1.2,
};

const headerSub = {
  fontSize: 12,
  color:    "#68788b",
  marginTop: 2,
};

const card = {
  background:   "#fff",
  borderRadius: 16,
  padding:      "16px",
  boxShadow:    "0 2px 10px rgba(21,45,75,.07)",
  display:      "flex",
  flexDirection: "column",
  gap:          10,
};

const cardTitle = {
  display:    "flex",
  alignItems: "center",
  gap:        6,
  fontWeight: 700,
  fontSize:   14,
  color:      "#152d4b",
};

const input = {
  border:       "1.5px solid #e4eaf0",
  borderRadius: 10,
  padding:      "10px 12px",
  fontSize:     13,
  color:        "#152d4b",
  outline:      "none",
  width:        "100%",
  boxSizing:    "border-box",
  fontFamily:   "'Inter', system-ui, sans-serif",
};

const textarea = {
  ...input,
  resize:     "none",
  lineHeight: 1.5,
};

const severityRow = {
  display: "flex",
  gap:     8,
};

const severityBtn = {
  flex:         1,
  padding:      "7px 4px",
  borderRadius: 9,
  fontSize:     11,
  cursor:       "pointer",
  textAlign:    "center",
  transition:   "all 0.15s",
  fontFamily:   "'Inter', system-ui, sans-serif",
};

const postBtn = {
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  gap:            7,
  background:     "#152d4b",
  color:          "#fff",
  border:         "none",
  borderRadius:   11,
  padding:        "12px",
  fontWeight:     700,
  fontSize:       14,
  cursor:         "pointer",
  fontFamily:     "'Inter', system-ui, sans-serif",
};

const feedSection = {
  display:       "flex",
  flexDirection: "column",
  gap:           10,
};

const feedTitle = {
  fontWeight: 700,
  fontSize:   15,
  color:      "#152d4b",
};

const reportCard = {
  background:   "#fff",
  borderRadius: 14,
  padding:      "14px",
  boxShadow:    "0 2px 8px rgba(21,45,75,.06)",
  display:      "flex",
  flexDirection: "column",
  gap:          10,
};

const authorRow = {
  display:    "flex",
  alignItems: "flex-start",
  gap:        10,
};

const avatar = {
  width:          36,
  height:         36,
  borderRadius:   "50%",
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  color:          "#fff",
  fontWeight:     700,
  fontSize:       15,
  flexShrink:     0,
};

const authorName = {
  fontWeight: 600,
  fontSize:   13,
  color:      "#152d4b",
};

const metaRow = {
  display:    "flex",
  alignItems: "center",
  gap:        4,
  marginTop:  3,
  flexWrap:   "wrap",
};

const metaText = {
  fontSize: 11,
  color:    "#68788b",
};

const badge = {
  fontSize:     10,
  fontWeight:   700,
  padding:      "3px 8px",
  borderRadius: 100,
  whiteSpace:   "nowrap",
};

const reportMsg = {
  margin:     0,
  fontSize:   13,
  color:      "#2c3e50",
  lineHeight: 1.55,
};

const likeRow = {
  borderTop:  "1px solid #f0f4f8",
  paddingTop: 8,
};

const likeBtn = {
  display:    "flex",
  alignItems: "center",
  gap:        5,
  background: "none",
  border:     "none",
  cursor:     "pointer",
  fontSize:   12,
  fontWeight: 600,
  fontFamily: "'Inter', system-ui, sans-serif",
  padding:    0,
};

const disclaimer = {
  display:     "flex",
  alignItems:  "center",
  gap:         6,
  fontSize:    11,
  color:       "#68788b",
  lineHeight:  1.5,
  paddingBottom: 4,
};
