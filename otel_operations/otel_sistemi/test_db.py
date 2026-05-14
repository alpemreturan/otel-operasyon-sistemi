import sys
sys.path.insert(0, '.')
from database import init_db, get_connection
import services as svc

conn = get_connection()
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tablolar:", [t[0] for t in tables])

users = conn.execute("SELECT name, surname, email FROM users").fetchall()
print("\nKullanicilar:")
for u in users:
    print(f"  {u[0]} {u[1]} - {u[2]}")

rooms = conn.execute("SELECT room_number, floor FROM rooms").fetchall()
print(f"\nOda sayisi: {len(rooms)}")
conn.close()

user = svc.login("admin@otel.com", "admin123")
print("\nLogin test:", user["name"], user["role"])

rep = svc.get_occupancy_report()
print("Doluluk:", rep)
