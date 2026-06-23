import { useState } from "react";

export function Spinner() {
  return <div className="spinner" />;
}

export function StatusBadge({ status }) {
  const labels = {
    learning: "Learning",
    ready: "Ready",
    on_hold: "On Hold",
    upcoming: "Upcoming",
    ongoing: "Ongoing",
    completed: "Completed",
    cancelled: "Cancelled",
  };
  return (
    <span className={`badge badge-${status}`}>
      {labels[status] || status}
    </span>
  );
}

export function RoleBadge({ role }) {
  return (
    <span className={`badge badge-${role === "band_leader" ? "leader" : "member"}`}>
      {role === "band_leader" ? "Leader" : "Member"}
    </span>
  );
}

export function Avatar({ name, size = 38 }) {
  const initials = (name || "?")
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
  return (
    <span
      className="avatar"
      style={{ width: size, height: size, fontSize: size * 0.38 }}
    >
      {initials}
    </span>
  );
}

export function ProgressBar({ value, color }) {
  const c =
    color ||
    (value >= 90 ? "var(--green)" : value >= 50 ? "var(--accent)" : "var(--blue)");
  return (
    <div className="progress-track">
      <div
        className="progress-fill"
        style={{ width: `${value}%`, background: c }}
      />
    </div>
  );
}

export function Field({ label, error, children }) {
  return (
    <div className="field">
      {label && <label>{label}</label>}
      {children}
      {error && <span className="input-error-text">{error}</span>}
    </div>
  );
}

export function Modal({ title, onClose, children }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="row spread" style={{ marginBottom: 18 }}>
          <h3 style={{ fontSize: 18 }}>{title}</h3>
          <button className="muted" onClick={onClose} style={{ fontSize: 20 }}>
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Toast({ message }) {
  if (!message) return null;
  return <div className="toast">{message}</div>;
}

export function useToast() {
  const [msg, setMsg] = useState("");
  const show = (m) => {
    setMsg(m);
    setTimeout(() => setMsg(""), 2800);
  };
  return { msg, show };
}

export function Empty({ icon = "🎵", title, sub, action }) {
  return (
    <div className="empty">
      <div style={{ fontSize: 40, marginBottom: 12 }}>{icon}</div>
      <h3 style={{ marginBottom: 6 }}>{title}</h3>
      {sub && <p className="muted" style={{ marginBottom: 18 }}>{sub}</p>}
      {action}
    </div>
  );
}

export const fmtDate = (d) =>
  d
    ? new Date(d).toLocaleDateString("id-ID", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : "—";

export const fmtTime = (d) =>
  d
    ? new Date(d).toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";

export const fmtDuration = (sec) => {
  if (!sec) return "—";
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
};
