import { MapPin, Navigation } from "lucide-react";

const PLACES = [
  { icon: "🏫", name: "Sekolah Kebangsaan Serdang",  dist: "1.2 km", note: "Open · 200 capacity"   },
  { icon: "🏥", name: "Hospital Putrajaya",           dist: "3.4 km", note: "Open · Emergency only" },
  { icon: "🅿️", name: "SACC Mall Car Park Level 3+", dist: "0.8 km", note: "Dry · Elevated parking" },
  { icon: "🏛️", name: "Dewan Orang Ramai Serdang",   dist: "0.6 km", note: "Open · 150 capacity"   },
];

export default function SafePlaces() {
  return (
    <div style={{ padding: "20px 20px 20px" }}>
      <div style={{ fontSize: 22, fontWeight: 800, color: "#152d4b", marginBottom: 4 }}>Safe Places</div>
      <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 13, color: "#68788b", marginBottom: 20 }}>
        <MapPin size={13} />
        Nearby evacuation and safe locations
      </div>

      {PLACES.map(({ icon, name, dist, note }) => (
        <div
          key={name}
          style={{
            display:      "flex",
            alignItems:   "center",
            gap:          14,
            background:   "#fff",
            borderRadius: 14,
            padding:      "14px 16px",
            marginBottom: 10,
            border:       "1px solid #e4eaf0",
            boxShadow:    "0 1px 4px rgba(21,45,75,.05)",
          }}
        >
          <span style={{ fontSize: 24, flexShrink: 0 }}>{icon}</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 14, color: "#152d4b" }}>{name}</div>
            <div style={{ fontSize: 12, color: "#68788b", marginTop: 2 }}>{dist} · {note}</div>
          </div>
          <Navigation size={18} color="#68788b" />
        </div>
      ))}
    </div>
  );
}
