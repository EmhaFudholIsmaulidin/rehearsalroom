import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Avatar } from "./ui";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: "▦" },
  { to: "/songs", label: "Songs", icon: "♪" },
  { to: "/schedule", label: "Schedule", icon: "▤" },
  { to: "/members", label: "Members", icon: "◍" },
];

export default function Layout({ children }) {
  const { user, currentBand, bands, selectBand, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-mark">🔊</span>
          <span>RehearsalRoom</span>
        </div>

        {bands.length > 1 && (
          <select
            className="select"
            style={{ marginBottom: 18 }}
            value={currentBand?.id || ""}
            onChange={(e) =>
              selectBand(bands.find((b) => b.id === e.target.value))
            }
          >
            {bands.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        )}

        <nav style={{ flex: 1 }}>
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <span style={{ width: 18, textAlign: "center" }}>{n.icon}</span>
              <span className="nav-label">{n.label}</span>
            </NavLink>
          ))}
          <button
            className="nav-item"
            style={{ width: "100%" }}
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            <span style={{ width: 18, textAlign: "center" }}>⏻</span>
            <span className="nav-label">Logout</span>
          </button>
        </nav>

        <div className="sidebar-user">
          <Avatar name={user?.username} size={36} />
          <div className="stack">
            <strong style={{ fontSize: 13 }}>{user?.username}</strong>
            <span className="dim" style={{ fontSize: 12 }}>
              {currentBand?._myRole === "band_leader" ? "Band Leader" : "Member"}
            </span>
          </div>
        </div>
      </aside>

      <main className="main">{children}</main>
    </div>
  );
}
