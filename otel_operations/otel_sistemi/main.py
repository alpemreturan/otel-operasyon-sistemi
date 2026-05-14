"""
Otel Operasyon Sistemi - Konsol Arayüzü (CLI)
Rol bazlı menü sistemi.
"""
import os
import sys
from datetime import date

# Windows konsolunda UTF-8 çıktısı sağla
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')

from database import init_db
import services as svc

# ── Renk Kodları (ANSI) ───────────────────────────────────────────────────────
CLR = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "blue":   "\033[94m",
    "magenta":"\033[95m",
    "white":  "\033[97m",
    "dim":    "\033[2m",
}

def c(color, text):
    return f"{CLR.get(color,'')}{text}{CLR['reset']}"

# ── Genel Yardımcılar ─────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header(title):
    print("\n" + c("cyan", "=" * 60))
    print(c("bold", c("cyan", f"  ** {title} **")))
    print(c("cyan", "=" * 60))

def prompt(msg, default=""):
    val = input(c("yellow", f"  {msg}: ")).strip()
    return val if val else default

def confirm(msg):
    return prompt(f"{msg} (e/h)").lower() == "e"

def success(msg):
    print(c("green", f"\n  [OK]  {msg}"))

def error(msg):
    print(c("red", f"\n  [!!]  {msg}"))

def info(msg):
    print(c("dim", f"  ·  {msg}"))

def pause():
    input(c("dim", "\n  [Enter'a basın...]"))

def print_table(rows, cols):
    """Basit tablo çıktısı."""
    if not rows:
        info("Kayıt bulunamadı.")
        return
    widths = {col: max(len(col), max(len(str(r.get(col, ""))) for r in rows)) for col in cols}
    sep = "  " + "  ".join("─" * widths[col] for col in cols)
    header_row = "  " + "  ".join(c("bold", str(col).ljust(widths[col])) for col in cols)
    print(sep)
    print(header_row)
    print(sep)
    for row in rows:
        line = "  " + "  ".join(str(row.get(col, "")).ljust(widths[col]) for col in cols)
        print(line)
    print(sep)


# ═══════════════════════════════════════════════════════════════════════════════
# Giriş Ekranı
# ═══════════════════════════════════════════════════════════════════════════════

def login_screen():
    clear()
    header("OTEL OPERASYON SİSTEMİ")
    print(c("dim", "\n  Varsayılan hesaplar:"))
    print(c("dim", "  admin@otel.com / admin123       → Yönetici"))
    print(c("dim", "  recep@otel.com / recep123        → Resepsiyonist"))
    print(c("dim", "  kat@otel.com   / kat123          → Kat Görevlisi"))
    print(c("dim", "  musteri@otel.com / musteri123    → Müşteri\n"))

    for _ in range(3):
        email = prompt("E-posta")
        pwd   = prompt("Şifre")
        user  = svc.login(email, pwd)
        if user:
            success(f"Hoş geldiniz, {user['name']} {user['surname']}! ({user['role']})")
            pause()
            return user
        error("E-posta veya şifre hatalı.")
    print(c("red", "\n  Çok fazla hatalı giriş. Program kapatılıyor."))
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# YÖNETİCİ MENÜSÜ
# ═══════════════════════════════════════════════════════════════════════════════

def manager_menu(user):
    while True:
        clear()
        header(f"YÖNETİCİ PANELİ  —  {user['name']} {user['surname']}")
        print(c("white", """
  1. Doluluk Raporu
  2. Tüm Rezervasyonları Görüntüle
  3. Tüm Odaları Görüntüle
  4. Bekleyen Hizmet Talepleri
  5. Personel Listesi
  6. Yeni Personel Ekle
  7. Personel Aktif / Pasif Yap
  8. Hizmet Talebini Personele Ata
  9. Aktivite Logları
  0. Çıkış
"""))
        ch = prompt("Seçim")
        if ch == "1":   _manager_occupancy()
        elif ch == "2": _manager_reservations()
        elif ch == "3": _manager_rooms()
        elif ch == "4": _manager_pending_services()
        elif ch == "5": _manager_staff_list()
        elif ch == "6": _create_user(user)
        elif ch == "7": _toggle_user(user)
        elif ch == "8": _assign_service(user)
        elif ch == "9": _activity_logs()
        elif ch == "0": break


