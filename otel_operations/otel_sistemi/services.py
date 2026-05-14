"""
Otel Operasyon Sistemi - İş Mantığı Servisleri
Tüm CRUD ve iş kuralı operasyonları burada yer alır.
"""
import uuid
from datetime import datetime
from database import get_connection, hash_password


# ═══════════════════════════════════════════════════════════════════════════════
# Yardımcı Fonksiyonlar
# ═══════════════════════════════════════════════════════════════════════════════

def _log(conn, user_id, action, entity=None, entity_id=None, details=None):
    conn.execute(
        """INSERT INTO activityLogs(user_id, action, entity, entity_id, details)
           VALUES(?,?,?,?,?)""",
        (user_id, action, entity, entity_id, details)
    )


def _get_role_id(conn, role_name):
    row = conn.execute("SELECT id FROM userRoles WHERE name=?", (role_name,)).fetchone()
    return row["id"] if row else None


def _get_status_id(conn, table, name):
    row = conn.execute(f"SELECT id FROM {table} WHERE name=?", (name,)).fetchone()
    return row["id"] if row else None


# ═══════════════════════════════════════════════════════════════════════════════
# Kimlik Doğrulama
# ═══════════════════════════════════════════════════════════════════════════════

def login(email: str, password: str):
    """
    E-posta ve şifre ile giriş yapar.
    Başarılı olursa kullanıcı dict'ini, başarısız olursa None döner.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT u.*, r.name AS role
               FROM users u JOIN userRoles r ON u.role_id = r.id
               WHERE u.email=? AND u.password=? AND u.is_active=1""",
            (email, hash_password(password))
        ).fetchone()
        if row:
            _log(conn, row["id"], "LOGIN", "users", row["id"])
            conn.commit()
            return dict(row)
        return None
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Kullanıcı Yönetimi
# ═══════════════════════════════════════════════════════════════════════════════

def create_user(actor_id, name, surname, email, password, role_name,
                phone=None, gender_id=None):
    """
    Yeni kullanıcı oluşturur. Yalnızca manager çağırabilir (UI katmanında kontrol).
    FR5, FR6
    """
    conn = get_connection()
    try:
        role_id = _get_role_id(conn, role_name)
        if not role_id:
            raise ValueError(f"Geçersiz rol: {role_name}")
        # benzersizlik kontrolü (FR6)
        if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            raise ValueError("Bu e-posta adresi zaten kullanımda.")
        cur = conn.execute(
            """INSERT INTO users(name, surname, email, password, phone, role_id, gender_id)
               VALUES(?,?,?,?,?,?,?)""",
            (name, surname, email, hash_password(password), phone, role_id, gender_id)
        )
        uid = cur.lastrowid
        _log(conn, actor_id, "CREATE_USER", "users", uid, f"role={role_name}")
        conn.commit()
        return uid
    finally:
        conn.close()


