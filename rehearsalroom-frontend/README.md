# 🎸 RehearsalRoom — Frontend

React + Vite frontend untuk RehearsalRoom, mengonsumsi REST API FastAPI di backend.

## Tech Stack
- **React 18** + **Vite 5**
- **React Router 6** (routing)
- **Axios** (HTTP client, auto-refresh JWT)
- Design system: dark mode, accent amber `#F5A623`, font **Sora**

## Halaman
| Route | Halaman | Akses |
|-------|---------|-------|
| `/login` | Landing + Login/Register | Publik |
| `/dashboard` | Statistik band | Member + Leader |
| `/songs` | Song Library (CRUD) | Lihat: semua · Edit: Leader |
| `/schedule` | Kalender + sesi latihan | Lihat: semua · Buat: Leader |
| `/sessions/:id` | Detail sesi: lagu, progress slider, feedback | Semua member |
| `/members` | Anggota band + undangan | Lihat: semua · Kelola: Leader |

## Cara Menjalankan

### 1. Pastikan backend sudah jalan dulu
```bash
# di folder rehearsalroom-backend
uvicorn app.main:app --reload     # → http://localhost:8000
```

### 2. Install & jalankan frontend
```bash
# di folder rehearsalroom-frontend
npm install
npm run dev        # → http://localhost:5173
```

Vite sudah dikonfigurasi mem-proxy semua request `/api/*` ke `http://localhost:8000`,
jadi tidak ada masalah CORS saat development.

### 3. Build untuk produksi
```bash
npm run build      # output di folder dist/
npm run preview    # preview hasil build
```

## Alur Penggunaan
1. **Register** akun baru di halaman login (tab Register).
2. Setelah login, kalau belum punya band → **Create a Band** (kamu otomatis jadi Band Leader).
3. **Songs** → tambah repertoar lagu band.
4. **Schedule** → buat sesi latihan, klik tanggal untuk lihat detail.
5. **Session Detail** → tambah lagu ke sesi, update progress (slider 0–100%), tulis feedback.
6. **Members** → undang anggota via email, atur role & instrumen.

## Pembagian Kerja (untuk kelompok)
Tiap halaman cukup independen, mudah dibagi per anggota:
- **Auth & routing** — `pages/Auth.jsx`, `context/AuthContext.jsx`, `App.jsx`
- **Dashboard** — `pages/Dashboard.jsx`
- **Songs** — `pages/Songs.jsx`
- **Schedule + Session Detail** — `pages/Schedule.jsx`, `pages/SessionDetail.jsx`
- **Members & invitations** — `pages/Members.jsx`
- **Design system & komponen** — `index.css`, `components/`

## Catatan
- Token JWT disimpan di `localStorage`. Saat access token expired (15 menit),
  axios otomatis refresh pakai refresh token — user tidak perlu login ulang.
- UI menyesuaikan role: tombol Add/Edit/Delete & undangan hanya muncul untuk Band Leader.
- Email undangan di backend default-nya stub (print token ke console server) —
  untuk testing, ambil token dari console backend lalu daftarkan user dengan email
  yang sama untuk menerima undangan.
