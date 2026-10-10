import { useState } from "react";
import {
  LifeBuoy,
  Truck,
  Package,
  Users,
  ChevronRight,
  Plus,
  X,
  MapPin,
  Clock,
  Flag,
  Info,
} from "lucide-react";

// ── Design tokens ──────────────────────────────────────────────────────────────
const C = {
  navy:    "#152d4b",
  muted:   "#68788b",
  border:  "#e4eaf0",
  bg:      "#f4f7fa",
  surface: "#ffffff",
  green:   "#23875b",
  greenBg: "#e8f5ee",
};

// Category config: icon, colour accent, label
const CATEGORIES = [
  { key: "all",       label: "All",       Icon: null,     color: C.navy   },
  { key: "transport", label: "Transport", Icon: Truck,    color: "#b77810" },
  { key: "supplies",  label: "Supplies",  Icon: Package,  color: "#2563eb" },
  { key: "other",     label: "Other",     Icon: Users,    color: "#7c3aed" },
];

// Seed data — matches the schema in crowd_reports.csv / community screen
const INITIAL_REQUESTS = [
  {
    id: 1,
    category:  "transport",
    title:     "Transport assistance needed",
    status:    "Pending verification",
    area:      "Serdang area",
    approx:    true,
    time:      "09:30",
    details:   "Family of 4 stranded at Jalan Equine. Need transport to Sekolah Kebangsaan Serdang shelter.",
  },
  {
    id: 2,
    category:  "supplies",
    title:     "Essential supplies requested",
    status:    "Pending verification",
    area:      "Seri Kembangan area",
    approx:    true,
    time:      "10:00",
    details:   "Running low on drinking water and infant formula. 3rd floor, Block B, Taman Equine.",
  },
];

// ── Sub-components ─────────────────────────────────────────────────────────────

function CategoryChip({ cat, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        display:      "flex",
        alignItems:   "center",
        gap:          5,
        padding:      "6px 14px",
        borderRadius: 99,
        border:       `1.5px solid ${active ? cat.color : C.border}`,
        background:   active ? cat.color : C.surface,
        color:        active ? "#fff" : C.navy,
        fontSize:     13,
        fontWeight:   600,
        whiteSpace:   "nowrap",
        cursor:       "pointer",
        flexShrink:   0,
        transition:   "background 0.15s, color 0.15s",
      }}
    >
      {cat.Icon && <cat.Icon size={13} />}
      {cat.label}
    </button>
  );
}

function RequestCard({ req, onReport }) {
  const [expanded, setExpanded] = useState(false);
  const cat = CATEGORIES.find((c) => c.key === req.category) ?? CATEGORIES[3];

  return (
    <div
      style={{
        background:   C.surface,
        borderRadius: 16,
        padding:      "16px",
        marginBottom: 10,
        border:       `1px solid ${C.border}`,
        boxShadow:    "0 1px 4px rgba(21,45,75,.05)",
      }}
    >
      {/* Category label */}
      <div
        style={{
          fontSize:      11,
          fontWeight:    700,
          color:         cat.color,
          textTransform: "uppercase",
          letterSpacing: ".6px",
          marginBottom:  5,
          display:       "flex",
          alignItems:    "center",
          gap:           4,
        }}
      >
        {cat.Icon && <cat.Icon size={11} />}
        {cat.label}
      </div>

      {/* Title */}
      <div style={{ fontSize: 16, fontWeight: 800, color: C.navy, lineHeight: 1.3, marginBottom: 8 }}>
        {req.title}
      </div>

      {/* Status badge */}
      <span
        style={{
          display:      "inline-block",
          padding:      "3px 10px",
          borderRadius: 99,
          fontSize:     11,
          fontWeight:   600,
          background:   C.bg,
          color:        C.muted,
          border:       `1px solid ${C.border}`,
          marginBottom: 10,
        }}
      >
        {req.status}
      </span>

      {/* Meta */}
      <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, color: C.muted, marginBottom: 3 }}>
        <MapPin size={12} />
        {req.area}{req.approx ? " · Approximate location" : ""}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, color: C.muted, marginBottom: 10 }}>
        <Clock size={12} />
        {req.time}
      </div>

      {/* Expanded details */}
      {expanded && (
        <div
          style={{
            background:   C.bg,
            borderRadius: 10,
            padding:      "10px 12px",
            fontSize:     13,
            color:        C.navy,
            lineHeight:   1.5,
            marginBottom: 10,
          }}
        >
          {req.details}
        </div>
      )}

      {/* Footer row */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <button
          onClick={() => setExpanded((v) => !v)}
          style={{
            display:    "flex",
            alignItems: "center",
            gap:        4,
            fontSize:   13,
            fontWeight: 700,
            color:      C.navy,
            background: "none",
            border:     "none",
            cursor:     "pointer",
            padding:    0,
          }}
        >
          {expanded ? "Hide Details" : "View Details"}
          <ChevronRight
            size={15}
            style={{ transform: expanded ? "rotate(90deg)" : "none", transition: "transform 0.15s" }}
          />
        </button>

        <button
          onClick={() => onReport(req.id)}
          style={{
            display:    "flex",
            alignItems: "center",
            gap:        4,
            fontSize:   12,
            fontWeight: 600,
            color:      C.muted,
            background: "none",
            border:     "none",
            cursor:     "pointer",
            padding:    0,
          }}
        >
          <Flag size={13} />
          Report
        </button>
      </div>
    </div>
  );
}

