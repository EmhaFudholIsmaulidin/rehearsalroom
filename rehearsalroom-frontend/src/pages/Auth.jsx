import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Field } from "../components/ui";
import { errMsg } from "../api";

export default function Auth() {
  const [tab, setTab] = useState("login");
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit() {
    setError("");
    setBusy(true);
    try {
      if (tab === "login") {
        await login(form.email, form.password);
      } else {
        await register({
          username: form.username,
          email: form.email,
          password: form.password,
        });
      }
      navigate("/dashboard");
    } catch (e) {
      setError(errMsg(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-hero">
        <div className="logo" style={{ marginBottom: 60 }}>
          <span className="logo-mark">🔊</span>
          <span>RehearsalRoom</span>
        </div>
        <span
          className="badge badge-leader"
          style={{ width: "fit-content", marginBottom: 24 }}
        >
          ⚡ Now in public beta
        </span>
        <h1 className="hero-title">
          Your Band,
          <br />
          <span className="accent">In Sync.</span>
        </h1>
        <p className="muted" style={{ marginTop: 20, maxWidth: 420, lineHeight: 1.6 }}>
          Schedule rehearsals, track song progress, and keep every member on the
          same page — all in one place built for indie bands.
        </p>
        <div className="waveform">
          {Array.from({ length: 40 }).map((_, i) => (
            <span
              key={i}
              style={{
                height: `${15 + Math.abs(Math.sin(i * 0.9)) * 45}px`,
                opacity: i % 3 === 0 ? 1 : 0.5,
              }}
            />
          ))}
        </div>
        <span className="dim" style={{ fontSize: 12, letterSpacing: 2 }}>
          REAL-TIME BAND SYNC
        </span>
      </div>

      <div className="auth-panel">
        <div style={{ maxWidth: 380, width: "100%", margin: "0 auto" }}>
          <div className="auth-tabs">
            <button
              className={`auth-tab ${tab === "login" ? "active" : ""}`}
              onClick={() => setTab("login")}
            >
              Sign In
            </button>
            <button
              className={`auth-tab ${tab === "register" ? "active" : ""}`}
              onClick={() => setTab("register")}
            >
              Register
            </button>
          </div>

          <h2 style={{ fontSize: 24, marginBottom: 6 }}>
            {tab === "login" ? "Welcome back" : "Create your account"}
          </h2>
          <p className="muted" style={{ marginBottom: 24, fontSize: 13 }}>
            {tab === "login"
              ? "Sign in to manage your band."
              : "Free forever for bands under 5 members."}
          </p>

          {tab === "register" && (
            <Field>
              <input
                className="input"
                placeholder="Username"
                value={form.username}
                onChange={set("username")}
              />
            </Field>
          )}
          <Field>
            <input
              className="input"
              type="email"
              placeholder="Email address"
              value={form.email}
              onChange={set("email")}
              onKeyDown={(e) => e.key === "Enter" && submit()}
            />
          </Field>
          <Field>
            <input
              className="input"
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={set("password")}
              onKeyDown={(e) => e.key === "Enter" && submit()}
            />
          </Field>

          {error && (
            <p className="input-error-text" style={{ marginBottom: 14 }}>
              {error}
            </p>
          )}

          <button
            className="btn btn-primary btn-block"
            onClick={submit}
            disabled={busy}
          >
            {busy ? "Please wait…" : tab === "login" ? "Sign In" : "Create Account"}
          </button>

          <p
            className="muted"
            style={{ textAlign: "center", marginTop: 18, fontSize: 13 }}
          >
            {tab === "login" ? "New here? " : "Already have an account? "}
            <button
              className="accent"
              style={{ fontWeight: 600 }}
              onClick={() => setTab(tab === "login" ? "register" : "login")}
            >
              {tab === "login" ? "Create one" : "Sign in"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
