import customtkinter as ctk
from tkinter import messagebox
from datetime import date
import services as svc
from database import init_db

# CustomTkinter ayarları
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Otel Operasyon Sistemi")
        self.geometry("800x600")
        self.current_user = None
        
        init_db()
        self.show_login_screen()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_popup(self, title, geometry="400x500"):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry(geometry)
        win.attributes('-topmost', True) # Popupların arkada kalmasını engeller
        win.grab_set() # Pop-up açıkken ana pencereye tıklamayı engeller
        win.focus_force()
        return win

    # --- GİRİŞ ---
    def show_login_screen(self):
        self.clear_screen()
        frame = ctk.CTkFrame(self, width=400, height=400)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame, text="Otel Girişi", font=("Roboto", 24, "bold")).pack(pady=30)
        
        self.entry_email = ctk.CTkEntry(frame, placeholder_text="E-posta", width=250)
        self.entry_email.pack(pady=10)
        
        self.entry_pwd = ctk.CTkEntry(frame, placeholder_text="Şifre", show="*", width=250)
        self.entry_pwd.pack(pady=10)
        
        ctk.CTkButton(frame, text="Giriş Yap", command=self.login).pack(pady=20)

    def login(self):
        email, pwd = self.entry_email.get(), self.entry_pwd.get()
        user = svc.login(email, pwd)
        
        if user:
            self.current_user = user
            role = user["role"]
            if role == "manager": self.show_manager_dashboard()
            elif role == "receptionist": self.show_receptionist_dashboard()
            elif role == "housekeeper": self.show_housekeeper_dashboard()
            else: messagebox.showerror("Hata", "Müşteriler mobil uygulamayı kullanmalıdır.")
        else:
            messagebox.showerror("Hata", "Hatalı e-posta veya şifre!")

    def logout(self):
        self.current_user = None
        self.show_login_screen()

    # --- ORTAK KISIMLAR ---
    def create_header(self, title):
        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text=f"{title} - Hoş Geldin {self.current_user['name']}", font=("Roboto", 18, "bold")).pack(side="left", padx=20)
        ctk.CTkButton(header, text="Çıkış Yap", command=self.logout, width=100, fg_color="red", hover_color="darkred").pack(side="right", padx=20)

    def show_manager_dashboard(self):
        self.clear_screen()
        self.create_header("Yönetici Paneli")
        f = ctk.CTkFrame(self)
        f.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkButton(f, text="Doluluk Raporu", command=self.m_occupancy).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Tüm Odalar", command=self.m_rooms).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(f, text="Aktif Konaklamalar", command=self.m_active_stays).grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkButton(f, text="Personel Görüntüle", command=self.m_staff).grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Yeni Personel Ekle", command=self.m_add_staff).grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(f, text="Personel Durumu", command=self.m_toggle_staff).grid(row=1, column=2, padx=10, pady=10)
        
        ctk.CTkButton(f, text="Hizmet Talepleri", command=self.m_all_tasks).grid(row=2, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Görev Ata", command=self.m_assign_task).grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkButton(f, text="İşlem Kayıtları (Log)", command=self.m_logs).grid(row=2, column=2, padx=10, pady=10)
        ctk.CTkButton(f, text="Ödeme Geçmişi", command=self.m_payments).grid(row=3, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Oda Durumu Değiştir", command=self.m_room_status).grid(row=3, column=1, padx=10, pady=10)

    def m_occupancy(self):
        rep = svc.get_occupancy_report()
        msg = f"Toplam Oda: {rep['total']}\nDolu: {rep['occupied']}\nMüsait: {rep['available']}\nTemizlikte: {rep['cleaning']}\nDoluluk Oranı: %{rep['occupancy_rate']}"
        messagebox.showinfo("Rapor", msg)

    def m_rooms(self):
        self.show_list_popup("Odalar", [f"Oda {r['room_number']} - Kat {r['floor']} - {r['type_name']} - {r['status_name']}" for r in svc.list_rooms()])

    def m_staff(self):
        staff = svc.list_users("housekeeper") + svc.list_users("receptionist")
        self.show_list_popup("Personel", [f"ID:{s['id']} | {s['name']} {s['surname']} ({s['role']}) - Aktif:{s['is_active']}" for s in staff])

    def m_active_stays(self):
        r = svc.list_reservations(status="checked_in")
        self.show_list_popup("Aktif Konaklamalar", [f"ID:{x['id']} | Oda:{x['room_number']} - {x['customer_name']} (Çıkış:{x['check_out_date']})" for x in r])

    def m_all_tasks(self):
        tasks = svc.list_service_requests()
        self.show_list_popup("Hizmet Talepleri", [f"ID:{t['id']} | Oda:{t['room_number']} | {t['service_type']} | D:{t['status']} | KatG:{t['staff_name'] or 'Yok'}" for t in tasks])

    def m_logs(self):
        w = self.create_popup("İşlem Kayıtları", "600x500")
        categories = {
            "Tümü": None,
            "Giriş/Çıkış": "auth",
            "Rezervasyon": "reservation",
            "Check-in/out": "checkin_checkout",
            "Hizmet": "service",
            "Oda": "room",
            "Kullanıcı": "user",
        }
        sf = ctk.CTkScrollableFrame(w, width=550, height=350)
        sf.pack(pady=5, padx=10, fill="both", expand=True)

        def load_logs(cat):
            for widget in sf.winfo_children():
                widget.destroy()
            logs = svc.get_activity_logs(limit=100, category=cat)
            if not logs:
                ctk.CTkLabel(sf, text="Kayıt yok.").pack()
                return
            for l in logs:
                ctk.CTkLabel(sf, text=f"[{l['logged_at'][:16]}] {l['user_name']} → {l['action']} ({l['entity']} ID:{l['entity_id']})", anchor="w", justify="left").pack(fill="x", pady=1)

        btn_frame = ctk.CTkFrame(w)
        btn_frame.pack(pady=5, padx=10, fill="x")
        for label, cat in categories.items():
            ctk.CTkButton(btn_frame, text=label, width=75, height=28, command=lambda c=cat: load_logs(c)).pack(side="left", padx=2)

        load_logs(None)

    def m_payments(self):
        pmts = svc.list_payments()
        self.show_list_popup("Ödeme Geçmişi", [f"[{p['paid_at'][:10]}] {p['customer_name']} | {p['amount']} TL | Kod:{p['transaction_code'][:10]}... | Kart:{p['card_holder_name']} ...{p['card_last_four'] or '????'}" for p in pmts])

    def m_room_status(self):
        w = self.create_popup("Oda Durumu Değiştir", "400x300")
        rooms = svc.list_rooms()
        r_vals = [f"{r['id']} - Oda {r['room_number']} (Mevcut: {r['status_name']})" for r in rooms]
        rv = ctk.StringVar(value=r_vals[0])
        ctk.CTkLabel(w, text="Oda Seç:").pack(pady=5)
        ctk.CTkOptionMenu(w, variable=rv, values=r_vals).pack(pady=5)
        statuses = ["available", "occupied", "cleaning", "maintenance"]
        sv = ctk.StringVar(value=statuses[0])
        ctk.CTkLabel(w, text="Yeni Durum:").pack(pady=5)
        ctk.CTkOptionMenu(w, variable=sv, values=statuses).pack(pady=5)
        def save():
            rid = int(rv.get().split(" - ")[0])
            try:
                svc.set_room_status(self.current_user['id'], rid, sv.get())
                messagebox.showinfo("Başarılı", "Oda durumu güncellendi.")
                w.destroy()
            except Exception as e: messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Güncelle", command=save).pack(pady=20)

    def m_add_staff(self):
        w = self.create_popup("Personel Ekle")
        e_name = ctk.CTkEntry(w, placeholder_text="Ad")
        e_name.pack(pady=5)
        e_sur = ctk.CTkEntry(w, placeholder_text="Soyad")
        e_sur.pack(pady=5)
        e_email = ctk.CTkEntry(w, placeholder_text="E-posta")
        e_email.pack(pady=5)
        e_pwd = ctk.CTkEntry(w, placeholder_text="Şifre")
        e_pwd.pack(pady=5)
        
        roles = ["receptionist", "housekeeper", "manager"]
        role_var = ctk.StringVar(value=roles[0])
        ctk.CTkOptionMenu(w, variable=role_var, values=roles).pack(pady=5)
        
        def save():
            try:
                svc.create_user(self.current_user['id'], e_name.get(), e_sur.get(), e_email.get(), e_pwd.get(), role_var.get())
                messagebox.showinfo("Başarılı", "Personel eklendi.")
                w.destroy()
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Kaydet", command=save).pack(pady=20)

    def m_toggle_staff(self):
        w = self.create_popup("Durum Değiştir", "400x300")
        staff = svc.list_users("housekeeper") + svc.list_users("receptionist") + svc.list_users("customer")
        vals = [f"{s['id']} - {s['name']} {s['surname']} ({s['role']}) (Aktif: {s['is_active']})" for s in staff]
        if not vals:
            ctk.CTkLabel(w, text="Personel yok").pack(pady=10); return
            
        sv = ctk.StringVar(value=vals[0])
        ctk.CTkOptionMenu(w, variable=sv, values=vals).pack(pady=10)
        
        def toggle(make_active):
            sid = int(sv.get().split(" - ")[0])
            svc.set_user_active(self.current_user['id'], sid, make_active)
            messagebox.showinfo("Başarılı", "Durum güncellendi.")
            w.destroy()
            
        ctk.CTkButton(w, text="Aktif Yap", command=lambda: toggle(True)).pack(pady=5)
        ctk.CTkButton(w, text="Pasif Yap", command=lambda: toggle(False)).pack(pady=5)

    def m_assign_task(self):
        w = self.create_popup("Görev Ata")
        pending = svc.list_service_requests(status="pending")
        if not pending: ctk.CTkLabel(w, text="Bekleyen görev yok.").pack(pady=10); return
        
        p_vals = [f"{p['id']} - Oda:{p['room_number']} ({p['service_type']})" for p in pending]
        p_var = ctk.StringVar(value=p_vals[0])
        ctk.CTkLabel(w, text="Görev Seç:").pack()
        ctk.CTkOptionMenu(w, variable=p_var, values=p_vals).pack(pady=10)
        
        staff = svc.list_users("housekeeper")
        s_vals = [f"{s['id']} - {s['name']} {s['surname']}" for s in staff]
        if not s_vals: ctk.CTkLabel(w, text="Kat görevlisi yok.").pack(pady=10); return
        s_var = ctk.StringVar(value=s_vals[0])
        ctk.CTkLabel(w, text="Personel Seç:").pack()
        ctk.CTkOptionMenu(w, variable=s_var, values=s_vals).pack(pady=10)

        def save():
            tid = int(p_var.get().split(" - ")[0])
            sid = int(s_var.get().split(" - ")[0])
            try:
                svc.assign_service_to_staff(self.current_user['id'], tid, sid)
                messagebox.showinfo("Başarılı", "Atandı.")
                w.destroy()
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Ata", command=save).pack(pady=20)


    # --- RESEPSİYONİST EKRANI ---
    def show_receptionist_dashboard(self):
        self.clear_screen()
        self.create_header("Resepsiyon Paneli")
        f = ctk.CTkFrame(self)
        f.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkButton(f, text="Müsait Odalar", command=self.r_avail).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Aktif Konaklamalar", command=self.r_active).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(f, text="Yeni Müşteri Ekle", command=self.r_add_cust).grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkButton(f, text="Rezervasyon Yap", command=self.r_add_res).grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Ödeme Al", command=self.r_pay).grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(f, text="Oda Ata & Check-in", command=self.r_checkin).grid(row=1, column=2, padx=10, pady=10)
        
        ctk.CTkButton(f, text="Check-out Yap", command=self.r_checkout, fg_color="red").grid(row=2, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Tüm Rezervasyonlar", command=self.r_all_res).grid(row=2, column=1, padx=10, pady=10)

    def r_avail(self):
        t = str(date.today())
        r = svc.get_available_rooms(t, t)
        self.show_list_popup("Müsait Odalar", [f"Oda {x['room_number']} - {x['type_name']}" for x in r])

    def r_active(self):
        r = svc.list_reservations(status="checked_in")
        self.show_list_popup("Aktif Konaklamalar", [f"ID:{x['id']} | Oda:{x['room_number']} - {x['customer_name']} (Çıkış:{x['check_out_date']})" for x in r])

    def r_all_res(self):
        r = svc.list_reservations()
        self.show_list_popup("Tüm Rezervasyonlar", [f"ID:{x['id']} | {x['customer_name']} | {x['status']} | Giriş:{x['check_in_date']} Çıkış:{x['check_out_date']}" for x in r])

    def r_add_cust(self):
        w = self.create_popup("Yeni Müşteri Ekle")
        entries = [ctk.CTkEntry(w, placeholder_text=p) for p in ["Ad", "Soyad", "E-posta", "Şifre", "Telefon"]]
        for e in entries: e.pack(pady=5)
        
        def save():
            try:
                svc.create_user(self.current_user['id'], entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get(), "customer", entries[4].get())
                messagebox.showinfo("Başarılı", "Müşteri kaydedildi.")
                w.destroy()
            except Exception as e: messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Kaydet", command=save).pack(pady=20)

    def r_add_res(self):
        w = self.create_popup("Rezervasyon Yap", "400x500")
        cust = svc.list_users("customer")
        if not cust: ctk.CTkLabel(w, text="Müşteri yok.").pack(pady=10); return
        
        cv = ctk.StringVar(value=f"{cust[0]['id']} - {cust[0]['name']}")
        ctk.CTkOptionMenu(w, variable=cv, values=[f"{c['id']} - {c['name']} {c['surname']}" for c in cust]).pack(pady=10)
        
        t = str(date.today())
        ei = ctk.CTkEntry(w, placeholder_text="Giriş (YYYY-AA-GG)")
        ei.insert(0, t); ei.pack(pady=5)
        
        eo = ctk.CTkEntry(w, placeholder_text="Çıkış (YYYY-AA-GG)")
        eo.pack(pady=5)
        
        ea = ctk.CTkEntry(w, placeholder_text="Yetişkin Sayısı")
        ea.insert(0, "1"); ea.pack(pady=5)
        
        def save():
            cid = int(cv.get().split(" - ")[0])
            try:
                res_id = svc.create_reservation(self.current_user['id'], cid, ei.get(), eo.get(), int(ea.get()))
                messagebox.showinfo("Başarılı", f"Oluşturuldu. ID: {res_id}")
                w.destroy()
            except Exception as e: messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Oluştur", command=save).pack(pady=20)

    def r_pay(self):
        w = self.create_popup("Ödeme Al", "400x400")
        p = svc.list_reservations(status="pending_payment")
        if not p: ctk.CTkLabel(w, text="Bekleyen ödeme yok.").pack(); return
        
        rv = ctk.StringVar(value=f"{p[0]['id']} - {p[0]['customer_name']}")
        ctk.CTkOptionMenu(w, variable=rv, values=[f"{x['id']} - {x['customer_name']}" for x in p]).pack(pady=10)
        
        def on_res_change(*args):
            rid = int(rv.get().split(" - ")[0])
            amount = svc.calculate_reservation_amount(rid)
            e_am.delete(0, "end")
            if amount: e_am.insert(0, str(amount))

        rv.trace_add("write", on_res_change)

        e_am = ctk.CTkEntry(w, placeholder_text="Tutar (TL - Otomatik Hesaplanır)")
        e_am.pack(pady=5)
        e_name = ctk.CTkEntry(w, placeholder_text="Kart Üzerindeki İsim")
        e_name.pack(pady=5)
        e_last4 = ctk.CTkEntry(w, placeholder_text="Kartın Son 4 Hanesi")
        e_last4.pack(pady=5)

        on_res_change()

        def save():
            rid = int(rv.get().split(" - ")[0])
            last4 = e_last4.get().strip()
            if len(last4) != 4 or not last4.isdigit():
                messagebox.showerror("Hata", "Kart son 4 hane 4 rakam olmalıdır."); return
            try:
                tx = svc.process_payment(self.current_user['id'], rid, float(e_am.get()), e_name.get(), last4)
                messagebox.showinfo("Başarılı", f"Ödendi! Kod: {tx}")
                w.destroy()
            except Exception as e: messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Öde", command=save).pack(pady=20)

    def r_checkin(self):
        w = self.create_popup("Check-in Yap", "400x400")
        p = svc.list_reservations(status="active")
        if not p: ctk.CTkLabel(w, text="Ödenmiş rezervasyon yok.").pack(); return
        
        rv = ctk.StringVar(value=f"{p[0]['id']} - {p[0]['customer_name']}")
        ctk.CTkOptionMenu(w, variable=rv, values=[f"{x['id']} - {x['customer_name']}" for x in p]).pack(pady=10)
        
        room_var = ctk.StringVar(value="Oda Listesini Getir")
        room_menu = ctk.CTkOptionMenu(w, variable=room_var, values=["Oda Listesini Getir"])
        room_menu.pack(pady=10)
        
        def load_r(*args):
            rid = int(rv.get().split(" - ")[0])
            res = next(x for x in p if x["id"] == rid)
            avail = svc.get_available_rooms(res["check_in_date"], res["check_out_date"])
            if avail:
                v = [f"{a['id']} - Oda {a['room_number']}" for a in avail]
                room_menu.configure(values=v)
                room_var.set(v[0])
            else:
                room_menu.configure(values=["Oda yok"])
                room_var.set("Oda yok")
        
        rv.trace_add("write", load_r)
        load_r()

        def save():
            try:
                rid = int(rv.get().split(" - ")[0])
                rmid = int(room_var.get().split(" - ")[0])
                qr = svc.assign_room_and_checkin(self.current_user['id'], rid, rmid)
                messagebox.showinfo("Başarılı", f"Check-in yapıldı. QR: {qr[:15]}...")
                w.destroy()
            except Exception as e: messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Check-in", command=save).pack(pady=20)

    def r_checkout(self):
        w = self.create_popup("Check-out Yap", "400x300")
        p = svc.list_reservations(status="checked_in")
        if not p: ctk.CTkLabel(w, text="Aktif oda yok.").pack(); return
        
        rv = ctk.StringVar(value=f"{p[0]['id']} - Oda:{p[0]['room_number']} ({p[0]['customer_name']})")
        ctk.CTkOptionMenu(w, variable=rv, values=[f"{x['id']} - Oda:{x['room_number']} ({x['customer_name']})" for x in p]).pack(pady=10)
        
        def save():
            try:
                rid = int(rv.get().split(" - ")[0])
                svc.checkout(self.current_user['id'], rid)
                messagebox.showinfo("Başarılı", "Çıkış yapıldı.")
                w.destroy()
            except Exception as e: messagebox.showerror("Hata", str(e))
        ctk.CTkButton(w, text="Check-out", command=save, fg_color="red").pack(pady=20)


    # --- KAT GÖREVLİSİ EKRANI ---
    def show_housekeeper_dashboard(self):
        self.clear_screen()
        self.create_header("Kat Görevlisi Paneli")
        f = ctk.CTkFrame(self)
        f.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkButton(f, text="Görevlerim", command=self.h_tasks).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(f, text="Görev Durumunu Değiştir", command=self.h_change).grid(row=0, column=1, padx=10, pady=10)

    def h_tasks(self):
        tasks = svc.list_service_requests(assigned_to=self.current_user["id"])
        self.show_list_popup("Görevlerim", [f"ID:{t['id']} | Oda:{t['room_number']} | {t['service_type']} | Durum:{t['status']}" for t in tasks])

    def h_change(self):
        w = self.create_popup("Görev Durumu Değiştir", "400x300")
        t = [x for x in svc.list_service_requests(assigned_to=self.current_user["id"]) if x['status'] in ('pending', 'in_progress')]
        if not t: ctk.CTkLabel(w, text="Aktif görev yok.").pack(); return
        
        tv = ctk.StringVar(value=f"{t[0]['id']} - Oda:{t[0]['room_number']}")
        ctk.CTkOptionMenu(w, variable=tv, values=[f"{x['id']} - Oda:{x['room_number']}" for x in t]).pack(pady=10)
        
        def save(status):
            tid = int(tv.get().split(" - ")[0])
            try:
                svc.update_service_status(self.current_user['id'], tid, status)
                messagebox.showinfo("Başarılı", "Durum güncellendi.")
                w.destroy()
            except Exception as e: messagebox.showerror("Hata", str(e))
            
        ctk.CTkButton(w, text="Başladım (Devam Ediyor)", command=lambda: save('in_progress'), fg_color="#e67e22").pack(pady=5)
        ctk.CTkButton(w, text="Tamamlandı İşaretle", command=lambda: save('completed'), fg_color="green").pack(pady=5)
        ctk.CTkButton(w, text="İptal Et", command=lambda: save('cancelled'), fg_color="red").pack(pady=5)


    def show_list_popup(self, title, items):
        w = self.create_popup(title, "500x400")
        sf = ctk.CTkScrollableFrame(w, width=450, height=350)
        sf.pack(pady=20, padx=20, fill="both", expand=True)
        if not items: ctk.CTkLabel(sf, text="Kayıt yok.").pack(); return
        for i in items: ctk.CTkLabel(sf, text=i, anchor="w", justify="left").pack(fill="x", pady=2)


if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()