// ── Submit modal ───────────────────────────────────────────────────────────────
function SubmitModal({ onClose, onSubmit }) {
  const [category, setCategory] = useState("transport");
  const [title,    setTitle]    = useState("");
  const [area,     setArea]     = useState("");
  const [details,  setDetails]  = useState("");

  function handleSubmit() {
    if (!title.trim() || !area.trim()) return;
    onSubmit({ category, title: title.trim(), area: area.trim(), details: details.trim() });
  }

  const inputStyle = {
    width:        "100%",
    height:       46,
    borderRadius: 12,
    border:       `1.5px solid ${C.border}`,
    padding:      "0 14px",
    fontSize:     14,
    color:        C.navy,
    background:   C.surface,
    outline:      "none",
    fontFamily:   "inherit",
    marginBottom: 12,
  };

  return (
    <div
      onClick={onClose}
      style={{
        position:       "fixed",
        inset:          0,
        background:     "rgba(21,45,75,0.55)",
        display:        "flex",
        alignItems:     "flex-end",
        justifyContent: "center",
        zIndex:         1000,
        backdropFilter: "blur(2px)",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width:        "100%",
          maxWidth:     390,
          background:   C.surface,
          borderRadius: "24px 24px 0 0",
          padding:      "0 0 32px",
          boxShadow:    "0 -8px 40px rgba(21,45,75,0.18)",
          animation:    "slideUp 0.2s ease-out",
          maxHeight:    "90dvh",
          overflowY:    "auto",
        }}
      >
        {/* Handle */}
        <div style={{ display: "flex", justifyContent: "center", padding: "12px 0 4px" }}>
          <div style={{ width: 40, height: 4, borderRadius: 99, background: C.border }} />
        </div>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 20px 16px" }}>
          <span style={{ fontWeight: 800, fontSize: 18, color: C.navy }}>New Help Request</span>
          <button onClick={onClose} style={{ background: C.bg, border: "none", borderRadius: 99, padding: 6, cursor: "pointer", display: "flex" }}>
            <X size={18} color={C.muted} />
          </button>
        </div>

        <div style={{ padding: "0 20px" }}>
          {/* Category picker */}
          <div style={{ fontSize: 12, fontWeight: 700, color: C.muted, textTransform: "uppercase", letterSpacing: "1px", marginBottom: 8 }}>
            Category
          </div>
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            {CATEGORIES.slice(1).map((cat) => (
              <button
                key={cat.key}
                onClick={() => setCategory(cat.key)}
                style={{
                  flex:         1,
                  height:       38,
                  borderRadius: 10,
                  border:       `1.5px solid ${category === cat.key ? cat.color : C.border}`,
                  background:   category === cat.key ? `${cat.color}15` : C.surface,
                  color:        category === cat.key ? cat.color : C.muted,
                  fontSize:     12,
                  fontWeight:   700,
                  cursor:       "pointer",
                  display:      "flex",
                  alignItems:   "center",
                  justifyContent: "center",
                  gap:          4,
                }}
              >
                <cat.Icon size={13} /> {cat.label}
              </button>
            ))}
          </div>

          {/* Title */}
          <div style={{ fontSize: 12, fontWeight: 700, color: C.muted, textTransform: "uppercase", letterSpacing: "1px", marginBottom: 6 }}>
            What do you need? *
          </div>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Transport to nearest shelter"
            style={inputStyle}
          />

          {/* Area */}
          <div style={{ fontSize: 12, fontWeight: 700, color: C.muted, textTransform: "uppercase", letterSpacing: "1px", marginBottom: 6 }}>
            Your area *
          </div>
          <input
            value={area}
            onChange={(e) => setArea(e.target.value)}
            placeholder="e.g. Serdang area, Block B"
            style={inputStyle}
          />

          {/* Details */}
          <div style={{ fontSize: 12, fontWeight: 700, color: C.muted, textTransform: "uppercase", letterSpacing: "1px", marginBottom: 6 }}>
            Additional details
          </div>
          <textarea
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            placeholder="Number of people, floor, special needs..."
            style={{
              ...inputStyle,
              height:     90,
              padding:    "12px 14px",
              resize:     "none",
              lineHeight: 1.5,
            }}
          />

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={!title.trim() || !area.trim()}
            style={{
              width:        "100%",
              height:       50,
              borderRadius: 14,
              background:   !title.trim() || !area.trim() ? "#e4eaf0" : C.navy,
              color:        !title.trim() || !area.trim() ? C.muted   : "#fff",
              border:       "none",
              fontWeight:   700,
              fontSize:     15,
              cursor:       !title.trim() || !area.trim() ? "not-allowed" : "pointer",
              marginBottom: 8,
            }}
          >
            Submit Request
          </button>

          <p style={{ textAlign: "center", fontSize: 11, color: C.muted, lineHeight: 1.5 }}>
            Requests are visible to community members nearby.
            Do not share personal information.
          </p>
        </div>
      </div>

      <style>{`@keyframes slideUp { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }`}</style>
    </div>
  );
}

