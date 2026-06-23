import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// ── Token storage ──────────────────────────────────────
export const tokens = {
  get access() {
    return localStorage.getItem("access_token");
  },
  get refresh() {
    return localStorage.getItem("refresh_token");
  },
  set({ access_token, refresh_token }) {
    if (access_token) localStorage.setItem("access_token", access_token);
    if (refresh_token) localStorage.setItem("refresh_token", refresh_token);
  },
  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};

// Attach access token to every request
api.interceptors.request.use((config) => {
  const t = tokens.access;
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

// Auto-refresh on 401
let refreshing = null;
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      !original._retry &&
      tokens.refresh &&
      !original.url.includes("/auth/")
    ) {
      original._retry = true;
      try {
        refreshing =
          refreshing ||
          api.post("/auth/refresh", { refresh_token: tokens.refresh });
        const { data } = await refreshing;
        refreshing = null;
        tokens.set(data);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        refreshing = null;
        tokens.clear();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// Helper to surface FastAPI's {"detail": "..."} messages
export const errMsg = (e) =>
  e?.response?.data?.detail || e?.message || "Terjadi kesalahan";

// ── Auth ───────────────────────────────────────────────
export const authApi = {
  register: (body) => api.post("/auth/register", body).then((r) => r.data),
  login: (body) => api.post("/auth/login", body).then((r) => r.data),
  logout: (refresh_token) => api.post("/auth/logout", { refresh_token }),
  me: () => api.get("/auth/me").then((r) => r.data),
};

// ── Bands ──────────────────────────────────────────────
export const bandApi = {
  create: (body) => api.post("/bands", body).then((r) => r.data),
  myBands: () => api.get("/bands/my").then((r) => r.data),
  get: (id) => api.get(`/bands/${id}`).then((r) => r.data),
  update: (id, body) => api.patch(`/bands/${id}`, body).then((r) => r.data),
  remove: (id) => api.delete(`/bands/${id}`),
  dashboard: (id) => api.get(`/bands/${id}/dashboard`).then((r) => r.data),
};

// ── Members & Invitations ──────────────────────────────
export const memberApi = {
  list: (bandId) =>
    api.get(`/bands/${bandId}/members`).then((r) => r.data),
  remove: (bandId, userId) =>
    api.delete(`/bands/${bandId}/members/${userId}`),
  update: (bandId, userId, body) =>
    api.patch(`/bands/${bandId}/members/${userId}`, body).then((r) => r.data),
};

export const inviteApi = {
  send: (bandId, invited_email) =>
    api
      .post(`/bands/${bandId}/invitations`, { invited_email })
      .then((r) => r.data),
  list: (bandId) =>
    api.get(`/bands/${bandId}/invitations`).then((r) => r.data),
  cancel: (bandId, id) => api.delete(`/bands/${bandId}/invitations/${id}`),
  accept: (token) =>
    api.post("/invitations/accept", { token }).then((r) => r.data),
};

// ── Songs ──────────────────────────────────────────────
export const songApi = {
  list: (bandId) => api.get(`/bands/${bandId}/songs`).then((r) => r.data),
  create: (bandId, body) =>
    api.post(`/bands/${bandId}/songs`, body).then((r) => r.data),
  get: (bandId, songId) =>
    api.get(`/bands/${bandId}/songs/${songId}`).then((r) => r.data),
  update: (bandId, songId, body) =>
    api.patch(`/bands/${bandId}/songs/${songId}`, body).then((r) => r.data),
  remove: (bandId, songId) =>
    api.delete(`/bands/${bandId}/songs/${songId}`),
  setStatus: (bandId, songId, status) =>
    api
      .patch(`/bands/${bandId}/songs/${songId}/status`, { status })
      .then((r) => r.data),
};

// ── Sessions ───────────────────────────────────────────
export const sessionApi = {
  list: (bandId) => api.get(`/bands/${bandId}/sessions`).then((r) => r.data),
  create: (bandId, body) =>
    api.post(`/bands/${bandId}/sessions`, body).then((r) => r.data),
  get: (bandId, sessionId) =>
    api.get(`/bands/${bandId}/sessions/${sessionId}`).then((r) => r.data),
  update: (bandId, sessionId, body) =>
    api
      .patch(`/bands/${bandId}/sessions/${sessionId}`, body)
      .then((r) => r.data),
  remove: (bandId, sessionId) =>
    api.delete(`/bands/${bandId}/sessions/${sessionId}`),
  setStatus: (bandId, sessionId, status) =>
    api
      .patch(`/bands/${bandId}/sessions/${sessionId}/status`, { status })
      .then((r) => r.data),
  addSong: (sessionId, song_id) =>
    api
      .post(`/sessions/${sessionId}/songs`, { song_id })
      .then((r) => r.data),
  removeSong: (sessionId, songId) =>
    api.delete(`/sessions/${sessionId}/songs/${songId}`),
};

// ── Progress ───────────────────────────────────────────
export const progressApi = {
  list: (sessionId) =>
    api.get(`/sessions/${sessionId}/progress`).then((r) => r.data),
  upsert: (sessionId, body) =>
    api.post(`/sessions/${sessionId}/progress`, body).then((r) => r.data),
};

// ── Feedback ───────────────────────────────────────────
export const feedbackApi = {
  list: (sessionId) =>
    api.get(`/sessions/${sessionId}/feedback`).then((r) => r.data),
  create: (sessionId, content) =>
    api.post(`/sessions/${sessionId}/feedback`, { content }).then((r) => r.data),
  remove: (sessionId, id) =>
    api.delete(`/sessions/${sessionId}/feedback/${id}`),
};

export default api;
