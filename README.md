![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

# 🎸 RehearsalRoom

![Dashboard Preview](dashboard.png)

Aplikasi web full-stack untuk mengelola latihan band, mulai dari manajemen repertoar lagu, jadwal latihan, progres sesi, hingga kolaborasi antar anggota band.

Frontend React telah di-build dan disajikan langsung oleh backend FastAPI sehingga aplikasi dapat dijalankan dengan konfigurasi yang sederhana.

## ✨ Fitur Utama

* 🔐 Login dan registrasi pengguna
* 🎵 Manajemen repertoar lagu (CRUD)
* 📅 Penjadwalan sesi latihan
* 📈 Tracking progres latihan
* 💬 Feedback dan catatan sesi
* 👥 Manajemen anggota band
* 📊 Dashboard statistik latihan

---

## 🛠️ Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* JWT Authentication
* SQLite (default)
* PostgreSQL (opsional)

### Frontend

* React
* TypeScript
* Vite

---

## 🚀 Menjalankan Aplikasi

### Prasyarat

Pastikan telah terpasang:

* Python 3.10 atau lebih baru

### Menjalankan

**Windows**

```bash
start.bat
```

**Linux / macOS**

```bash
chmod +x start.sh
./start.sh
```

Script akan secara otomatis:

1. Membuat virtual environment
2. Menginstall dependency
3. Membuat database
4. Mengisi data dummy
5. Menjalankan server

Setelah berhasil dijalankan, buka:

```text
http://localhost:8000
```

---

## 📖 API Documentation

Dokumentasi API tersedia melalui Swagger UI:

```text
http://localhost:8000/docs
```

---

## 🔑 Akun Demo

| Email                                             | Password    | Role        |
| ------------------------------------------------- | ----------- | ----------- |
| [ivan@thecatalyst.id](mailto:ivan@thecatalyst.id) | password123 | Band Leader |
| [geby@thecatalyst.id](mailto:geby@thecatalyst.id) | password123 | Member      |

Data dummy lainnya akan dibuat secara otomatis saat inisialisasi database.

---

## 📂 Struktur Proyek

```text
rehearsalroom/
├── start.bat
├── start.sh
├── rehearsalroom-backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── bootstrap.py
│   │   └── static/
│   └── rehearsalroom.db
└── rehearsalroom-frontend/
```

---

## 🗄️ Database

Secara default aplikasi menggunakan SQLite dan database akan dibuat otomatis saat pertama kali dijalankan.

Apabila ingin menggunakan PostgreSQL, atur variabel lingkungan berikut:

```env
DATABASE_URL=postgresql://username:password@localhost/rehearsalroom
```

---

## 💻 Pengembangan Frontend

Source code frontend berada pada direktori:

```text
rehearsalroom-frontend/
```

Untuk melakukan perubahan pada frontend:

```bash
npm install
npm run build
```

Hasil build kemudian ditempatkan pada:

```text
rehearsalroom-backend/app/static/
```

---

## 📄 Lisensi

Proyek ini dikembangkan untuk tujuan pembelajaran dan pengembangan perangkat lunak.
