import { useEffect, useRef } from "react";
import { MapPin, Navigation } from "lucide-react";
import "leaflet/dist/leaflet.css";

// ── Safe-place data with coordinates ─────────────────────────────────────────
const PLACES = [
  {
    icon: "🏫",
    name: "Sekolah Kebangsaan Serdang",
    dist: "1.2 km",
    note: "Open · 200 capacity",
    lat:  2.9982,
    lon:  101.7036,
    color: "#1565c0",
  },
  {
    icon: "🏥",
    name: "Hospital Putrajaya",
    dist: "3.4 km",
    note: "Open · Emergency only",
    lat:  2.9264,
    lon:  101.6964,
    color: "#c62828",
  },
  {
    icon: "🅿️",
    name: "SACC Mall Car Park Level 3+",
    dist: "0.8 km",
    note: "Dry · Elevated parking",
    lat:  3.0726,
    lon:  101.5220,
    color: "#2e7d32",
  },
  {
    icon: "🏛️",
    name: "Dewan Orang Ramai Serdang",
    dist: "0.6 km",
    note: "Open · 150 capacity",
    lat:  3.0140,
    lon:  101.7010,
    color: "#6a1b9a",
  },
];

// User / flood origin point
const USER_LOCATION = { lat: 3.0738, lon: 101.5183 };

// ── Custom marker helper (pure Leaflet DivIcon) ───────────────────────────────
function makeIcon(L, emoji, color) {
  return L.divIcon({
    className: "",
    html: `
      <div style="
        width:38px;height:38px;border-radius:50% 50% 50% 0;
        background:${color};transform:rotate(-45deg);
        border:3px solid #fff;
        box-shadow:0 2px 6px rgba(0,0,0,.35);
        display:flex;align-items:center;justify-content:center;
      ">
        <span style="transform:rotate(45deg);font-size:16px;line-height:1">${emoji}</span>
      </div>`,
    iconSize:   [38, 38],
    iconAnchor: [19, 38],
    popupAnchor:[0, -40],
  });
}

function makeUserIcon(L) {
  return L.divIcon({
    className: "",
    html: `
      <div style="
        width:18px;height:18px;border-radius:50%;
        background:#1565c0;border:3px solid #fff;
        box-shadow:0 0 0 4px rgba(21,101,192,.25);
      "></div>`,
    iconSize:   [18, 18],
    iconAnchor: [9, 9],
  });
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function SafePlaces() {
  const mapRef     = useRef(null);   // DOM node
  const leafletRef = useRef(null);   // L.map instance

  useEffect(() => {
    const container = mapRef.current;
    if (!container) return;

    // Tear down any previous instance (React StrictMode double-invoke)
    if (leafletRef.current) {
      leafletRef.current.remove();
      leafletRef.current = null;
    }

    // Dynamic import so SSR / Vite tree-shaking stay clean
    import("leaflet").then((mod) => {
      const L = mod.default ?? mod;

      // Guard: component may have unmounted while the import resolved
      if (!mapRef.current) return;

      const map = L.map(mapRef.current, {
        center:             [USER_LOCATION.lat, USER_LOCATION.lon],
        zoom:               13,
        zoomControl:        true,
        attributionControl: true,
      });

      leafletRef.current = map;

      // Force Leaflet to recalculate container size after mount
      setTimeout(() => map.invalidateSize(), 0);

      // Tile layer
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
      }).addTo(map);

      // User location marker
      L.marker([USER_LOCATION.lat, USER_LOCATION.lon], { icon: makeUserIcon(L) })
        .addTo(map)
        .bindPopup("<b>📍 Your Location</b><br/>Serdang, Selangor")
        .openPopup();

      // Safe-place markers
      PLACES.forEach(({ icon, name, dist, note, lat, lon, color }) => {
        L.marker([lat, lon], { icon: makeIcon(L, icon, color) })
          .addTo(map)
          .bindPopup(`<b>${icon} ${name}</b><br/>${dist} · ${note}`);
      });

      // Flood risk zone circle around user
      L.circle([USER_LOCATION.lat, USER_LOCATION.lon], {
        radius:      1200,
        color:       "#c62828",
        fillColor:   "#c62828",
        fillOpacity: 0.08,
        weight:      2,
        dashArray:   "6 4",
      }).addTo(map).bindPopup("⚠️ High flood-risk zone radius");
    });

    return () => {
      if (leafletRef.current) {
        leafletRef.current.remove();
        leafletRef.current = null;
      }
    };
  }, []);

  return (
    <div style={container}>

      {/* ── Page heading ── */}
      <div style={heading}>
        <div style={{ fontSize: 22, fontWeight: 800, color: "#152d4b" }}>Safe Places</div>
        <div style={subHead}>
          <MapPin size={13} />
          Nearby evacuation &amp; safe locations
        </div>
      </div>

      {/* ── Map ── */}
      <div style={mapWrap}>
        <div ref={mapRef} style={mapBox} />
        <div style={mapLegend}>
          <span style={legendDot("#c62828")} /> Flood zone &nbsp;
          <span style={legendDot("#1565c0")} /> You &nbsp;
          <span style={legendDot("#2e7d32")} /> Safe place
        </div>
      </div>

      {/* ── Safe places list ── */}
      <div style={listSection}>
        {PLACES.map(({ icon, name, dist, note, color }) => (
          <div key={name} style={card}>
            <div style={{ ...iconBox, background: color + "18", fontSize: 22 }}>{icon}</div>
            <div style={{ flex: 1 }}>
              <div style={cardName}>{name}</div>
              <div style={cardMeta}>{dist} · {note}</div>
            </div>
            <Navigation size={18} color="#68788b" />
          </div>
        ))}
      </div>

    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const legendDot = (color) => ({
  display:      "inline-block",
  width:        9,
  height:       9,
  borderRadius: "50%",
  background:   color,
  marginRight:  3,
  verticalAlign: "middle",
});

const container = {
  padding:       "20px 16px 8px",
  display:       "flex",
  flexDirection: "column",
  gap:           14,
};

const heading = {
  display:       "flex",
  flexDirection: "column",
  gap:           4,
};

const subHead = {
  display:    "flex",
  alignItems: "center",
  gap:        5,
  fontSize:   13,
  color:      "#68788b",
};

const mapWrap = {
  borderRadius: 16,
  boxShadow:    "0 2px 12px rgba(21,45,75,.12)",
  border:       "1px solid #e4eaf0",
  background:   "#e8eef4",
};

const mapBox = {
  width:        "100%",
  height:       "280px",
  display:      "block",
  borderRadius: "16px 16px 0 0",
};

const mapLegend = {
  background: "#fff",
  padding:    "7px 14px",
  fontSize:   11,
  color:      "#68788b",
  display:    "flex",
  alignItems: "center",
};

const listSection = {
  display:       "flex",
  flexDirection: "column",
  gap:           10,
};

const card = {
  display:      "flex",
  alignItems:   "center",
  gap:          14,
  background:   "#fff",
  borderRadius: 14,
  padding:      "14px 16px",
  border:       "1px solid #e4eaf0",
  boxShadow:    "0 1px 4px rgba(21,45,75,.05)",
};

const iconBox = {
  width:          44,
  height:         44,
  borderRadius:   12,
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  flexShrink:     0,
};

const cardName = {
  fontWeight: 700,
  fontSize:   14,
  color:      "#152d4b",
};

const cardMeta = {
  fontSize:  12,
  color:     "#68788b",
  marginTop: 2,
};