// ── Main page ──────────────────────────────────────────────────────────────────
export default function RequestHelp() {
  const [requests,     setRequests]     = useState(INITIAL_REQUESTS);
  const [activeFilter, setActiveFilter] = useState("all");
  const [modalOpen,    setModalOpen]    = useState(false);
  const [reportedIds,  setReportedIds]  = useState(new Set());
  const [nextId,       setNextId]       = useState(INITIAL_REQUESTS.length + 1);

  const filtered =
    activeFilter === "all"
      ? requests
      : requests.filter((r) => r.category === activeFilter);

  function handleReport(id) {
    setReportedIds((prev) => new Set([...prev, id]));
  }

  function handleSubmit({ category, title, area, details }) {
    const newReq = {
      id:       nextId,
      category,
      title,
      status:   "Pending verification",
      area,
      approx:   false,
      time:     new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      details:  details || "No additional details provided.",
    };
    setRequests((prev) => [newReq, ...prev]);
    setNextId((n) => n + 1);
    setModalOpen(false);
  }

  return (
    <div style={{ padding: "0 20px 20px" }}>

      {/* Page heading */}
      <div style={{ paddingTop: 20, paddingBottom: 4 }}>
        <div style={{ fontSize: 22, fontWeight: 800, color: C.navy }}>Community Help</div>
        <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 4, fontSize: 13, color: C.muted }}>
          <MapPin size={13} />
          Serdang, Selangor
        </div>
        <div style={{ fontSize: 12, color: C.muted, marginTop: 2 }}>Nearby community requests</div>
      </div>

      {/* Category filter chips */}
      <div style={{ fontWeight: 700, fontSize: 13, color: C.navy, margin: "16px 0 8px" }}>
        Nearby requests
      </div>
      <div
        style={{
          display:        "flex",
          gap:            8,
          overflowX:      "auto",
          scrollbarWidth: "none",
          paddingBottom:  4,
          marginBottom:   12,
        }}
      >
        {CATEGORIES.map((cat) => (
          <CategoryChip
            key={cat.key}
            cat={cat}
            active={activeFilter === cat.key}
            onClick={() => setActiveFilter(cat.key)}
          />
        ))}
      </div>

      {/* Request cards */}
      {filtered.length === 0 ? (
        <div
          style={{
            textAlign:    "center",
            padding:      "40px 0",
            color:        C.muted,
            fontSize:     14,
          }}
        >
          No {activeFilter === "all" ? "" : activeFilter} requests yet.
        </div>
      ) : (
        filtered.map((req) => (
          <RequestCard
            key={req.id}
            req={req}
            onReport={handleReport}
          />
        ))
      )}

      {/* Info note */}
      <div
        style={{
          display:      "flex",
          alignItems:   "center",
          gap:          10,
          background:   C.greenBg,
          borderRadius: 12,
          padding:      "12px 14px",
          margin:       "4px 0 16px",
          fontSize:     13,
          color:        C.navy,
          border:       `1px solid ${C.green}30`,
        }}
      >
        <Info size={16} color={C.green} style={{ flexShrink: 0 }} />
        Verify requests before offering help.
      </div>

      {/* Offer Help button */}
      <button
        onClick={() => setModalOpen(true)}
        style={{
          width:          "100%",
          height:         50,
          borderRadius:   14,
          background:     C.navy,
          color:          "#fff",
          border:         "none",
          fontWeight:     700,
          fontSize:       16,
          cursor:         "pointer",
          display:        "flex",
          alignItems:     "center",
          justifyContent: "center",
          gap:            8,
          boxShadow:      "0 3px 12px rgba(21,45,75,0.2)",
          marginBottom:   8,
        }}
      >
        <Plus size={18} strokeWidth={2.5} />
        Offer Help
      </button>

      {/* Submit modal */}
      {modalOpen && (
        <SubmitModal
          onClose={() => setModalOpen(false)}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
}
