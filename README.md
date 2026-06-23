# 🎸 RehearsalRoom — Full-Stack App

Platform manajemen latihan band. **Hanya butuh Python** — tidak perlu Node.js
maupun PostgreSQL. Frontend React sudah di-build dan disajikan langsung oleh backend.

## ⚡ Cara Menjalankan (1 langkah)

**Windows:** dobel-klik **`start.bat`**
**Mac/Linux:** `chmod +x start.sh && ./start.sh`

Script otomatis: bikin virtualenv → install dependencies (sekali saja) →
buat database SQLite → isi data dummy → nyalakan server.

Lalu buka browser ke **http://localhost:8000** — selesai. Satu alamat saja.

> Syarat: cukup **Python 3.10+** terpasang. Database (file `rehearsalroom.db`)
> dan tabel dibuat otomatis saat pertama jalan. Tidak ada install PostgreSQL/Node.

## 🔑 Login Demo (data sudah terisi)
| Akun | Email | Password | Role |
|------|-------|----------|------|
| Ivan | `ivan@thecatalyst.id` | `password123` | Band Leader |
| Geby, Fauzi, Iman, Eval, Fudhol, Aril | `geby@thecatalyst.id` dst | `password123` | Member |

Login sebagai **Ivan** untuk fitur leader (tambah lagu, undang member, buat sesi).
Login sebagai member lain untuk lihat tampilan read-only — bagus untuk tunjukkan role-based access.

## Halaman
- **/** Login & Register
- **Dashboard** — statistik band
- **Songs** — repertoar lagu (CRUD)
- **Schedule** — kalender + sesi latihan
- **Session Detail** — lagu, progress slider, feedback
- **Members** — anggota + undangan

## Struktur & Pembagian Kerja Kelompok
```
rehearsalroom-fullstack/
├── start.bat / start.sh         ← jalankan ini
├── rehearsalroom-backend/       ← FastAPI + SQLite + JWT
│   ├── app/models/  schemas/  routers/  services/  utils/
│   ├── app/bootstrap.py         ← auto-create tabel + data dummy
│   └── app/static/              ← frontend React hasil build (disajikan FastAPI)
└── rehearsalroom-frontend/      ← SOURCE React (untuk dipelajari/diedit)
```

| Anggota | Bagian yang bisa dijelaskan |
|---------|------------------------------|
| 1 | Backend auth + models + database (FastAPI, JWT, SQLAlchemy) |
| 2 | Backend bands / members / invitations + services |
| 3 | Backend songs / sessions / progress / feedback / dashboard |
| 4 | Frontend auth + dashboard + design system |
| 5 | Frontend songs + schedule + session detail + members |

## Dokumentasi API
Swagger UI otomatis aktif di **http://localhost:8000/docs**

## Catatan
- Ingin pakai PostgreSQL? Isi `DATABASE_URL` PostgreSQL di file `.env` backend
  (lihat `.env.example`). Default tanpa `.env` = SQLite.
- Mau reset data? Hapus file `rehearsalroom-backend/rehearsalroom.db`, jalankan lagi.
- Mau ubah tampilan frontend? Edit di `rehearsalroom-frontend/` (butuh Node),
  lalu `npm run build` dan salin isi `dist/` ke `rehearsalroom-backend/app/static/`.