def _manager_occupancy():
    clear()
    header("DOLULUK RAPORU")
    r = svc.get_occupancy_report()
    print(f"""
  Toplam Oda    : {c('bold', str(r['total']))}
  Dolu          : {c('red', str(r['occupied']))}
  Müsait        : {c('green', str(r['available']))}
  Temizlikte    : {c('yellow', str(r['cleaning']))}
  Doluluk Oranı : {c('cyan', f"%{r['occupancy_rate']}")}
""")
    pause()


def _manager_reservations():
    clear()
    header("TÜM REZERVASYONLAR")
    rows = svc.list_reservations()
    print_table(rows, ["id", "customer_name", "room_number", "check_in_date",
                       "check_out_date", "status"])
    pause()


def _manager_rooms():
    clear()
    header("TÜM ODALAR")
    rows = svc.list_rooms()
    print_table(rows, ["room_number", "floor", "type_name", "base_price",
                       "capacity", "status_name"])
    pause()


def _manager_pending_services():
    clear()
    header("BEKLEYİP DEVAM EDEN HİZMET TALEPLERİ")
    rows = svc.list_service_requests(status="pending")
    rows += svc.list_service_requests(status="in_progress")
    rows.sort(key=lambda r: r["created_at"])
    print_table(rows, ["id", "customer_name", "room_number", "service_type",
                       "status", "staff_name", "created_at"])
    pause()


def _manager_staff_list():
    clear()
    header("PERSONEL LİSTESİ")
    rows = svc.list_users(role_name="housekeeper")
    rows += svc.list_users(role_name="receptionist")
    print_table(rows, ["id", "name", "surname", "email", "role", "is_active"])
    pause()


def _create_user(actor):
    clear()
    header("YENİ KULLANICI EKLE")
    name    = prompt("Ad")
    surname = prompt("Soyad")
    email   = prompt("E-posta")
    pwd     = prompt("Şifre")
    print("  Roller: manager / receptionist / housekeeper / customer")
    role    = prompt("Rol")
    phone   = prompt("Telefon (isteğe bağlı)")
    try:
        uid = svc.create_user(actor["id"], name, surname, email, pwd, role,
                              phone or None)
        success(f"Kullanıcı oluşturuldu. ID: {uid}")
    except Exception as e:
        error(str(e))
    pause()


def _toggle_user(actor):
    clear()
    header("KULLANICI AKTİF/PASİF")
    rows = svc.list_users()
    print_table(rows, ["id", "name", "email", "role", "is_active"])
    uid  = prompt("Kullanıcı ID")
    stat = prompt("Durum (1=aktif, 0=pasif)")
    try:
        svc.set_user_active(actor["id"], int(uid), stat == "1")
        success("Kullanıcı durumu güncellendi.")
    except Exception as e:
        error(str(e))
    pause()


def _assign_service(actor):
    clear()
    header("HİZMET TALEBİ ATAMA")
    pending = svc.list_service_requests(status="pending")
    if not pending:
        info("Bekleyen talep yok.")
        pause(); return
    print_table(pending, ["id", "customer_name", "room_number", "service_type"])
    svc_id = prompt("Talep ID")
    staff  = svc.list_users("housekeeper")
    print_table(staff, ["id", "name", "surname"])
    staff_id = prompt("Personel ID")
    try:
        svc.assign_service_to_staff(actor["id"], int(svc_id), int(staff_id))
        success("Talep personele atandı.")
    except Exception as e:
        error(str(e))
    pause()


