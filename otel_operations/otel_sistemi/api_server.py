"""
Otel Operasyon Sistemi - Flask REST API
Tüm roller (Admin, Resepsiyonist, Kat Görevlisi, Müşteri) bu API üzerinden çalışır.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import init_db, get_connection
import services as svc

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

# ── Yardımcı ─────────────────────────────────────────────────────────────────

def ok(data=None, msg="OK"):
    return jsonify({"success": True, "message": msg, "data": data})

def err(msg, code=400):
    return jsonify({"success": False, "message": msg, "data": None}), code


# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def login():
    body = request.json or {}
    user = svc.login(body.get("email", ""), body.get("password", ""))
    if not user:
        return err("E-posta veya şifre hatalı.", 401)
    user.pop("password", None)
    return ok(user)


# ── Kullanıcı Yönetimi ───────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
def get_users():
    role = request.args.get("role")
    rows = svc.list_users(role)
    return ok(rows)


@app.route("/api/users", methods=["POST"])
def create_user():
    body = request.json or {}
    try:
        uid = svc.create_user(
            body["actor_id"], body["name"], body["surname"],
            body["email"], body["password"], body["role"],
            body.get("phone"), body.get("gender_id")
        )
        return ok({"id": uid}, "Kullanıcı oluşturuldu.")
    except Exception as e:
        return err(str(e))


@app.route("/api/users/<int:uid>/toggle", methods=["PATCH"])
def toggle_user(uid):
    body = request.json or {}
    try:
        svc.set_user_active(body["actor_id"], uid, body["is_active"])
        return ok(msg="Kullanıcı durumu güncellendi.")
    except Exception as e:
        return err(str(e))


# ── QR / Kod Doğrulama ────────────────────────────────────────────────────────

@app.route("/api/verify-access", methods=["POST"])
def verify_access():
    body = request.json or {}
    code = (body.get("code") or "").strip().upper()
    if not code:
        return err("Kod boş olamaz.")

    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT q.*, r.room_number, res.check_in_date, res.check_out_date,
                      u.name || ' ' || u.surname AS guest_name
               FROM qrLogs q
               JOIN rooms r ON q.room_id = r.id
               JOIN reservations res ON q.reservation_id = res.id
               JOIN users u ON res.customer_id = u.id
               WHERE q.qr_code = ? AND q.is_active = 1""",
            (code,)
        ).fetchone()
        if not row:
            return err("Geçersiz veya süresi dolmuş erişim kodu.", 404)

        from datetime import date
        today = str(date.today())
        if not (row["valid_from"] <= today <= row["valid_until"]):
            return err("Erişim kodunun geçerlilik süresi dışında.", 403)

        return ok({
            "room_number": row["room_number"],
            "guest_name":  row["guest_name"],
            "valid_from":  row["valid_from"],
            "valid_until": row["valid_until"],
            "qr_code":     row["qr_code"],
        }, "Erişim onaylandı!")
    finally:
        conn.close()


@app.route("/api/my-access", methods=["POST"])
def my_access():
    body = request.json or {}
    cid  = body.get("customer_id")
    if not cid:
        return err("customer_id gerekli.")

    reservations = svc.list_reservations(status="checked_in", customer_id=int(cid))
    if not reservations:
        return err("Aktif konaklamanız bulunamadı.", 404)

    res = reservations[0]
    qr  = svc.get_active_qr(res["id"])
    if not qr:
        return err("QR erişim kodunuz bulunamadı.", 404)

    return ok({
        "room_number":  res["room_number"],
        "check_in_date":  res["check_in_date"],
        "check_out_date": res["check_out_date"],
        "qr_code":        qr["qr_code"],
        "valid_until":    qr["valid_until"],
    })


# ── Oda ──────────────────────────────────────────────────────────────────────

@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    status = request.args.get("status")
    rooms  = svc.list_rooms(status)
    return ok(rooms)


@app.route("/api/rooms/available", methods=["GET"])
def get_available_rooms():
    ci = request.args.get("check_in")
    co = request.args.get("check_out")
    if not ci or not co:
        return err("check_in ve check_out gerekli.")
    rooms = svc.get_available_rooms(ci, co)
    return ok(rooms)


