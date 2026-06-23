import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { memberApi, inviteApi, errMsg } from "../api";
import {
  Spinner,
  RoleBadge,
  Avatar,
  Modal,
  Field,
  Toast,
  useToast,
  Empty,
  fmtDate,
} from "../components/ui";

const INSTRUMENTS = ["Guitar", "Bass", "Drums", "Vocals", "Keys", "Violin", "Other"];

export default function Members() {
  const { currentBand, isLeader, user } = useAuth();
  const [members, setMembers] = useState([]);
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [editMember, setEditMember] = useState(null);
  const toast = useToast();

  async function load() {
    if (!currentBand) return;
    setLoading(true);
    try {
      const m = await memberApi.list(currentBand.id);
      setMembers(m.items || []);
      if (isLeader) {
        const inv = await inviteApi.list(currentBand.id);
        setInvites(inv.items || []);
      }
    } catch (e) {
      toast.show(errMsg(e));
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

  async function removeMember(m) {
    if (!confirm(`Remove ${m.username} from the band?`)) return;
    try {
      await memberApi.remove(currentBand.id, m.user_id);
      load();
      toast.show("Member removed");
    } catch (e) {
      toast.show(errMsg(e));
    }
  }

  async function cancelInvite(id) {
    try {
      await inviteApi.cancel(currentBand.id, id);
      load();
      toast.show("Invitation cancelled");
    } catch (e) {
      toast.show(errMsg(e));
    }
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">Band Members</h1>
          <p className="page-sub">Manage your roster, roles, and invitations.</p>
        </div>
        {isLeader && (
          <button className="btn btn-primary" onClick={() => setShowInvite(true)}>
            + Invite Member
          </button>
        )}
      </div>

      {/* Band info card */}
      <div className="card" style={{ marginBottom: 22 }}>
        <div className="row spread">
          <div className="row">
            <span className="logo-mark" style={{ width: 48, height: 48, fontSize: 24 }}>
              ♪
            </span>
            <div>
              <h2 style={{ fontSize: 20 }}>{currentBand.name}</h2>
              <div className="row" style={{ gap: 6, marginTop: 6 }}>
                {currentBand.genre && <span className="tag">{currentBand.genre}</span>}
                {currentBand.formed_year && (
                  <span className="tag">Formed {currentBand.formed_year}</span>
                )}
              </div>
            </div>
          </div>
          <div className="row" style={{ gap: 32 }}>
            <Stat label="Members" value={members.length} />
            {currentBand.formed_year && (
              <Stat label="Formed" value={currentBand.formed_year} />
            )}
          </div>
        </div>
      </div>

      <h3 style={{ fontSize: 16, marginBottom: 14 }}>
        Active Members <span className="dim">({members.length})</span>
      </h3>
      <div className="grid grid-3" style={{ marginBottom: 28 }}>
        {members.map((m) => (
          <div className="card" key={m.id}>
            <div className="row spread" style={{ marginBottom: 12 }}>
              <div className="row">
                <Avatar name={m.username} size={44} />
                <div>
                  <strong>{m.username}</strong>
                  {m.instrument && (
                    <p className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                      🎸 {m.instrument}
                    </p>
                  )}
                </div>
              </div>
              <RoleBadge role={m.role} />
            </div>
            <p className="muted" style={{ fontSize: 13 }}>
              ✉ {m.email}
            </p>
            <p className="muted" style={{ fontSize: 13, marginTop: 4 }}>
              📅 Joined {fmtDate(m.joined_at)}
            </p>

            {isLeader && m.user_id !== user?.id && (
              <div className="row" style={{ marginTop: 14, gap: 8 }}>
                <button
                  className="btn btn-ghost btn-sm"
                  style={{ flex: 1 }}
                  onClick={() => setEditMember(m)}
                >
                  ✎ Edit Role
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  style={{ flex: 1 }}
                  onClick={() => removeMember(m)}
                >
                  Remove
                </button>
              </div>
            )}
            {m.user_id === user?.id && (
              <p className="dim" style={{ fontSize: 12, marginTop: 14, textAlign: "center" }}>
                {m.role === "band_leader" ? "Band owner · cannot be removed" : "This is you"}
              </p>
            )}
          </div>
        ))}
      </div>

      {isLeader && (
        <>
          <h3 style={{ fontSize: 16, marginBottom: 14 }}>
            Pending Invitations <span className="dim">({invites.length})</span>
          </h3>
          {invites.length === 0 ? (
            <p className="muted">No pending invitations.</p>
          ) : (
            <div className="card" style={{ padding: 0, overflow: "hidden" }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Email Address</th>
                    <th>Sent Date</th>
                    <th>Expires</th>
                    <th style={{ width: 120 }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {invites.map((inv) => (
                    <tr key={inv.id}>
                      <td>✉ {inv.invited_email}</td>
                      <td className="muted">{fmtDate(inv.created_at)}</td>
                      <td className="muted">{fmtDate(inv.expires_at)}</td>
                      <td>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => cancelInvite(inv.id)}
                        >
                          Cancel
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {showInvite && (
        <InviteModal
          bandId={currentBand.id}
          onClose={() => setShowInvite(false)}
          onSaved={() => {
            setShowInvite(false);
            load();
            toast.show("Invitation sent");
          }}
        />
      )}
      {editMember && (
        <EditMemberModal
          bandId={currentBand.id}
          member={editMember}
          onClose={() => setEditMember(null)}
          onSaved={() => {
            setEditMember(null);
            load();
            toast.show("Member updated");
          }}
        />
      )}
      <Toast message={toast.msg} />
    </>
  );
}

function Stat({ label, value }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 22, fontWeight: 700 }}>{value}</div>
      <div className="dim" style={{ fontSize: 12 }}>
        {label}
      </div>
    </div>
  );
}

function InviteModal({ bandId, onClose, onSaved }) {
  const [email, setEmail] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function send() {
    setBusy(true);
    setErr("");
    try {
      await inviteApi.send(bandId, email);
      onSaved();
    } catch (e) {
      setErr(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title="Invite Member" onClose={onClose}>
      <Field label="Email address">
        <input
          className="input"
          type="email"
          placeholder="member@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </Field>
      {err && <p className="input-error-text">{err}</p>}
      <button
        className="btn btn-primary btn-block"
        style={{ marginTop: 8 }}
        onClick={send}
        disabled={busy || !email}
      >
        {busy ? "Sending…" : "Send Invitation"}
      </button>
    </Modal>
  );
}

function EditMemberModal({ bandId, member, onClose, onSaved }) {
  const [role, setRole] = useState(member.role);
  const [instrument, setInstrument] = useState(member.instrument || "");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    setErr("");
    try {
      await memberApi.update(bandId, member.user_id, {
        role,
        instrument: instrument || null,
      });
      onSaved();
    } catch (e) {
      setErr(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title={`Edit ${member.username}`} onClose={onClose}>
      <Field label="Role">
        <select className="select" value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="member">Member</option>
          <option value="band_leader">Band Leader</option>
        </select>
      </Field>
      <Field label="Instrument">
        <select
          className="select"
          value={instrument}
          onChange={(e) => setInstrument(e.target.value)}
        >
          <option value="">None</option>
          {INSTRUMENTS.map((i) => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </select>
      </Field>
      {err && <p className="input-error-text">{err}</p>}
      <button
        className="btn btn-primary btn-block"
        style={{ marginTop: 8 }}
        onClick={save}
        disabled={busy}
      >
        {busy ? "Saving…" : "Save Changes"}
      </button>
    </Modal>
  );
}