def _activity_logs():
    clear()
    header("AKTİVİTE LOGLARI (Son 30)")
    rows = svc.get_activity_logs(30)
    print_table(rows, ["id", "user_name", "action", "entity", "entity_id",
                       "details", "logged_at"])
    pause()


# ═══════════════════════════════════════════════════════════════════════════════
# RESEPSİYONİST MENÜSÜ
# ═══════════════════════════════════════════════════════════════════════════════

def receptionist_menu(user):
    while True:
        clear()
        header(f"RESEPSİYONİST PANELİ  —  {user['name']} {user['surname']}")
        print(c("white", """
  1. Yeni Müşteri Kaydı
  2. Rezervasyon Oluştur
  3. Ödeme Al (Rezervasyon Aktifleştir)
  4. Oda Ata & Check-in Yap
  5. Check-out Yap
  6. Müsait Odaları Görüntüle
  7. Aktif Konaklamalar
  8. Tüm Rezervasyonlar
  0. Çıkış
"""))
        ch = prompt("Seçim")
        if ch == "1":   _recep_add_customer(user)
        elif ch == "2": _recep_create_reservation(user)
        elif ch == "3": _recep_payment(user)
        elif ch == "4": _recep_checkin(user)
        elif ch == "5": _recep_checkout(user)
        elif ch == "6": _recep_available_rooms()
        elif ch == "7": _recep_active_stays()
        elif ch == "8": _manager_reservations()
        elif ch == "0": break


def _recep_add_customer(actor):
    clear()
    header("YENİ MÜŞTERİ KAYDI")
    name    = prompt("Ad")
    surname = prompt("Soyad")
    email   = prompt("E-posta")
    pwd     = prompt("Şifre")
    phone   = prompt("Telefon")
    try:
        uid = svc.create_user(actor["id"], name, surname, email, pwd,
                              "customer", phone or None)
        success(f"Müşteri kaydedildi. ID: {uid}")
    except Exception as e:
        error(str(e))
    pause()


def _recep_create_reservation(actor):
    clear()
    header("YENİ REZERVASYON")
    # Müşteri listesi
    customers = svc.list_users("customer")
    if not customers:
        info("Sistemde müşteri yok. Önce müşteri ekleyin.")
        pause(); return
    print_table(customers, ["id", "name", "surname", "email"])
    cust_id   = prompt("Müşteri ID")
    check_in  = prompt("Giriş Tarihi (YYYY-MM-DD)")
    check_out = prompt("Çıkış Tarihi (YYYY-MM-DD)")
    adults    = prompt("Yetişkin sayısı", "1")
    children  = prompt("Çocuk sayısı",   "0")
    special   = prompt("Özel istek (isteğe bağlı)")
    try:
        res_id = svc.create_reservation(actor["id"], int(cust_id),
                                        check_in, check_out,
                                        int(adults), int(children),
                                        special or None)
        success(f"Rezervasyon oluşturuldu. ID: {res_id} — Ödeme bekleniyor.")
    except Exception as e:
        error(str(e))
    pause()


def _recep_payment(actor):
    clear()
    header("ÖDEME AL")
    rows = svc.list_reservations(status="pending_payment")
    if not rows:
        info("Ödemesi bekleyen rezervasyon yok.")
        pause(); return
    print_table(rows, ["id", "customer_name", "check_in_date", "check_out_date"])
    res_id = prompt("Rezervasyon ID")
    amount = prompt("Tutar (TL)")
    holder = prompt("Kart Sahibi Adı")
    last4  = prompt("Kartın Son 4 Hanesi")
    try:
        tx = svc.process_payment(actor["id"], int(res_id), float(amount),
                                 holder or None, last4 or None)
        success(f"Ödeme alındı. İşlem Kodu: {tx}")
    except Exception as e:
        error(str(e))
    pause()