@app.route("/api/rooms/<int:rid>/status", methods=["PATCH"])
def change_room_status(rid):
    body = request.json or {}
    try:
        svc.set_room_status(body["actor_id"], rid, body["status"])
        return ok(msg="Oda durumu güncellendi.")
    except Exception as e:
        return err(str(e))


# ── Rezervasyonlar ────────────────────────────────────────────────────────────

@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    status      = request.args.get("status")
    customer_id = request.args.get("customer_id", type=int)
    rows = svc.list_reservations(status=status, customer_id=customer_id)
    return ok(rows)


@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    body = request.json or {}
    try:
        res_id = svc.create_reservation(
            body["actor_id"], body["customer_id"],
            body["check_in"], body["check_out"],
            body.get("adult_count", 1), body.get("child_count", 0),
            body.get("special_requests")
        )
        return ok({"id": res_id}, "Rezervasyon oluşturuldu.")
    except Exception as e:
        return err(str(e))


@app.route("/api/reservations/<int:rid>/pay", methods=["POST"])
def pay_reservation(rid):
    body = request.json or {}
    try:
        tx = svc.process_payment(
            body["actor_id"], rid, float(body["amount"]),
            body.get("card_holder_name"), body.get("card_last_four")
        )
        return ok({"transaction_code": tx}, "Ödeme başarılı.")
    except Exception as e:
        return err(str(e))


@app.route("/api/reservations/<int:rid>/checkin", methods=["POST"])
def checkin_reservation(rid):
    body = request.json or {}
    try:
        qr = svc.assign_room_and_checkin(body["actor_id"], rid, body["room_id"])
        return ok({"qr_code": qr}, "Check-in başarılı.")
    except Exception as e:
        return err(str(e))


@app.route("/api/reservations/<int:rid>/checkout", methods=["POST"])
def checkout_reservation(rid):
    body = request.json or {}
    try:
        svc.checkout(body["actor_id"], rid)
        return ok(msg="Check-out başarılı.")
    except Exception as e:
        return err(str(e))


@app.route("/api/reservations/<int:rid>/amount", methods=["GET"])
def get_reservation_amount(rid):
    amount = svc.calculate_reservation_amount(rid)
    return ok({"amount": amount})


# ── Hizmet Talepleri ──────────────────────────────────────────────────────────

@app.route("/api/services", methods=["GET"])
def get_services():
    assigned_to = request.args.get("assigned_to", type=int)
    status      = request.args.get("status")
    rows = svc.list_service_requests(assigned_to=assigned_to, status=status)
    return ok(rows)


@app.route("/api/services", methods=["POST"])
def create_service():
    body = request.json or {}
    try:
        sid = svc.create_service_request(
            body["customer_id"],
            body["service_type"],
            body.get("description")
        )
        return ok({"id": sid}, "Hizmet talebi oluşturuldu.")
    except Exception as e:
        return err(str(e))


@app.route("/api/services/<int:sid>/status", methods=["PATCH"])
def update_service(sid):
    body = request.json or {}
    try:
        svc.update_service_status(body.get("actor_id", 0), sid, body["status"])
        return ok(msg="Durum güncellendi.")
    except Exception as e:
        return err(str(e))


@app.route("/api/services/<int:sid>/assign", methods=["POST"])
def assign_service(sid):
    body = request.json or {}
    try:
        svc.assign_service_to_staff(body["actor_id"], sid, body["staff_id"])
        return ok(msg="Görev atandı.")
    except Exception as e:
        return err(str(e))


# ── Raporlar ─────────────────────────────────────────────────────────────────

@app.route("/api/occupancy", methods=["GET"])
def occupancy():
    return ok(svc.get_occupancy_report())


@app.route("/api/logs", methods=["GET"])
def get_logs():
    category = request.args.get("category")
    limit = request.args.get("limit", 100, type=int)
    logs = svc.get_activity_logs(limit=limit, category=category)
    return ok(logs)


@app.route("/api/payments", methods=["GET"])
def get_payments():
    reservation_id = request.args.get("reservation_id", type=int)
    rows = svc.list_payments(reservation_id=reservation_id)
    return ok(rows)


if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  Otel API Sunucusu baslatildi")
    print("  http://0.0.0.0:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False)
