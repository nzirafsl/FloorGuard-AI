import { Phone, X, AlertCircle, Shield } from "lucide-react";

/**
 * SosModal
 *
 * Props:
 *   isOpen   {boolean}  — controls visibility
 *   onClose  {function} — called when the user cancels
 *   location {string}   — current location label shown in the modal
 *   onConfirm {function} — called when the user confirms the SOS call
 */
export default function SosModal({ isOpen, onClose, location = "Serdang, Selangor", onConfirm }) {
  if (!isOpen) return null;

  function handleConfirm() {
    if (onConfirm) onConfirm();
    onClose();
  }

  return (
    /* Backdrop */
    <div
      onClick={onClose}
      style={{
        position:       "fixed",
        inset:          0,
        background:     "rgba(127, 29, 29, 0.60)",
        display:        "flex",
        alignItems:     "flex-end",
        justifyContent: "center",
        zIndex:         1000,
        backdropFilter: "blur(3px)",
      }}
    >
      {/* Sheet */}
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width:        "100%",
          maxWidth:     390,
          background:   "#fff",
          borderRadius: "24px 24px 0 0",
          padding:      "0 0 36px",
          boxShadow:    "0 -8px 40px rgba(127,29,29,0.3)",
          animation:    "sosSlideUp 0.22s ease-out",
        }}
      >
        {/* Drag handle */}
        <div style={{ display: "flex", justifyContent: "center", padding: "12px 0 4px" }}>
          <div style={{ width: 40, height: 4, borderRadius: 99, background: "#fca5a5" }} />
        </div>

        {/* Close button */}
        <div style={{ display: "flex", justifyContent: "flex-end", padding: "4px 16px 0" }}>
          <button
            onClick={onClose}
            aria-label="Cancel"
            style={{ background: "#fee2e2", border: "none", borderRadius: 99, padding: 6, cursor: "pointer", display: "flex" }}
          >
            <X size={18} color="#c62828" />
          </button>
        </div>

        {/* Icon */}
        <div style={{ display: "flex", justifyContent: "center", padding: "8px 0 0" }}>
          <div style={{
            width:        72,
            height:       72,
            borderRadius: "50%",
            background:   "linear-gradient(135deg, #7f1d1d, #c62828)",
            display:      "flex",
            alignItems:   "center",
            justifyContent: "center",
            boxShadow:    "0 4px 20px rgba(198,40,40,0.35)",
          }}>
            <Phone size={32} color="#fff" strokeWidth={2.5} />
          </div>
        </div>

        {/* Title */}
        <div style={{ textAlign: "center", padding: "14px 20px 0" }}>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 900, color: "#152d4b" }}>
            SOS Emergency
          </h2>
          <p style={{ margin: "6px 0 0", fontSize: 14, color: "#68788b", lineHeight: 1.5 }}>
            This will call <strong style={{ color: "#c62828" }}>999</strong> (Malaysian emergency services).
            Only use in a real emergency.
          </p>
        </div>

        {/* Location row */}
        <div style={{
          display:      "flex",
          alignItems:   "center",
          gap:          8,
          margin:       "14px 20px 0",
          background:   "#f4f7fa",
          borderRadius: 12,
          padding:      "10px 14px",
        }}>
          <Shield size={16} color="#68788b" />
          <div>
            <div style={{ fontSize: 11, color: "#68788b", fontWeight: 600, textTransform: "uppercase", letterSpacing: ".6px" }}>
              Your location
            </div>
            <div style={{ fontSize: 14, fontWeight: 700, color: "#152d4b", marginTop: 1 }}>{location}</div>
          </div>
        </div>

        {/* Warning note */}
        <div style={{
          display:      "flex",
          alignItems:   "flex-start",
          gap:          10,
          margin:       "12px 20px 0",
          background:   "#fdeaea",
          borderRadius: 12,
          padding:      "10px 14px",
        }}>
          <AlertCircle size={16} color="#c62828" style={{ flexShrink: 0, marginTop: 1 }} />
          <p style={{ margin: 0, fontSize: 12, color: "#991b1b", lineHeight: 1.5 }}>
            False calls to emergency services are a criminal offence.
            Follow official JPS/NADMA flood alerts for general guidance.
          </p>
        </div>

        {/* Action buttons */}
        <div style={{ padding: "20px 20px 0", display: "flex", flexDirection: "column", gap: 10 }}>
          {/* Confirm — red */}
          <button
            onClick={handleConfirm}
            style={{
              width:          "100%",
              height:         54,
              borderRadius:   14,
              background:     "#c62828",
              color:          "#fff",
              border:         "none",
              fontWeight:     800,
              fontSize:       17,
              cursor:         "pointer",
              display:        "flex",
              alignItems:     "center",
              justifyContent: "center",
              gap:            10,
              boxShadow:      "0 4px 16px rgba(198,40,40,0.35)",
              letterSpacing:  ".2px",
            }}
          >
            <Phone size={20} strokeWidth={2.5} />
            Call 999 Now
          </button>

          {/* Cancel — ghost */}
          <button
            onClick={onClose}
            style={{
              width:        "100%",
              height:       44,
              borderRadius: 14,
              background:   "transparent",
              color:        "#68788b",
              border:       "1.5px solid #e4eaf0",
              fontWeight:   600,
              fontSize:     14,
              cursor:       "pointer",
            }}
          >
            Cancel
          </button>
        </div>

        {/* Disclaimer */}
        <p style={{ textAlign: "center", fontSize: 11, color: "#9ca3af", margin: "10px 20px 0", lineHeight: 1.5 }}>
          Nothing is sent automatically. Your call connects you directly to emergency services.
        </p>
      </div>

      <style>{`
        @keyframes sosSlideUp {
          from { transform: translateY(100%); opacity: 0; }
          to   { transform: translateY(0);    opacity: 1; }
        }
      `}</style>
    </div>
  );
}
