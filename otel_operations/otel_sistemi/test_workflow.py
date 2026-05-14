"""Tam iş akışı testi: rezervasyon → ödeme → check-in → hizmet → check-out"""
import sys
sys.path.insert(0, '.')
from database import init_db, get_connection
import services as svc

print("=== TAM İŞ AKIŞI TESTİ ===\n")

# Kullanıcıları al
admin   = svc.login("admin@otel.com",    "admin123")
recep   = svc.login("recep@otel.com",    "recep123")
kat_gv  = svc.login("kat@otel.com",      "kat123")
musteri = svc.login("musteri@otel.com",  "musteri123")

print("1. Kullanicilar oturum acti OK")

# Rezervasyon oluştur
res_id = svc.create_reservation(
    actor_id=recep["id"],
    customer_id=musteri["id"],
    check_in="2026-06-01",
    check_out="2026-06-05",
    adult_count=2, child_count=1,
    special_requests="Deniz manzarali oda lutfen"
)
print(f"2. Rezervasyon olusturuldu: ID={res_id}")

# Ödeme al
tx = svc.process_payment(
    actor_id=recep["id"],
    reservation_id=res_id,
    amount=3200.0,
    card_holder_name="Mehmet Kaya",
    card_last_four="4242"
)
print(f"3. Odeme alindi: TX={tx}")

# Müsait odaları listele
avail = svc.get_available_rooms("2026-06-01", "2026-06-05")
print(f"4. Musait oda sayisi: {len(avail)}")

# Oda ata & check-in
room_id = avail[0]["id"]
qr = svc.assign_room_and_checkin(recep["id"], res_id, room_id)
print(f"5. Check-in yapildi. Oda: {avail[0]['room_number']}, QR: {qr[:20]}...")

# Hizmet talebi oluştur
svc_id = svc.create_service_request(musteri["id"], "cleaning", "Odam temizlensin")
print(f"6. Hizmet talebi olusturuldu: ID={svc_id}")

# Personele ata
svc.assign_service_to_staff(admin["id"], svc_id, kat_gv["id"])
print(f"7. Talep kat gorevlisine atandi: {kat_gv['name']}")

# Görevi tamamla
svc.update_service_status(kat_gv["id"], svc_id, "completed")
print("8. Hizmet talebi tamamlandi")

# Check-out
svc.checkout(recep["id"], res_id)
print("9. Check-out yapildi")

# Rapor
rep = svc.get_occupancy_report()
print(f"\n=== DOLULUK RAPORU ===")
print(f"Toplam: {rep['total']} | Dolu: {rep['occupied']} | Musait: {rep['available']} | Temizlik: {rep['cleaning']}")

# Log
logs = svc.get_activity_logs(10)
print(f"\n=== SON LOGLAR ({len(logs)} kayit) ===")
for log in logs:
    print(f"  [{log['logged_at']}] {log['user_name']} -> {log['action']} ({log['entity']}:{log['entity_id']})")

print("\n✓ TUM TESTLER BASARILI!")