def _recep_checkin(actor):
    clear()
    header("ODA ATA & CHECK-IN")
    rows = svc.list_reservations(status="active")
    if not rows:
        info("Ödemesi tamamlanmış rezervasyon yok.")
        pause(); return
    print_table(rows, ["id", "customer_name", "check_in_date", "check_out_date"])
    res_id    = prompt("Rezervasyon ID")
    res_info  = next((r for r in rows if r["id"] == int(res_id)), None)
    if not res_info:
        error("Rezervasyon bulunamadı."); pause(); return

    avail = svc.get_available_rooms(res_info["check_in_date"], res_info["check_out_date"])
    if not avail:
        info("Müsait oda bulunamadı."); pause(); return
    print_table(avail, ["id", "room_number", "floor", "type_name", "base_price", "capacity"])
    room_id = prompt("Oda ID")
    try:
        qr = svc.assign_room_and_checkin(actor["id"], int(res_id), int(room_id))
        success(f"Check-in yapıldı! QR Kodu: {qr}")
    except Exception as e:
        error(str(e))
    pause()


def _recep_checkout(actor):
    clear()
    header("CHECK-OUT")
    rows = svc.list_reservations(status="checked_in")
    if not rows:
        info("Aktif konaklama yok."); pause(); return
    print_table(rows, ["id", "customer_name", "room_number", "check_in_date", "check_out_date"])
    res_id = prompt("Rezervasyon ID")
    try:
        svc.checkout(actor["id"], int(res_id))
        success("Check-out tamamlandı. Oda temizlemeye alındı.")
    except Exception as e:
        error(str(e))
    pause()


def _recep_available_rooms():
    clear()
    header("MÜSAİT ODALAR")
    check_in  = prompt("Giriş Tarihi (YYYY-MM-DD)", str(date.today()))
    check_out = prompt("Çıkış Tarihi (YYYY-MM-DD)")
    rows = svc.get_available_rooms(check_in, check_out)
    print_table(rows, ["room_number", "floor", "type_name", "base_price", "capacity"])
    pause()


def _recep_active_stays():
    clear()
    header("AKTİF KONAKLAMALAR")
    rows = svc.list_reservations(status="checked_in")
    print_table(rows, ["id", "customer_name", "room_number", "check_in_date",
                       "check_out_date", "status"])
    pause()


# ═══════════════════════════════════════════════════════════════════════════════
# KAT GÖREVLİSİ MENÜSÜ
# ═══════════════════════════════════════════════════════════════════════════════

def housekeeper_menu(user):
    while True:
        clear()
        header(f"KAT GÖREVLİSİ PANELİ  —  {user['name']} {user['surname']}")
        print(c("white", """
  1. Bana Atanan Görevler
  2. Görevi Tamamlandı Olarak İşaretle
  3. Görevi İptal Et
  0. Çıkış
"""))
        ch = prompt("Seçim")
        if ch == "1":   _hk_my_tasks(user)
        elif ch == "2": _hk_complete_task(user)
        elif ch == "3": _hk_cancel_task(user)
        elif ch == "0": break


def _hk_my_tasks(user):
    clear()
    header("GÖREVLERİM")
    rows = svc.list_service_requests(assigned_to=user["id"])
    print_table(rows, ["id", "room_number", "service_type", "description",
                       "status", "created_at"])
    pause()


def _hk_complete_task(user):
    clear()
    header("GÖREVİ TAMAMLA")
    rows = svc.list_service_requests(assigned_to=user["id"], status="in_progress")
    if not rows:
        info("Devam eden görev yok."); pause(); return
    print_table(rows, ["id", "room_number", "service_type", "status"])
    svc_id = prompt("Talep ID")
    try:
        svc.update_service_status(user["id"], int(svc_id), "completed")
        success("Görev tamamlandı olarak işaretlendi.")
    except Exception as e:
        error(str(e))
    pause()