def list_users(role_name=None):
    """Tüm kullanıcıları (isteğe bağlı role göre) listeler."""
    conn = get_connection()
    try:
        if role_name:
            rows = conn.execute(
                """SELECT u.id, u.name, u.surname, u.email, u.phone, u.is_active,
                          r.name AS role
                   FROM users u JOIN userRoles r ON u.role_id=r.id
                   WHERE r.name=?
                   ORDER BY u.name""", (role_name,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT u.id, u.name, u.surname, u.email, u.phone, u.is_active,
                          r.name AS role
                   FROM users u JOIN userRoles r ON u.role_id=r.id
                   ORDER BY r.name, u.name"""
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_user_active(actor_id, target_user_id, is_active: bool):
    """Kullanıcıyı aktif/pasif yapar. FR4"""
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET is_active=? WHERE id=?",
                     (1 if is_active else 0, target_user_id))
        _log(conn, actor_id, "SET_USER_ACTIVE", "users", target_user_id,
             f"is_active={is_active}")
        conn.commit()
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Oda Yönetimi
# ═══════════════════════════════════════════════════════════════════════════════

def list_rooms(status_name=None):
    """Odaları listeler, isteğe bağlı duruma göre filtreler."""
    conn = get_connection()
    try:
        if status_name:
            rows = conn.execute(
                """SELECT r.*, rt.name AS type_name, rt.base_price, rs.name AS status_name
                   FROM rooms r
                   JOIN roomTypes rt ON r.type_id=rt.id
                   JOIN roomStatus rs ON r.status_id=rs.id
                   WHERE rs.name=?
                   ORDER BY r.room_number""", (status_name,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT r.*, rt.name AS type_name, rt.base_price, rs.name AS status_name
                   FROM rooms r
                   JOIN roomTypes rt ON r.type_id=rt.id
                   JOIN roomStatus rs ON r.status_id=rs.id
                   ORDER BY r.room_number"""
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_available_rooms(check_in, check_out):
    """
    Verilen tarih aralığında müsait odaları döndürür.
    FR11, FR12, FR27, FR28, FR29
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT r.*, rt.name AS type_name, rt.base_price, rs.name AS status_name
               FROM rooms r
               JOIN roomTypes rt ON r.type_id=rt.id
               JOIN roomStatus rs ON r.status_id=rs.id
               WHERE rs.name = 'available'
                 AND r.id NOT IN (
                     SELECT res.room_id FROM reservations res
                     WHERE res.room_id IS NOT NULL
                       AND res.status NOT IN ('completed','cancelled')
                       AND res.check_in_date < ?
                       AND res.check_out_date > ?
                 )
               ORDER BY r.room_number""",
            (check_out, check_in)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_room_status(conn, actor_id, room_id, new_status):
    """Oda durumunu günceller (bağlantı dışarıdan gelir)."""
    status_id = _get_status_id(conn, "roomStatus", new_status)
    conn.execute("UPDATE rooms SET status_id=? WHERE id=?", (status_id, room_id))
    _log(conn, actor_id, "UPDATE_ROOM_STATUS", "rooms", room_id, f"status={new_status}")


# ═══════════════════════════════════════════════════════════════════════════════
# Rezervasyon Yönetimi
# ═══════════════════════════════════════════════════════════════════════════════

def create_reservation(actor_id, customer_id, check_in, check_out,
                       adult_count=1, child_count=0, special_requests=None):
    """
    Yeni rezervasyon oluşturur, 'pending_payment' durumunda kaydeder.
    FR8, FR9, FR13
    """
    conn = get_connection()
    try:
        if check_out <= check_in:
            raise ValueError("Çıkış tarihi, giriş tarihinden büyük olmalıdır.")
        cur = conn.execute(
            """INSERT INTO reservations(customer_id, check_in_date, check_out_date,
                                        status, created_by)
               VALUES(?,?,?,'pending_payment',?)""",
            (customer_id, check_in, check_out, actor_id)
        )
        res_id = cur.lastrowid
        conn.execute(
            """INSERT INTO reservationDetails(reservation_id, adult_count,
                                              child_count, special_requests)
               VALUES(?,?,?,?)""",
            (res_id, adult_count, child_count, special_requests)
        )
        _log(conn, actor_id, "CREATE_RESERVATION", "reservations", res_id,
             f"customer={customer_id} {check_in}→{check_out}")
        conn.commit()
        return res_id
    finally:
        conn.close()


def process_payment(actor_id, reservation_id, amount,
                    card_holder_name=None, card_last_four=None):
    """
    Ödeme simülasyonu. Başarılı olursa rezervasyonu 'active' yapar.
    FR20-FR24
    """
    conn = get_connection()
    try:
        res = conn.execute(
            "SELECT * FROM reservations WHERE id=?", (reservation_id,)
        ).fetchone()
        if not res:
            raise ValueError("Rezervasyon bulunamadı.")
        if res["status"] != "pending_payment":
            raise ValueError("Bu rezervasyonun ödemesi zaten yapılmış veya iptal edilmiş.")

        tx_code = str(uuid.uuid4()).replace("-", "").upper()[:20]
        conn.execute(
            """INSERT INTO payments(reservation_id, customer_id, amount,
                                    transaction_code, card_holder_name, card_last_four)
               VALUES(?,?,?,?,?,?)""",
            (reservation_id, res["customer_id"], amount,
             tx_code, card_holder_name, card_last_four)
        )
        conn.execute(
            "UPDATE reservations SET status='active', updated_at=datetime('now') WHERE id=?",
            (reservation_id,)
        )
        _log(conn, actor_id, "PAYMENT", "payments", reservation_id,
             f"amount={amount} tx={tx_code}")
        conn.commit()
        return tx_code
    finally:
        conn.close()


def assign_room_and_checkin(actor_id, reservation_id, room_id):
    """
    Odayı rezervasyona atar ve check-in yapar. QR kodu oluşturur.
    FR10, FR12, FR13, FR14, FR26-FR32
    """
    conn = get_connection()
    try:
        res = conn.execute(
            "SELECT * FROM reservations WHERE id=?", (reservation_id,)
        ).fetchone()
        if not res:
            raise ValueError("Rezervasyon bulunamadı.")
        if res["status"] != "active":
            raise ValueError("Rezervasyon ödemesi tamamlanmamış veya zaten check-in yapılmış.")

        # Oda müsaitlik kontrolü (FR12, FR29)
        conflict = conn.execute(
            """SELECT 1 FROM reservations
               WHERE room_id=? AND status NOT IN ('completed','cancelled')
                 AND id != ?
                 AND check_in_date < ? AND check_out_date > ?""",
            (room_id, reservation_id, res["check_out_date"], res["check_in_date"])
        ).fetchone()
        if conflict:
            raise ValueError("Seçilen oda bu tarih aralığında dolu.")

        # Oda durumu kontrolü (FR28)
        room = conn.execute(
            """SELECT r.*, rs.name AS status_name
               FROM rooms r JOIN roomStatus rs ON r.status_id=rs.id
               WHERE r.id=?""", (room_id,)
        ).fetchone()
        if not room or room["status_name"] not in ("available", "cleaning"):
            raise ValueError("Oda atanamaz (bakımda veya dolu).")

        # QR kodu üret (FR14)
        qr_code = str(uuid.uuid4()).upper()
        conn.execute(
            """INSERT INTO qrLogs(reservation_id, room_id, qr_code, valid_from, valid_until)
               VALUES(?,?,?,?,?)""",
            (reservation_id, room_id, qr_code,
             res["check_in_date"], res["check_out_date"])
        )

        # Rezervasyon güncelle
        conn.execute(
            """UPDATE reservations
               SET room_id=?, status='checked_in', updated_at=datetime('now')
               WHERE id=?""",
            (room_id, reservation_id)
        )

        # Oda durumu → occupied
        update_room_status(conn, actor_id, room_id, "occupied")

        _log(conn, actor_id, "CHECKIN", "reservations", reservation_id,
             f"room={room_id} qr={qr_code}")
        conn.commit()
        return qr_code
    finally:
        conn.close()


def checkout(actor_id, reservation_id):
    """
    Check-out işlemi. QR iptal, oda → cleaning, rezervasyon → completed.
    FR16-FR19
    """
    conn = get_connection()
    try:
        res = conn.execute(
            "SELECT * FROM reservations WHERE id=?", (reservation_id,)
        ).fetchone()
        if not res:
            raise ValueError("Rezervasyon bulunamadı.")
        if res["status"] != "checked_in":
            raise ValueError("Müşteri check-in yapmamış.")

        # Açık hizmet talebi kontrolü (Use Case 7.4.4 Alternatif)
        open_svc = conn.execute(
            """SELECT COUNT(*) AS cnt FROM roomServices
               WHERE reservation_id=? AND status NOT IN ('completed','cancelled')""",
            (reservation_id,)
        ).fetchone()["cnt"]
        if open_svc > 0:
            raise ValueError(
                f"Açık {open_svc} hizmet talebi var. Check-out yapılamaz."
            )

        # QR iptal (FR17)
        conn.execute(
            "UPDATE qrLogs SET is_active=0 WHERE reservation_id=?", (reservation_id,)
        )
        # Oda → cleaning (FR18)
        update_room_status(conn, actor_id, res["room_id"], "cleaning")
        # Rezervasyon → completed (FR19)
        conn.execute(
            "UPDATE reservations SET status='completed', updated_at=datetime('now') WHERE id=?",
            (reservation_id,)
        )
        _log(conn, actor_id, "CHECKOUT", "reservations", reservation_id)
        conn.commit()
    finally:
        conn.close()


def list_reservations(status=None, customer_id=None):
    """Rezervasyonları listeler."""
    conn = get_connection()
    try:
        where_clauses = []
        params = []
        if status:
            where_clauses.append("res.status=?")
            params.append(status)
        if customer_id:
            where_clauses.append("res.customer_id=?")
            params.append(customer_id)
        where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        rows = conn.execute(
            f"""SELECT res.*,
                       u.name || ' ' || u.surname AS customer_name,
                       u.email AS customer_email,
                       r.room_number
                FROM reservations res
                JOIN users u ON res.customer_id=u.id
                LEFT JOIN rooms r ON res.room_id=r.id
                {where}
                ORDER BY res.created_at DESC""",
            params
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Hizmet Talebi Yönetimi
# ═══════════════════════════════════════════════════════════════════════════════

def create_service_request(customer_id, service_type, description=None):
    """
    Müşteri hizmet talebi oluşturur.
    FR33-FR37
    """
    conn = get_connection()
    try:
        # Aktif konaklama var mı? (FR37)
        res = conn.execute(
            """SELECT * FROM reservations
               WHERE customer_id=? AND status='checked_in'""",
            (customer_id,)
        ).fetchone()
        if not res:
            raise ValueError("Aktif konaklamanız bulunmamaktadır.")
        if service_type not in ("cleaning", "room_service"):
            raise ValueError("Hizmet tipi 'cleaning' veya 'room_service' olmalıdır.")

        cur = conn.execute(
            """INSERT INTO roomServices(customer_id, room_id, reservation_id,
                                        service_type, description)
               VALUES(?,?,?,?,?)""",
            (customer_id, res["room_id"], res["id"], service_type, description)
        )
        svc_id = cur.lastrowid
        _log(conn, customer_id, "CREATE_SERVICE_REQUEST", "roomServices", svc_id,
             f"type={service_type}")
        conn.commit()
        return svc_id
    finally:
        conn.close()


def assign_service_to_staff(actor_id, service_id, staff_id):
    """Hizmet talebini kat görevlisine atar. FR39, FR47, FR48"""
    conn = get_connection()
    try:
        # Staff rolü kontrolü
        staff = conn.execute(
            """SELECT u.*, r.name AS role FROM users u JOIN userRoles r ON u.role_id=r.id
               WHERE u.id=? AND r.name='housekeeper'""", (staff_id,)
        ).fetchone()
        if not staff:
            raise ValueError("Belirtilen personel kat görevlisi değil.")

        conn.execute(
            "UPDATE roomServices SET assigned_to=?, status='in_progress' WHERE id=?",
            (staff_id, service_id)
        )
        conn.execute(
            """INSERT INTO staffAssignments(staff_id, service_id, assigned_by)
               VALUES(?,?,?)""",
            (staff_id, service_id, actor_id)
        )
        _log(conn, actor_id, "ASSIGN_SERVICE", "roomServices", service_id,
             f"staff={staff_id}")
        conn.commit()
    finally:
        conn.close()


def update_service_status(actor_id, service_id, new_status):
    """
    Hizmet talebi durumunu günceller.
    FR40, FR41
    """
    conn = get_connection()
    try:
        if new_status not in ("pending", "in_progress", "completed", "cancelled"):
            raise ValueError("Geçersiz durum.")
        completed_at = datetime.now().isoformat() if new_status == "completed" else None
        conn.execute(
            "UPDATE roomServices SET status=?, completed_at=? WHERE id=?",
            (new_status, completed_at, service_id)
        )
        _log(conn, actor_id, "UPDATE_SERVICE_STATUS", "roomServices", service_id,
             f"status={new_status}")
        conn.commit()
    finally:
        conn.close()


def list_service_requests(assigned_to=None, status=None, reservation_id=None):
    """Hizmet taleplerini listeler. FR38, FR39"""
    conn = get_connection()
    try:
        where_clauses = []
        params = []
        if assigned_to:
            where_clauses.append("rs.assigned_to=?")
            params.append(assigned_to)
        if status:
            where_clauses.append("rs.status=?")
            params.append(status)
        if reservation_id:
            where_clauses.append("rs.reservation_id=?")
            params.append(reservation_id)
        where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        rows = conn.execute(
            f"""SELECT rs.*,
                       u.name || ' ' || u.surname AS customer_name,
                       r.room_number,
                       staff.name || ' ' || staff.surname AS staff_name
                FROM roomServices rs
                JOIN users u ON rs.customer_id=u.id
                JOIN rooms r ON rs.room_id=r.id
                LEFT JOIN users staff ON rs.assigned_to=staff.id
                {where}
                ORDER BY rs.created_at DESC""",
            params
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# QR Yönetimi
# ═══════════════════════════════════════════════════════════════════════════════

def get_active_qr(reservation_id):
    """Aktif QR kaydını döndürür. FR14, FR15"""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT * FROM qrLogs WHERE reservation_id=? AND is_active=1""",
            (reservation_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Ödeme Raporlama
# ═══════════════════════════════════════════════════════════════════════════════

def list_payments(reservation_id=None):
    """Ödeme kayıtlarını listeler. FR24"""
    conn = get_connection()
    try:
        where = "WHERE p.reservation_id=?" if reservation_id else ""
        params = (reservation_id,) if reservation_id else ()
        rows = conn.execute(
            f"""SELECT p.*,
                       u.name || ' ' || u.surname AS customer_name,
                       r.room_number
                FROM payments p
                JOIN users u ON p.customer_id = u.id
                JOIN reservations res ON p.reservation_id = res.id
                LEFT JOIN rooms r ON res.room_id = r.id
                {where}
                ORDER BY p.paid_at DESC""",
            params
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_room_status(actor_id, room_id, new_status):
    """Odanın durumunu manuel olarak günceller. FR28 - Bakım/Müsait yönetimi"""
    conn = get_connection()
    try:
        update_room_status(conn, actor_id, room_id, new_status)
        conn.commit()
    finally:
        conn.close()


def calculate_reservation_amount(reservation_id):
    """Rezervasyon tutarını base_price × gece sayısı olarak hesaplar. (Oda atanmadıysa varsayılan 1000 TL baz alınır)"""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT res.check_in_date, res.check_out_date, r.type_id
               FROM reservations res
               LEFT JOIN rooms r ON res.room_id = r.id
               WHERE res.id = ?""",
            (reservation_id,)
        ).fetchone()
        if not row:
            return None
        
        base_price = 1000  # Default price if room/type is not yet assigned
        if row["type_id"]:
            type_row = conn.execute("SELECT base_price FROM roomTypes WHERE id=?", (row["type_id"],)).fetchone()
            if type_row:
                base_price = type_row["base_price"]

        from datetime import datetime
        d1 = datetime.strptime(row["check_in_date"], "%Y-%m-%d")
        d2 = datetime.strptime(row["check_out_date"], "%Y-%m-%d")
        nights = (d2 - d1).days
        if nights <= 0: nights = 1
        return base_price * nights
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Yönetici / Raporlama
# ═══════════════════════════════════════════════════════════════════════════════

def get_occupancy_report():
    """Doluluk raporu. FR43"""
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) AS cnt FROM rooms").fetchone()["cnt"]
        occupied = conn.execute(
            """SELECT COUNT(*) AS cnt FROM rooms r
               JOIN roomStatus rs ON r.status_id=rs.id
               WHERE rs.name='occupied'"""
        ).fetchone()["cnt"]
        cleaning = conn.execute(
            """SELECT COUNT(*) AS cnt FROM rooms r
               JOIN roomStatus rs ON r.status_id=rs.id
               WHERE rs.name='cleaning'"""
        ).fetchone()["cnt"]
        available = conn.execute(
            """SELECT COUNT(*) AS cnt FROM rooms r
               JOIN roomStatus rs ON r.status_id=rs.id
               WHERE rs.name='available'"""
        ).fetchone()["cnt"]
        rate = round(occupied / total * 100, 1) if total else 0
        return {
            "total": total,
            "occupied": occupied,
            "available": available,
            "cleaning": cleaning,
            "occupancy_rate": rate
        }
    finally:
        conn.close()


def get_activity_logs(limit=50, category=None):
    """Son aktivite kayıtları. FR50-FR56. category ile filtreleme yapılabilir."""
    conn = get_connection()
    try:
        where = ""
        params = []
        if category:
            cat_map = {
                "auth": ["LOGIN"],
                "reservation": ["CREATE_RESERVATION", "PAYMENT"],
                "checkin_checkout": ["CHECKIN", "CHECKOUT"],
                "service": ["CREATE_SERVICE_REQUEST", "ASSIGN_SERVICE", "UPDATE_SERVICE_STATUS"],
                "room": ["UPDATE_ROOM_STATUS"],
                "user": ["CREATE_USER", "SET_USER_ACTIVE"],
            }
            actions = cat_map.get(category, [])
            if actions:
                placeholders = ",".join(["?" for _ in actions])
                where = f"WHERE al.action IN ({placeholders})"
                params = actions
        query = f"""SELECT al.*, u.name || ' ' || u.surname AS user_name
               FROM activityLogs al
               LEFT JOIN users u ON al.user_id=u.id
               {where}
               ORDER BY al.logged_at DESC LIMIT ?"""
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
