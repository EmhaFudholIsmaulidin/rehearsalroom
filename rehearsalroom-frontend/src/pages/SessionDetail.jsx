import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  sessionApi,
  progressApi,
  feedbackApi,
  songApi,
  errMsg,
} from "../api";
import {
  Spinner,
  StatusBadge,
  ProgressBar,
  Avatar,
  Modal,
  Toast,
  useToast,
  fmtDate,
  fmtTime,
} from "../components/ui";

export default function SessionDetail() {
  const { sessionId } = useParams();
  const { currentBand, isLeader, user } = useAuth();
  const [session, setSession] = useState(null);
  const [progress, setProgress] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [allSongs, setAllSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newFeedback, setNewFeedback] = useState("");
  const [addSong, setAddSong] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  async function load() {
    if (!currentBand) return;
    setLoading(true);
    try {
      const [s, p, f, songs] = await Promise.all([
        sessionApi.get(currentBand.id, sessionId),
        progressApi.list(sessionId),
        feedbackApi.list(sessionId),
        songApi.list(currentBand.id),
      ]);
      setSession(s);
      setProgress(p.items || []);
      setFeedback(f.items || []);
      setAllSongs(songs.items || []);
    } catch (e) {
      toast.show(errMsg(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line
  }, [sessionId, currentBand]);

  if (loading) return <Spinner />;
  if (!session) return <p className="muted">Session not found.</p>;

  // Merge session songs with their latest progress
  const progressBySong = {};
  progress.forEach((p) => (progressBySong[p.song_id] = p));

  async function submitFeedback() {
    if (!newFeedback.trim()) return;
    try {
      await feedbackApi.create(sessionId, newFeedback);
      setNewFeedback("");
      load();
      toast.show("Feedback submitted");
    } catch (e) {
      toast.show(errMsg(e));
    }
  }

  async function deleteFeedback(id) {
    try {
      await feedbackApi.remove(sessionId, id);
      load();
    } catch (e) {
      toast.show(errMsg(e));
    }
  }

  return (
    <>
      <button
        className="muted"
        style={{ marginBottom: 16, fontSize: 14 }}
        onClick={() => navigate("/schedule")}
      >
        ← Back to Schedule
      </button>

      <div className="page-head">
        <div>
          <div className="row" style={{ gap: 10 }}>
            <h1 className="page-title">{session.title}</h1>
            <StatusBadge status={session.status} />
          </div>
          <p className="page-sub">
            📅 {fmtDate(session.scheduled_at)} · ⏰ {fmtTime(session.scheduled_at)} (
            {session.duration_minutes}min) · 📍 {session.location || "TBD"}
          </p>
        </div>
        {isLeader && (
          <button className="btn btn-primary" onClick={() => setAddSong(true)}>
            + Add Song
          </button>
        )}
      </div>

      <div className="card" style={{ marginBottom: 18, padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Song Title</th>
              <th>Status</th>
              <th style={{ width: "30%" }}>Progress</th>
              <th>Notes</th>
              <th style={{ width: 90 }}></th>
            </tr>
          </thead>
          <tbody>
            {session.session_songs.length === 0 && (
              <tr>
                <td colSpan={5} className="muted" style={{ textAlign: "center", padding: 28 }}>
                  No songs in this session yet.
                </td>
              </tr>
            )}
            {session.session_songs.map((ss) => (
              <SongRow
                key={ss.id}
                ss={ss}
                progress={progressBySong[ss.song_id]}
                sessionId={sessionId}
                onSaved={() => {
                  load();
                  toast.show("Progress updated");
                }}
                onError={(m) => toast.show(m)}
              />
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <div className="row spread" style={{ marginBottom: 16 }}>
          <h3 style={{ fontSize: 17 }}>Session Feedback</h3>
          <span className="tag">
            {isLeader ? "✓ Viewing all feedback" : "Viewing your feedback"}
          </span>
        </div>

        <div style={{ marginBottom: 20 }}>
          <textarea
            className="textarea"
            rows={3}
            placeholder="Add your feedback or notes about this session…"
            value={newFeedback}
            onChange={(e) => setNewFeedback(e.target.value)}
          />
          <div className="row spread" style={{ marginTop: 10 }}>
            <span className="dim" style={{ fontSize: 12 }}>
              Visible to all Band Leaders and the submitting member.
            </span>
            <button className="btn btn-primary btn-sm" onClick={submitFeedback}>
              Submit Feedback
            </button>
          </div>
        </div>

        {feedback.map((f) => (
          <div
            key={f.id}
            style={{
              padding: 16,
              background: "var(--bg)",
              borderRadius: 8,
              marginBottom: 12,
            }}
          >
            <div className="row spread" style={{ marginBottom: 8 }}>
              <div className="row">
                <Avatar name={f.username} size={30} />
                <strong style={{ fontSize: 14 }}>{f.username}</strong>
                <span className="dim" style={{ fontSize: 12 }}>
                  {fmtDate(f.created_at)} {fmtTime(f.created_at)}
                </span>
              </div>
              {f.user_id === user?.id && (
                <button
                  style={{ color: "var(--red)", fontSize: 12 }}
                  onClick={() => deleteFeedback(f.id)}
                >
                  Delete
                </button>
              )}
            </div>
            <p className="muted" style={{ fontSize: 14, lineHeight: 1.5 }}>
              {f.content}
            </p>
          </div>
        ))}
      </div>

      {addSong && (
        <AddSongModal
          sessionId={sessionId}
          allSongs={allSongs}
          existing={session.session_songs.map((s) => s.song_id)}
          onClose={() => setAddSong(false)}
          onSaved={() => {
            setAddSong(false);
            load();
            toast.show("Song added to session");
          }}
        />
      )}
      <Toast message={toast.msg} />
    </>
  );
}

function SongRow({ ss, progress, sessionId, onSaved, onError }) {
  const song = ss.song || {};
  const [pct, setPct] = useState(progress?.progress_pct ?? 0);
  const [notes, setNotes] = useState(progress?.notes ?? "");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    try {
      await progressApi.upsert(sessionId, {
        song_id: ss.song_id,
        progress_pct: Number(pct),
        notes: notes || null,
      });
      onSaved();
    } catch (e) {
      onError(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <tr>
      <td>
        <strong>{song.title}</strong>
        <p className="muted" style={{ fontSize: 12 }}>
          {song.composer || ""}
        </p>
      </td>
      <td>
        <StatusBadge status={song.status} />
      </td>
      <td>
        <div className="row" style={{ gap: 10 }}>
          <input
            type="range"
            min="0"
            max="100"
            value={pct}
            onChange={(e) => setPct(e.target.value)}
            style={{ flex: 1, accentColor: "var(--accent)" }}
          />
          <span className="muted" style={{ fontSize: 13, width: 38 }}>
            {pct}%
          </span>
        </div>
      </td>
      <td>
        <input
          className="input"
          style={{ padding: "8px 10px", fontSize: 13 }}
          placeholder="Add a note…"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </td>
      <td>
        <button className="btn btn-primary btn-sm" onClick={save} disabled={busy}>
          Update
        </button>
      </td>
    </tr>
  );
}

function AddSongModal({ sessionId, allSongs, existing, onClose, onSaved }) {
  const available = allSongs.filter((s) => !existing.includes(s.id));
  const [selected, setSelected] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function add() {
    if (!selected) return;
    setBusy(true);
    setErr("");
    try {
      await sessionApi.addSong(sessionId, selected);
      onSaved();
    } catch (e) {
      setErr(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title="Add Song to Session" onClose={onClose}>
      {available.length === 0 ? (
        <p className="muted">All songs are already in this session.</p>
      ) : (
        <>
          <select
            className="select"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            style={{ marginBottom: 16 }}
          >
            <option value="">Select a song…</option>
            {available.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title} {s.composer ? `— ${s.composer}` : ""}
              </option>
            ))}
          </select>
          {err && <p className="input-error-text">{err}</p>}
          <button
            className="btn btn-primary btn-block"
            onClick={add}
            disabled={busy || !selected}
          >
            {busy ? "Adding…" : "Add Song"}
          </button>
        </>
      )}
    </Modal>
  );
}
