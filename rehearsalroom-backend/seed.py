"""
Isi data dummy secara manual (opsional — server juga auto-seed saat startup).
Jalankan dari folder rehearsalroom-backend:
    python seed.py
"""
from app.bootstrap import seed_if_empty

if __name__ == "__main__":
    created = seed_if_empty()
    if created:
        print("✅ Seed berhasil! Band: The Catalyst (7 member, 10 lagu, 3 sesi)")
        print("   Login: ivan@thecatalyst.id / password123  (Band Leader)")
        print("   Member: geby@/fauzi@/iman@/eval@/fudhol@/aril@thecatalyst.id")
        print("   Semua password: password123")
    else:
        print("⚠️  Data sudah ada, seed dilewati.")
