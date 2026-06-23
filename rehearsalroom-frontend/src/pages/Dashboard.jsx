import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { bandApi, errMsg } from "../api";
import {
  Spinner,
  StatusBadge,
  ProgressBar,
  Avatar,
  Empty,
  Modal,
  Field,
  fmtDate,
  fmtTime,
} from "../components/ui";

export default function Dashboard() {
  const { user, currentBand, reloadBands } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!currentBand) {
      setLoading(false);
      return;
    }
    setLoading(true);
    bandApi
      .dashboard(currentBand.id)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [currentBand]);

  if (!currentBand)
    return <NoBand onCreated={reloadBands} show={showCreate} setShow={setShowCreate} />;
  if (loading) return <Spinner />;

  const next = data?.upcoming_sessions?.[0];

  return (
    <>
      <div className="page-head">
        <div>
          <span className="badge badge-leader" style={{ marginBottom: 10, display: "inline-block" }}>
            {currentBand.name.toUpperCase()}
          </span>
          <h1 className="page-title">Welcome back, {user?.username}</h1>
          <p className="page-sub">Here's what's happening with your band today.</p>
        </div>
      </div>

      <div className="grid grid-3" style={{ marginBottom: 18 }}>
        <div className="card">
          <p className="muted" style={{ fontSize: 13, marginBottom: 14 }}>
            ⏰ Next Rehearsal
          </p>
          {next ? (
            <>
              <h2 style={{ fontSize: 24 }}>{fmtDate(next.scheduled_at)}</h2>
              <p className="muted" style={{ marginTop: 6, fontSize: 13 }}>
                {fmtTime(next.scheduled_at)} · {next.location || "TBD"}
              </p>
            </>
          ) : (
            <p className="muted">No upcoming sessions</p>
          )}
        </div>

        <div className="card">
          <p className="muted" style={{ fontSize: 13, marginBottom: 14 }}>
            ♪ Setlist Progress
          </p>
          <h2 style={{ fontSize: 28 }}>
            {data.ready_songs}
            <span className="muted" style={{ fontSize: 18 }}> / {data.total_songs}</span>
          </h2>
          <p className="muted" style={{ marginTop: 6, fontSize: 13 }}>
            Songs ready for gig
          </p>
        </div>

        <div className="card">
          <p className="muted" style={{ fontSize: 13, marginBottom: 14 }}>
            📈 Band Readiness
          </p>
          <h2 style={{ fontSize: 28, marginBottom: 12 }}>{data.ready_pct}%</h2>
          <ProgressBar value={data.ready_pct} color="var(--green)" />
        </div>
      </div>

      <div className="grid grid-2" style={{ marginBottom: 18 }}>
        <div className="card">
          <div className="row spread" style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: 17 }}>Upcoming Sessions</h3>
            <button className="accent" style={{ fontSize: 13 }} onClick={() => navigate("/schedule")}>
              View All
            </button>
          </div>
          {data.upcoming_sessions.length === 0 && (
            <p className="muted">No sessions scheduled.</p>
          )}
          {data.upcoming_sessions.map((s) => (
            <div
              key={s.id}
              className="row spread"
              style={{
                padding: "14px",
                background: "var(--bg)",
                borderRadius: 8,
                marginBottom: 10,
                cursor: "pointer",
              }}
              onClick={() => navigate(`/sessions/${s.id}`)}
            >
              <div>
                <strong style={{ fontSize: 14 }}>{s.title}</strong>
                <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                  {fmtDate(s.scheduled_at)} · {fmtTime(s.scheduled_at)} ·{" "}
                  {s.location || "TBD"}
                </p>
              </div>
              <StatusBadge status={s.status} />
            </div>
          ))}
        </div>

        <div className="card">
          <h3 style={{ fontSize: 17, marginBottom: 16 }}>Song Progress</h3>
          {data.song_progress_summary.length === 0 && (
            <p className="muted">No songs yet.</p>
          )}
          {data.song_progress_summary.slice(0, 5).map((s) => (
            <div key={s.song_id} style={{ marginBottom: 14 }}>
              <div className="row spread" style={{ marginBottom: 6 }}>
                <strong style={{ fontSize: 14 }}>{s.song_title}</strong>
                <span className="muted" style={{ fontSize: 12 }}>
                  {s.latest_progress_pct ?? 0}%
                </span>
              </div>
              <ProgressBar value={s.latest_progress_pct ?? 0} />
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: 17, marginBottom: 16 }}>Recent Feedback</h3>
        {data.latest_feedbacks.length === 0 && (
          <p className="muted">No feedback yet.</p>
        )}
        <div className="grid grid-2">
          {data.latest_feedbacks.map((f) => (
            <div
              key={f.id}
              style={{ padding: 14, background: "var(--bg)", borderRadius: 8 }}
            >
              <div className="row" style={{ marginBottom: 8 }}>
                <Avatar name={f.username} size={28} />
                <strong style={{ fontSize: 13 }}>{f.username}</strong>
                <span className="dim" style={{ fontSize: 12 }}>
                  · {fmtDate(f.created_at)}
                </span>
              </div>
              <p className="muted" style={{ fontSize: 13, lineHeight: 1.5 }}>
                {f.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

// Shown when the user belongs to no band yet
function NoBand({ onCreated, show, setShow }) {
  const [form, setForm] = useState({ name: "", genre: "", formed_year: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function create() {
    setBusy(true);
    setErr("");
    try {
      await bandApi.create({
        name: form.name,
        genre: form.genre || null,
        formed_year: form.formed_year ? Number(form.formed_year) : null,
      });
      await onCreated();
      setShow(false);
    } catch (e) {
      setErr(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Empty
        icon="🎸"
        title="No band yet"
        sub="Create your first band to start scheduling rehearsals and tracking songs."
        action={
          <button className="btn btn-primary" onClick={() => setShow(true)}>
            + Create a Band
          </button>
        }
      />
      {show && (
        <Modal title="Create a Band" onClose={() => setShow(false)}>
          <Field label="Band name">
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </Field>
          <Field label="Genre">
            <input
              className="input"
              value={form.genre}
              onChange={(e) => setForm({ ...form, genre: e.target.value })}
            />
          </Field>
          <Field label="Formed year">
            <input
              className="input"
              type="number"
              value={form.formed_year}
              onChange={(e) => setForm({ ...form, formed_year: e.target.value })}
            />
          </Field>
          {err && <p className="input-error-text">{err}</p>}
          <button
            className="btn btn-primary btn-block"
            style={{ marginTop: 8 }}
            onClick={create}
            disabled={busy || !form.name}
          >
            {busy ? "Creating…" : "Create Band"}
          </button>
        </Modal>
      )}
    </>
  );
}