def _hk_cancel_task(user):
    clear()
    header("GÖREVİ İPTAL ET")
    rows = svc.list_service_requests(assigned_to=user["id"])
    rows = [r for r in rows if r["status"] in ("pending", "in_progress")]
    if not rows:
        info("İptal edilecek görev yok."); pause(); return
    print_table(rows, ["id", "room_number", "service_type", "status"])
    svc_id = prompt("Talep ID")
    if confirm("İptal etmek istediğinizden emin misiniz?"):
        try:
            svc.update_service_status(user["id"], int(svc_id), "cancelled")
            success("Görev iptal edildi.")
        except Exception as e:
            error(str(e))
    pause()


# ═══════════════════════════════════════════════════════════════════════════════
# MÜŞTERİ MENÜSÜ
# ═══════════════════════════════════════════════════════════════════════════════

def customer_menu(user):
    while True:
        clear()
        header(f"MÜŞTERİ PANELİ  —  {user['name']} {user['surname']}")
        print(c("white", """
  1. Rezervasyonlarım
  2. QR Erişim Kodum
  3. Hizmet Talebi Oluştur
  4. Hizmet Taleplerim
  0. Çıkış
"""))
        ch = prompt("Seçim")
        if ch == "1":   _cust_reservations(user)
        elif ch == "2": _cust_qr(user)
        elif ch == "3": _cust_create_service(user)
        elif ch == "4": _cust_my_services(user)
        elif ch == "0": break


def _cust_reservations(user):
    clear()
    header("REZERVASYONLARIM")
    rows = svc.list_reservations(customer_id=user["id"])
    print_table(rows, ["id", "room_number", "check_in_date",
                       "check_out_date", "status"])
    pause()


def _cust_qr(user):
    clear()
    header("QR ERİŞİM KODUM")
    rows = svc.list_reservations(customer_id=user["id"], status="checked_in")
    if not rows:
        info("Aktif konaklamanız yok."); pause(); return
    res = rows[0]
    qr  = svc.get_active_qr(res["id"])
    if qr:
        print(f"\n  Oda    : {c('bold', res['room_number'])}")
        print(f"  QR Kod : {c('cyan', qr['qr_code'])}")
        print(f"  Geçerlilik: {qr['valid_from']} → {qr['valid_until']}")
    else:
        info("QR kodunuz bulunamadı.")
    pause()


def _cust_create_service(user):
    clear()
    header("HİZMET TALEBİ OLUŞTUR")
    print("  1. Temizlik (cleaning)")
    print("  2. Oda Servisi (room_service)")
    ch = prompt("Seçim")
    stype = "cleaning" if ch == "1" else "room_service"
    desc  = prompt("Açıklama (isteğe bağlı)")
    try:
        sid = svc.create_service_request(user["id"], stype, desc or None)
        success(f"Hizmet talebiniz oluşturuldu. ID: {sid}")
    except Exception as e:
        error(str(e))
    pause()


def _cust_my_services(user):
    clear()
    header("HİZMET TALEPLERİM")
    # Müşterinin tüm rezervasyonlarındaki talepler
    rows = svc.list_reservations(customer_id=user["id"])
    all_svc = []
    for r in rows:
        all_svc += svc.list_service_requests(reservation_id=r["id"])
    if not all_svc:
        info("Hizmet talebiniz yok.")
    else:
        print_table(all_svc, ["id", "service_type", "description",
                              "status", "staff_name", "created_at"])
    pause()


# ═══════════════════════════════════════════════════════════════════════════════
# ANA DÖNGÜ
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Veritabanını hazırla
    init_db()

    while True:
        user = login_screen()
        role = user["role"]
        if role == "manager":
            manager_menu(user)
        elif role == "receptionist":
            receptionist_menu(user)
        elif role == "housekeeper":
            housekeeper_menu(user)
        elif role == "customer":
            customer_menu(user)
        else:
            error("Bilinmeyen rol.")
            break

        clear()
        header("OTURUM KAPATILDI")
        if not confirm("Yeni oturum acmak ister misiniz?"):
            print(c("cyan", "\n  Gorusuruz!\n"))
            break


if __name__ == "__main__":
    main()
