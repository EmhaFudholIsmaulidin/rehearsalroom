# 🎸 RehearsalRoom Backend

Platform manajemen jadwal dan progres latihan untuk band indie/rintisan.

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Framework | FastAPI (Python 3.11+) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 + Alembic |
| Auth | JWT (access + refresh token) |
| Password | bcrypt via passlib |
| Docs | Swagger UI (`/docs`) |
| Frontend | Vite + ReactJS (http://localhost:5173) |

---

## Struktur Proyek

```
rehearsalroom-backend/
├── app/
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Environment variables
│   ├── database.py          # SQLAlchemy engine + session
│   ├── dependencies.py      # get_current_user, require_band_leader
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic v2 request/response schemas
│   ├── routers/             # FastAPI router per fitur
│   ├── services/            # Business logic
│   └── utils/
│       ├── security.py      # JWT + bcrypt
│       └── email.py         # Kirim undangan email (SMTP/stub)
├── alembic/                 # Database migrations
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

## Cara Setup & Menjalankan

### 1. Prerequisites

- Python 3.11+
- PostgreSQL (running, buat database `rehearsalroom`)
- pip

### 2. Clone dan masuk ke folder

```bash
cd rehearsalroom-backend
```

### 3. Buat virtual environment

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Konfigurasi environment

```bash
cp .env.example .env
```

Edit `.env` sesuai konfigurasi lokal kamu:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/rehearsalroom
SECRET_KEY=ganti-dengan-secret-key-yang-kuat
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=http://localhost:5173
```

### 6. Buat database PostgreSQL

```bash
psql -U postgres -c "CREATE DATABASE rehearsalroom;"
```

### 7. Jalankan migrasi Alembic

```bash
# Inisialisasi (sudah ada migration awal)
alembic upgrade head
```

### 8. Jalankan server

```bash
uvicorn app.main:app --reload
```

Server berjalan di: **http://localhost:8000**

---

## Dokumentasi API

| URL | Deskripsi |
|-----|-----------|
| http://localhost:8000/docs | Swagger UI (interaktif) |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |

---

## Endpoint Summary

### Auth
```
POST   /api/v1/auth/register       Daftar user baru
POST   /api/v1/auth/login          Login → access + refresh token
POST   /api/v1/auth/refresh        Refresh access token
POST   /api/v1/auth/logout         Logout / invalidate refresh token
GET    /api/v1/auth/me             Profil user login
```

### Bands
```
POST   /api/v1/bands                    Buat band baru
GET    /api/v1/bands/my                 List band saya
GET    /api/v1/bands/{band_id}          Detail band
PATCH  /api/v1/bands/{band_id}          Edit band [leader]
DELETE /api/v1/bands/{band_id}          Hapus band [leader]
```

### Members
```
GET    /api/v1/bands/{band_id}/members              List anggota
DELETE /api/v1/bands/{band_id}/members/{user_id}    Keluarkan member [leader]
PATCH  /api/v1/bands/{band_id}/members/{user_id}    Update role/instrumen [leader]
```

### Invitations
```
POST   /api/v1/bands/{band_id}/invitations           Kirim undangan [leader]
GET    /api/v1/bands/{band_id}/invitations           List undangan pending [leader]
DELETE /api/v1/bands/{band_id}/invitations/{id}      Batalkan undangan [leader]
POST   /api/v1/invitations/accept                    Terima undangan via token
```

### Songs
```
GET    /api/v1/bands/{band_id}/songs                 List lagu
POST   /api/v1/bands/{band_id}/songs                 Tambah lagu [leader]
GET    /api/v1/bands/{band_id}/songs/{song_id}       Detail lagu
PATCH  /api/v1/bands/{band_id}/songs/{song_id}       Edit lagu [leader]
DELETE /api/v1/bands/{band_id}/songs/{song_id}       Hapus lagu [leader]
PATCH  /api/v1/bands/{band_id}/songs/{song_id}/status  Update status [leader]
```

### Sessions
```
GET    /api/v1/bands/{band_id}/sessions              List sesi
POST   /api/v1/bands/{band_id}/sessions              Buat sesi [leader]
GET    /api/v1/bands/{band_id}/sessions/{id}         Detail sesi + lagu + progres
PATCH  /api/v1/bands/{band_id}/sessions/{id}         Edit sesi [leader]
DELETE /api/v1/bands/{band_id}/sessions/{id}         Hapus sesi [leader]
PATCH  /api/v1/bands/{band_id}/sessions/{id}/status  Update status [leader]
```

### Session Songs
```
POST   /api/v1/sessions/{session_id}/songs           Tambah lagu ke sesi [leader]
DELETE /api/v1/sessions/{session_id}/songs/{song_id} Hapus lagu dari sesi [leader]
PATCH  /api/v1/sessions/{session_id}/songs/reorder   Ubah urutan lagu [leader]
```

### Song Progress
```
GET    /api/v1/sessions/{session_id}/progress        List progres semua lagu
POST   /api/v1/sessions/{session_id}/progress        Buat/update progres lagu
```

### Feedback
```
GET    /api/v1/sessions/{session_id}/feedback        List feedback
POST   /api/v1/sessions/{session_id}/feedback        Tambah feedback
DELETE /api/v1/sessions/{session_id}/feedback/{id}   Hapus feedback sendiri
```

### Dashboard
```
GET    /api/v1/bands/{band_id}/dashboard             Ringkasan statistik band
```

---

## Contoh Request

### Register + Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "gitaris123", "email": "gitar@band.com", "password": "rahasia123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "gitar@band.com", "password": "rahasia123"}'
```

### Buat Band

```bash
curl -X POST http://localhost:8000/api/v1/bands \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Melodi Senja", "genre": "Indie Pop", "formed_year": 2023}'
```

---

## User Roles

| Role | Kemampuan |
|------|-----------|
| `band_leader` | CRUD band, undang/keluarkan member, buat sesi, kelola lagu |
| `member` | Lihat data band, update progres lagu, tambah feedback |

---

## Pengembangan

### Generate migrasi baru (setelah ubah model)

```bash
alembic revision --autogenerate -m "deskripsi perubahan"
alembic upgrade head
```

### Rollback migrasi

```bash
alembic downgrade -1
```

### Cek status migrasi

```bash
alembic current
alembic history
```

---

## Konfigurasi Email Undangan

Secara default, email undangan **tidak benar-benar terkirim** (stub mode — cukup print ke console). Untuk mengaktifkan pengiriman email nyata, isi variabel SMTP di `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=akun@gmail.com
SMTP_PASSWORD=app-password-gmail
```

> Untuk Gmail, gunakan **App Password** (bukan password utama). Aktifkan 2FA terlebih dahulu di akun Google-mu.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'app'`**  
Pastikan kamu menjalankan dari folder root `rehearsalroom-backend/`, bukan dari dalam `app/`.

**`sqlalchemy.exc.OperationalError: could not connect to server`**  
Pastikan PostgreSQL berjalan dan `DATABASE_URL` di `.env` sudah benar.

**`alembic.util.exc.CommandError: Can't locate revision`**  
Jalankan `alembic upgrade head` untuk menerapkan semua migration.
