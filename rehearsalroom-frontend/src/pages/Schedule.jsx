import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { sessionApi, errMsg } from "../api";
import {
  Spinner,
  StatusBadge,
  Modal,
  Field,
  Empty,
  Toast,
  useToast,
  fmtDate,
  fmtTime,
} from "../components/ui";

const DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];

export default function Schedule() {
  const { currentBand, isLeader } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cursor, setCursor] = useState(new Date());
  const [showNew, setShowNew] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  async function load() {
    if (!currentBand) return;
    setLoading(true);
    try {
      const res = await sessionApi.list(currentBand.id);
      setSessions(res.items || []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line
  }, [currentBand]);

  if (!currentBand)
    return <Empty title="No band selected" sub="Create or join a band first." />;
  if (loading) return <Spinner />;

  const year = cursor.getFullYear();
  const month = cursor.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const today = new Date();

  const cells = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  const sessionsOn = (day) =>
    sessions.filter((s) => {
      const dt = new Date(s.scheduled_at);
      return (
        dt.getDate() === day &&
        dt.getMonth() === month &&
        dt.getFullYear() === year
      );
    });

  const upcoming = [...sessions]
    .filter((s) => s.status === "upcoming")
    .sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at));

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">Rehearsal Schedule</h1>
          <p className="page-sub">Plan sessions and keep the band on time.</p>
        </div>
        <div className="row">
          <div className="row" style={{ gap: 6 }}>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setCursor(new Date(year, month - 1, 1))}
            >
              ‹
            </button>
            <span style={{ minWidth: 120, textAlign: "center" }}>
              {cursor.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
            </span>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setCursor(new Date(year, month + 1, 1))}
            >
              ›
            </button>
          </div>
          {isLeader && (
            <button className="btn btn-primary" onClick={() => setShowNew(true)}>
              + New Session
            </button>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 18 }}>
        <div className="calendar">
          {DAYS.map((d) => (
            <div key={d} className="cal-head">
              {d}
            </div>
          ))}
          {cells.map((day, i) => {
            const isToday =
              day === today.getDate() &&
              month === today.getMonth() &&
              year === today.getFullYear();
            const evts = day ? sessionsOn(day) : [];
            return (
              <div key={i} className={`cal-cell ${isToday ? "cal-today" : ""}`}>
                {day && <span className="day-num">{day}</span>}
                {evts.map((e) => (
                  <div
                    key={e.id}
                    className="cal-event"
                    onClick={() => navigate(`/sessions/${e.id}`)}
                    style={{ cursor: "pointer" }}
                  >
                    ● {e.title}
                  </div>
                ))}
              </div>
            );
          })}
        </div>

        <div>
          <h3 style={{ fontSize: 16, marginBottom: 14 }}>Upcoming Sessions</h3>
          {upcoming.length === 0 && <p className="muted">No upcoming sessions.</p>}
          {upcoming.map((s) => (
            <div className="card" key={s.id} style={{ marginBottom: 12, padding: 16 }}>
              <div className="row spread" style={{ marginBottom: 8 }}>
                <strong>{s.title}</strong>
                <StatusBadge status={s.status} />
              </div>
              <p className="muted" style={{ fontSize: 13 }}>
                ⏰ {fmtDate(s.scheduled_at)} · {fmtTime(s.scheduled_at)} ·{" "}
                {s.duration_minutes}min
              </p>
              <p className="muted" style={{ fontSize: 13, marginTop: 4 }}>
                📍 {s.location || "TBD"}
              </p>
              <button
                className="btn btn-ghost btn-sm btn-block"
                style={{ marginTop: 12 }}
                onClick={() => navigate(`/sessions/${s.id}`)}
              >
                View Detail
              </button>
            </div>
          ))}
        </div>
      </div>

      {showNew && (
        <SessionModal
          bandId={currentBand.id}
          onClose={() => setShowNew(false)}
          onSaved={() => {
            setShowNew(false);
            load();
            toast.show("Session created");
          }}
        />
      )}
      <Toast message={toast.msg} />
    </>
  );
}

function SessionModal({ bandId, onClose, onSaved }) {
  const [form, setForm] = useState({
    title: "",
    date: "",
    time: "18:00",
    duration_minutes: 120,
    location: "",
  });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function save() {
    setBusy(true);
    setErr("");
    try {
      const scheduled_at = new Date(`${form.date}T${form.time}`).toISOString();
      await sessionApi.create(bandId, {
        title: form.title,
        scheduled_at,
        duration_minutes: Number(form.duration_minutes),
        location: form.location || null,
      });
      onSaved();
    } catch (e) {
      setErr(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title="New Session" onClose={onClose}>
      <Field label="Session name">
        <input className="input" value={form.title} onChange={set("title")} />
      </Field>
      <div className="row">
        <Field label="Date">
          <input className="input" type="date" value={form.date} onChange={set("date")} />
        </Field>
        <Field label="Time">
          <input className="input" type="time" value={form.time} onChange={set("time")} />
        </Field>
      </div>
      <div className="row">
        <Field label="Duration (min)">
          <input
            className="input"
            type="number"
            value={form.duration_minutes}
            onChange={set("duration_minutes")}
          />
        </Field>
        <Field label="Location">
          <input className="input" value={form.location} onChange={set("location")} />
        </Field>
      </div>
      {err && <p className="input-error-text">{err}</p>}
      <button
        className="btn btn-primary btn-block"
        style={{ marginTop: 8 }}
        onClick={save}
        disabled={busy || !form.title || !form.date}
      >
        {busy ? "Creating…" : "Create Session"}
      </button>
    </Modal>
  );
}
