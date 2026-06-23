import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { songApi, errMsg } from "../api";
import {
  Spinner,
  StatusBadge,
  Modal,
  Field,
  Empty,
  Toast,
  useToast,
  fmtDate,
  fmtDuration,
} from "../components/ui";

const STATUSES = ["learning", "ready", "on_hold"];

export default function Songs() {
  const { currentBand, isLeader } = useAuth();
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [modal, setModal] = useState(null); // null | "new" | song object
  const toast = useToast();

  async function load() {
    if (!currentBand) return;
    setLoading(true);
    try {
      const res = await songApi.list(currentBand.id);
      setSongs(res.items || []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line
  }, [currentBand]);

  async function remove(song) {
    if (!confirm(`Delete "${song.title}"?`)) return;
    try {
      await songApi.remove(currentBand.id, song.id);
      toast.show("Song deleted");
      load();
    } catch (e) {
      toast.show(errMsg(e));
    }
  }

  async function cycleStatus(song) {
    if (!isLeader) return;
    const next = STATUSES[(STATUSES.indexOf(song.status) + 1) % STATUSES.length];
    try {
      await songApi.setStatus(currentBand.id, song.id, next);
      load();
    } catch (e) {
      toast.show(errMsg(e));
    }
  }

  if (!currentBand)
    return <Empty title="No band selected" sub="Create or join a band first." />;
  if (loading) return <Spinner />;

  const filtered = songs.filter((s) => {
    const matchSearch =
      s.title.toLowerCase().includes(search.toLowerCase()) ||
      (s.composer || "").toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === "all" || s.status === filter;
    return matchSearch && matchFilter;
  });

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">Song Library</h1>
          <p className="page-sub">Manage and track your band's setlist progress.</p>
        </div>
        {isLeader && (
          <button className="btn btn-primary" onClick={() => setModal("new")}>
            + Add Song
          </button>
        )}
      </div>

      <div className="row" style={{ marginBottom: 18 }}>
        <input
          className="input"
          placeholder="🔍 Search songs, artists…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ maxWidth: 360 }}
        />
        <select
          className="select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ maxWidth: 180 }}
        >
          <option value="all">All Songs</option>
          <option value="learning">Learning</option>
          <option value="ready">Ready</option>
          <option value="on_hold">On Hold</option>
        </select>
        <span className="tag" style={{ marginLeft: "auto" }}>
          {songs.length} songs
        </span>
      </div>

      {filtered.length === 0 ? (
        <div className="card">
          <Empty
            icon="💿"
            title="No songs yet"
            sub="Add your first song to start building your setlist."
            action={
              isLeader && (
                <button className="btn btn-primary" onClick={() => setModal("new")}>
                  + Add Your First Song
                </button>
              )
            }
          />
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: 50 }}>No.</th>
                <th>Song Title</th>
                <th>Artist / Composer</th>
                <th>Duration</th>
                <th>Status</th>
                <th>Added</th>
                {isLeader && <th style={{ width: 100 }}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map((s, i) => (
                <tr key={s.id}>
                  <td className="dim">{String(i + 1).padStart(2, "0")}</td>
                  <td>
                    <strong>{s.title}</strong>
                  </td>
                  <td className="muted">{s.composer || "—"}</td>
                  <td className="muted">⏱ {fmtDuration(s.duration_seconds)}</td>
                  <td>
                    <button
                      onClick={() => cycleStatus(s)}
                      title={isLeader ? "Click to change status" : ""}
                    >
                      <StatusBadge status={s.status} />
                    </button>
                  </td>
                  <td className="muted">{fmtDate(s.created_at)}</td>
                  {isLeader && (
                    <td>
                      <div className="row" style={{ gap: 8 }}>
                        <button className="accent" onClick={() => setModal(s)}>
                          ✎
                        </button>
                        <button
                          style={{ color: "var(--red)" }}
                          onClick={() => remove(s)}
                        >
                          🗑
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <SongModal
          song={modal === "new" ? null : modal}
          bandId={currentBand.id}
          onClose={() => setModal(null)}
          onSaved={() => {
            setModal(null);
            load();
            toast.show("Saved");
          }}
        />
      )}
      <Toast message={toast.msg} />
    </>
  );
}

function SongModal({ song, bandId, onClose, onSaved }) {
  const [form, setForm] = useState({
    title: song?.title || "",
    composer: song?.composer || "",
    minutes: song ? Math.floor((song.duration_seconds || 0) / 60) : "",
    seconds: song ? (song.duration_seconds || 0) % 60 : "",
    status: song?.status || "learning",
  });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function save() {
    setBusy(true);
    setErr("");
    const duration_seconds =
      Number(form.minutes || 0) * 60 + Number(form.seconds || 0);
    const body = {
      title: form.title,
      composer: form.composer || null,
      duration_seconds: duration_seconds || null,
    };
    try {
      if (song) {
        await songApi.update(bandId, song.id, body);
      } else {
        await songApi.create(bandId, { ...body, status: form.status });
      }
      onSaved();
    } catch (e) {
      setErr(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title={song ? "Edit Song" : "Add Song"} onClose={onClose}>
      <Field label="Song title">
        <input className="input" value={form.title} onChange={set("title")} />
      </Field>
      <Field label="Artist / Composer">
        <input className="input" value={form.composer} onChange={set("composer")} />
      </Field>
      <div className="row">
        <Field label="Minutes">
          <input
            className="input"
            type="number"
            value={form.minutes}
            onChange={set("minutes")}
          />
        </Field>
        <Field label="Seconds">
          <input
            className="input"
            type="number"
            value={form.seconds}
            onChange={set("seconds")}
          />
        </Field>
      </div>
      {!song && (
        <Field label="Status">
          <select className="select" value={form.status} onChange={set("status")}>
            <option value="learning">Learning</option>
            <option value="ready">Ready</option>
            <option value="on_hold">On Hold</option>
          </select>
        </Field>
      )}
      {err && <p className="input-error-text">{err}</p>}
      <button
        className="btn btn-primary btn-block"
        style={{ marginTop: 8 }}
        onClick={save}
        disabled={busy || !form.title}
      >
        {busy ? "Saving…" : "Save Song"}
      </button>
    </Modal>
  );
}
