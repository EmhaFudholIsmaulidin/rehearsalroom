from datetime import datetime, timedelta, timezone

from app.database import Base, engine, SessionLocal
import app.models  # noqa: F401  (pastikan semua model ter-import)
from app.utils.security import hash_password
from app.models.user import User
from app.models.band import Band, BandMember, MemberRole
from app.models.song import Song, SongProgress, SongStatus
from app.models.session import RehearsalSession, SessionSong, SessionStatus
from app.models.feedback import Feedback

PASSWORD = "password123"

MEMBERS = [
    ("Ivan",   "ivan@thecatalyst.id",   "Vocals", MemberRole.band_leader),
    ("Geby",   "geby@thecatalyst.id",   "Keys",   MemberRole.member),
    ("Fauzi",  "fauzi@thecatalyst.id",  "Guitar", MemberRole.member),
    ("Iman",   "iman@thecatalyst.id",   "Bass",   MemberRole.member),
    ("Eval",   "eval@thecatalyst.id",   "Drums",  MemberRole.member),
    ("Fudhol", "fudhol@thecatalyst.id", "Guitar", MemberRole.member),
    ("Aril",   "aril@thecatalyst.id",   "Vocals", MemberRole.member),
]

SONGS = [
    ("Kuning",            "Rumahsakit",            270, SongStatus.ready),
    ("Tarung Bebas",      "Perunggu",              230, SongStatus.ready),
    ("O Tuan",            ".Feast",                250, SongStatus.learning),
    ("Roman Picisan",     "Dewa 19",               300, SongStatus.ready),
    ("Hysteria",          "Muse",                  227, SongStatus.learning),
    ("Soul To Squeeze",   "Red Hot Chili Peppers", 280, SongStatus.on_hold),
    ("Hidup Begini Saja", "Hindia",                240, SongStatus.learning),
    ("Evaluasi",          "Hindia",                255, SongStatus.ready),
    ("Can't Stop",        "Red Hot Chili Peppers", 269, SongStatus.on_hold),
    ("Sial",              "Mahalini",              262, SongStatus.learning),
]


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_if_empty(force: bool = False):
    init_db()
    db = SessionLocal()
    try:
        if not force and db.query(Band).filter(Band.name == "The Catalyst").first():
            return False  # sudah ada, lewati

        now = datetime.now(timezone.utc)

        users = {}
        for username, email, _i, _r in MEMBERS:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(username=username, email=email,
                         hashed_password=hash_password(PASSWORD))
                db.add(u)
            users[username] = u
        db.flush()

        leader = users["Ivan"]
        band = Band(name="The Catalyst", genre="Indie Rock / Alternative",
                    formed_year=2022, created_by=leader.id)
        db.add(band)
        db.flush()

        for username, _e, instrument, role in MEMBERS:
            db.add(BandMember(band_id=band.id, user_id=users[username].id,
                              role=role, instrument=instrument,
                              joined_at=now - timedelta(days=120)))

        songs = []
        for i, (title, composer, dur, status) in enumerate(SONGS):
            s = Song(band_id=band.id, title=title, composer=composer,
                     duration_seconds=dur, status=status, added_by=leader.id,
                     created_at=now - timedelta(days=90 - i * 5))
            db.add(s)
            songs.append(s)
        db.flush()

        past = RehearsalSession(band_id=band.id, title="Latihan Rutin Mingguan",
                                scheduled_at=now - timedelta(days=6, hours=4),
                                duration_minutes=150, location="Studio Reverb, Lt. 2",
                                status=SessionStatus.completed, created_by=leader.id)
        up1 = RehearsalSession(band_id=band.id, title="Persiapan Gigs Kampus",
                               scheduled_at=now + timedelta(days=2, hours=2),
                               duration_minutes=180, location="Studio Reverb, Lt. 2",
                               status=SessionStatus.upcoming, created_by=leader.id)
        up2 = RehearsalSession(band_id=band.id, title="Run-through Full Set",
                               scheduled_at=now + timedelta(days=8, hours=3),
                               duration_minutes=120, location="Basecamp Fauzi",
                               status=SessionStatus.upcoming, created_by=leader.id)
        db.add_all([past, up1, up2])
        db.flush()

        def attach(session, song_list, progress_map=None):
            for idx, song in enumerate(song_list):
                db.add(SessionSong(session_id=session.id, song_id=song.id,
                                   order_index=idx))
                if progress_map and song in progress_map:
                    pct, notes, updater = progress_map[song]
                    db.add(SongProgress(session_id=session.id, song_id=song.id,
                                        updated_by=updater.id, progress_pct=pct,
                                        notes=notes,
                                        updated_at=session.scheduled_at + timedelta(hours=1)))

        attach(past, [songs[0], songs[1], songs[3], songs[4]], {
            songs[0]: (95, "Aman, tinggal poles ending.", users["Fauzi"]),
            songs[1]: (90, "Tempo intro masih kecepetan.", users["Eval"]),
            songs[3]: (100, "Siap dibawakan live.", leader),
            songs[4]: (55, "Bridge perlu latihan lagi.", users["Geby"]),
        })
        attach(up1, [songs[0], songs[1], songs[3], songs[7], songs[2]], {
            songs[2]: (40, "Masih hafalan lirik.", users["Aril"]),
            songs[7]: (80, "Synth part udah oke.", users["Geby"]),
        })
        attach(up2, [songs[0], songs[1], songs[3], songs[4], songs[7], songs[2]])

        for user, content in [
            (users["Eval"],  "Drum fill di Tarung Bebas udah jauh lebih rapi minggu ini. Mantap."),
            (users["Geby"],  "Tolong next session fokus ke transisi Hysteria, masih agak kaku."),
            (users["Fauzi"], "Gitar lead Roman Picisan udah pas, tinggal jaga dinamika pas chorus."),
            (leader,         "Overall progress bagus. Target: 6 lagu ready sebelum gigs kampus."),
        ]:
            db.add(Feedback(session_id=past.id, user_id=user.id, content=content,
                            created_at=past.scheduled_at + timedelta(hours=2, minutes=30)))

        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
