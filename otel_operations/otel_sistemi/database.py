"""
Otel Operasyon Sistemi - Veritabanı Modülü
SQLite3 veritabanı bağlantısı ve tablo oluşturma işlemleri.
"""
import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "otel.db")


def get_connection():
    """Veritabanı bağlantısı döndürür."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    """SHA-256 ile şifre hashleme."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    """Tüm tabloları oluşturur ve başlangıç verilerini ekler."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Lookup tabloları ───────────────────────────────────────────────────────
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS userRoles (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT NOT NULL UNIQUE  -- 'customer', 'receptionist', 'housekeeper', 'manager'
    );

    CREATE TABLE IF NOT EXISTS genders (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT NOT NULL UNIQUE  -- 'male', 'female', 'other'
    );

    CREATE TABLE IF NOT EXISTS roomTypes (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL UNIQUE,  -- 'single', 'double', 'suite', 'deluxe'
        base_price  REAL NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS roomStatus (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT NOT NULL UNIQUE  -- 'available', 'occupied', 'cleaning', 'maintenance'
    );

    -- ── Kullanıcılar ─────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        surname     TEXT NOT NULL,
        email       TEXT NOT NULL UNIQUE,
        password    TEXT NOT NULL,
        phone       TEXT,
        role_id     INTEGER NOT NULL REFERENCES userRoles(id),
        gender_id   INTEGER REFERENCES genders(id),
        is_active   INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Odalar ───────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS rooms (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT NOT NULL UNIQUE,
        floor       INTEGER NOT NULL DEFAULT 1,
        type_id     INTEGER NOT NULL REFERENCES roomTypes(id),
        status_id   INTEGER NOT NULL REFERENCES roomStatus(id),
        capacity    INTEGER NOT NULL DEFAULT 2,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Rezervasyonlar ───────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS reservations (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES users(id),
        room_id         INTEGER REFERENCES rooms(id),
        check_in_date   TEXT NOT NULL,
        check_out_date  TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'pending_payment',
            -- pending_payment | active | checked_in | completed | cancelled
        created_by      INTEGER REFERENCES users(id),
        created_at      TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at      TEXT DEFAULT (datetime('now')),
        CHECK (check_out_date > check_in_date)
    );

    -- ── Rezervasyon Detayları ────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS reservationDetails (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        reservation_id  INTEGER NOT NULL UNIQUE REFERENCES reservations(id),
        adult_count     INTEGER NOT NULL DEFAULT 1,
        child_count     INTEGER NOT NULL DEFAULT 0,
        special_requests TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Ödemeler ─────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS payments (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        reservation_id  INTEGER NOT NULL REFERENCES reservations(id),
        customer_id     INTEGER NOT NULL REFERENCES users(id),
        amount          REAL NOT NULL,
        transaction_code TEXT NOT NULL UNIQUE,
        card_holder_name TEXT,
        card_last_four  TEXT,           -- hassas veri saklanmaz
        status          TEXT NOT NULL DEFAULT 'completed',
        paid_at         TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── İadeler ──────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS refunds (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id  INTEGER NOT NULL REFERENCES payments(id),
        amount      REAL NOT NULL,
        reason      TEXT,
        refunded_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Oda Hizmet Talepleri ─────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS roomServices (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     INTEGER NOT NULL REFERENCES users(id),
        room_id         INTEGER NOT NULL REFERENCES rooms(id),
        reservation_id  INTEGER NOT NULL REFERENCES reservations(id),
        service_type    TEXT NOT NULL,  -- 'cleaning' | 'room_service'
        description     TEXT,
        status          TEXT NOT NULL DEFAULT 'pending',
            -- pending | in_progress | completed | cancelled
        assigned_to     INTEGER REFERENCES users(id),
        completed_at    TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── QR Erişim Kayıtları ──────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS qrLogs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        reservation_id  INTEGER NOT NULL REFERENCES reservations(id),
        room_id         INTEGER NOT NULL REFERENCES rooms(id),
        qr_code         TEXT NOT NULL UNIQUE,
        is_active       INTEGER NOT NULL DEFAULT 1,
        valid_from      TEXT NOT NULL,
        valid_until     TEXT NOT NULL,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- ── Personel Atamaları ───────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS staffAssignments (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id        INTEGER NOT NULL REFERENCES users(id),
        service_id      INTEGER NOT NULL REFERENCES roomServices(id),
        assigned_at     TEXT NOT NULL DEFAULT (datetime('now')),
        assigned_by     INTEGER REFERENCES users(id)
    );

    -- ── Aktivite Logları ─────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS activityLogs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER REFERENCES users(id),
        action      TEXT NOT NULL,
        entity      TEXT,
        entity_id   INTEGER,
        details     TEXT,
        logged_at   TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)

    # ── Başlangıç Verileri ────────────────────────────────────────────────────
    # Roller
    for role in ("customer", "receptionist", "housekeeper", "manager"):
        cur.execute("INSERT OR IGNORE INTO userRoles(name) VALUES(?)", (role,))

    # Cinsiyetler
    for g in ("male", "female", "other"):
        cur.execute("INSERT OR IGNORE INTO genders(name) VALUES(?)", (g,))

    # Oda Tipleri
    for rtype, price in [("single", 500), ("double", 800), ("suite", 1500), ("deluxe", 1200)]:
        cur.execute("INSERT OR IGNORE INTO roomTypes(name, base_price) VALUES(?,?)", (rtype, price))

    # Oda Durumları
    for st in ("available", "occupied", "cleaning", "maintenance"):
        cur.execute("INSERT OR IGNORE INTO roomStatus(name) VALUES(?)", (st,))

    conn.commit()

    # ── Varsayılan Kullanıcılar ───────────────────────────────────────────────
    _seed_users(conn)
    _seed_rooms(conn)

    conn.close()
    print("[DB] Veritabanı başarıyla hazırlandı:", DB_PATH)


def _seed_users(conn):
    cur = conn.cursor()
    default_users = [
        ("Admin",     "Yönetici",  "admin@otel.com",    "admin123",   "manager"),
        ("Ahmet",     "Yılmaz",    "recep@otel.com",    "recep123",   "receptionist"),
        ("Fatma",     "Demir",     "kat@otel.com",      "kat123",     "housekeeper"),
        ("Mehmet",    "Kaya",      "musteri@otel.com",  "musteri123", "customer"),
    ]
    for name, surname, email, pwd, role_name in default_users:
        cur.execute("SELECT id FROM userRoles WHERE name=?", (role_name,))
        role_id = cur.fetchone()["id"]
        cur.execute(
            """INSERT OR IGNORE INTO users(name, surname, email, password, role_id)
               VALUES(?,?,?,?,?)""",
            (name, surname, email, hash_password(pwd), role_id)
        )
    conn.commit()


def _seed_rooms(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM roomTypes WHERE name='single'")
    row = cur.fetchone()
    if not row:
        return
    single_id  = row["id"]
    cur.execute("SELECT id FROM roomTypes WHERE name='double'")
    double_id  = cur.fetchone()["id"]
    cur.execute("SELECT id FROM roomTypes WHERE name='suite'")
    suite_id   = cur.fetchone()["id"]
    cur.execute("SELECT id FROM roomTypes WHERE name='deluxe'")
    deluxe_id  = cur.fetchone()["id"]
    cur.execute("SELECT id FROM roomStatus WHERE name='available'")
    avail_id   = cur.fetchone()["id"]

    rooms = [
        ("101", 1, single_id,  avail_id, 1),
        ("102", 1, single_id,  avail_id, 1),
        ("103", 1, double_id,  avail_id, 2),
        ("201", 2, double_id,  avail_id, 2),
        ("202", 2, deluxe_id,  avail_id, 2),
        ("301", 3, suite_id,   avail_id, 4),
        ("302", 3, suite_id,   avail_id, 4),
    ]
    for rno, floor, type_id, status_id, cap in rooms:
        cur.execute(
            """INSERT OR IGNORE INTO rooms(room_number, floor, type_id, status_id, capacity)
               VALUES(?,?,?,?,?)""",
            (rno, floor, type_id, status_id, cap)
        )
    conn.commit()


if __name__ == "__main__":
    init_db()
