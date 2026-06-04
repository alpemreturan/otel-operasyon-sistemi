# 🏨 Otel Operasyon Sistemi

Otel operasyonlarını dijitalleştirmek ve yönetim süreçlerini daha verimli hale getirmek amacıyla geliştirilmiş, rol tabanlı ve mobil uyumlu modern otel yönetim sistemi.

---

# 📌 Proje Hakkında

Otel Operasyon Sistemi; otel içerisindeki rezervasyon, konaklama, oda yönetimi, hizmet talepleri ve personel süreçlerini merkezi bir yapı üzerinden yönetmek için geliştirilmiştir.

Sistem aşağıdaki kullanıcı rollerini desteklemektedir:

- 👤 Müşteri
- 🧑‍💼 Resepsiyonist
- 🧹 Kat Görevlisi
- 🧑‍💻 Otel Müdürü

Bu yapı sayesinde tüm operasyon süreçleri dijital, güvenli ve daha verimli bir şekilde yönetilebilmektedir.

---

# ✨ Özellikler

## 👤 Müşteri Özellikleri

- Konaklama bilgilerini görüntüleme
- QR kod ile oda erişimi
- Temizlik ve oda servisi talebi oluşturma
- Hizmet taleplerinin durumunu takip etme

---

## 🧑‍💼 Resepsiyonist Özellikleri

- Yeni müşteri kaydı oluşturma
- Rezervasyon yönetimi
- Check-in / Check-out işlemleri
- Oda atama işlemleri
- Müsait oda görüntüleme
- Aktif konaklama yönetimi

---

## 🧹 Kat Görevlisi Özellikleri

- Atanan görevleri görüntüleme
- Hizmet taleplerini yönetme
- Görev durumunu güncelleme
- Tamamlanan işlemleri sisteme kaydetme

---

## 🧑‍💻 Yönetici Özellikleri

- Yönetim paneli (Dashboard)
- Doluluk oranı takibi
- Personel yönetimi
- Aktif müşteri ve oda durumlarını görüntüleme
- Hizmet taleplerini takip etme

---

# 🔐 Güvenlik Özellikleri

- Rol tabanlı yetkilendirme sistemi
- Güvenli giriş sistemi
- Şifre hashleme
- QR erişim doğrulama
- Yetkisiz işlem engelleme
- Güvenli veri saklama
- İşlem kayıtları ve log sistemi

---

# 📱 Mobil Uyumluluk

Sistem aşağıdaki platformlar için tasarlanmıştır:

- 📱 Android
- 🍎 iOS
- 📲 Tablet cihazlar

Mobil uyumlu arayüz yapısı sayesinde farklı cihazlarda sorunsuz kullanım hedeflenmiştir.

---

# 🧩 Temel Modüller

## 🛏️ Rezervasyon & Konaklama Modülü

- Rezervasyon oluşturma
- Check-in / Check-out yönetimi
- Oda atama sistemi
- Müsaitlik kontrolü
- Konaklama süreci takibi

---

## 🚪 QR Erişim Modülü

- Süreli QR erişim sistemi
- Güvenli oda giriş işlemleri
- Check-out sonrası QR iptali
- QR işlem kayıtları

---

## 🧹 Hizmet Talebi Modülü

- Temizlik talebi oluşturma
- Oda servisi talebi oluşturma
- Personel görev atamaları
- Durum takibi:
  - Bekliyor
  - Devam Ediyor
  - Tamamlandı

---

## 💳 Ödeme Modülü

> Ödeme sistemi simülasyon mantığında çalışmaktadır.

- Ödeme kayıt yönetimi
- İşlem takibi
- İade kayıtları
- Güvenli ödeme bilgisi saklama

---

## 📊 Yönetim Paneli

- Doluluk oranı analizi
- Aktif müşteri takibi
- Oda durum görüntüleme
- Personel operasyon yönetimi
- Hizmet taleplerini izleme

---

# 🗄️ Veri Tabanı Tasarımı

Proje; sürdürülebilir, genişletilebilir ve ilişkisel veri tabanı mimarisi kullanılarak tasarlanmıştır.

## Temel Varlıklar

- users
- userRoles
- rooms
- roomTypes
- roomStatus
- reservations
- reservationDetails
- roomServices
- qrLogs
- payments
- refunds
- staffAssignments
- activityLogs

---

# 📐 UML & Sistem Tasarımı

Proje dokümantasyonu içerisinde:

- ✅ Use Case Diyagramları
- ✅ Sınıf Diyagramları
- ✅ Aktivite Diyagramları
- ✅ ER Diyagramı
- ✅ Wireframe Tasarımları

yer almaktadır.

---

# 🧠 İş Kuralları

- Müşteri doğrudan oda seçemez
- Aynı oda aynı tarihlerde birden fazla müşteriye atanamaz
- Check-in ve Check-out işlemleri yalnızca resepsiyonist tarafından yapılabilir
- Check-out sonrası QR erişim iptal edilir
- Hizmet talepleri yalnızca aktif konaklama süresince oluşturulabilir

---

# ⚙️ Fonksiyonel Olmayan Gereksinimler

## 🚀 Performans

- Hızlı işlem yanıt süreleri
- Optimize edilmiş veri tabanı sorguları
- Çoklu kullanıcı desteği

## 🔒 Güvenilirlik

- Veri tutarlılığı
- Hata önleme mekanizmaları
- Güvenli işlem yönetimi

## 🎨 Kullanılabilirlik

- Basit ve kullanıcı dostu arayüz
- Rol bazlı ekranlar
- Mobil odaklı kullanım deneyimi

## 🛠️ Sürdürülebilirlik

- Modüler mimari
- Kolay bakım yapılabilir yapı
- Genişletilebilir sistem tasarımı

---

# 📋 Proje Planlaması

## Geliştirme Süreci

| Aşama | Açıklama |
|---|---|
| Analiz | Gereksinim analizi |
| Tasarım | Veri tabanı, UML ve arayüz tasarımı |
| Geliştirme | Sistem modüllerinin kodlanması |
| Test | Sistem test süreçleri |
| Teslim | Final proje teslimi |

---

# 👥 Ekip Üyeleri

| Üye |
|---|
| EMRE TURAN |
| ONUR KOCA |
| BERAT HATİNOĞLU |
| AHMET TALHA TÜRKAN |
| YİĞİT EFE DEMİRCİOĞLU |

---

# 🧪 Gelecekteki Geliştirmeler

- Gerçek ödeme sistemi entegrasyonu
- Bildirim sistemi
- Online rezervasyon desteği
- Çoklu dil desteği
- Yapay zekâ destekli operasyon yönetimi
- Cloud deployment desteği

---

## 🛠️ Kullanılan Teknolojiler

Projenin hem masaüstü, hem konsol hem de web tabanlı arayüzlerini destekleyen esnek ve katmanlı mimarisi için aşağıdaki teknolojiler, kütüphaneler ve protokoller kullanılmıştır:

* **Temel Programlama Dilleri:** Python 3.x ve JavaScript (ES6+).
* **Masaüstü Arayüzü (GUI):** `CustomTkinter` (Gelişmiş Python Tkinter kütüphanesi kullanılarak, modern ve işletim sistemi temasına otomatik uyum sağlayan pencereli bir arayüz geliştirilmiştir).
* **Web Backend & REST API:** `Flask` mikro çerçevesi (microframework) kullanılarak tüm arayüzlerin ortak tüketebileceği servis uç noktaları (endpoints) yazılmıştır. Tarayıcı tabanlı erişim güvenliği için `Flask-CORS` entegrasyonu sağlanmıştır.
* **Web Frontend:** Mobil öncelikli (responsive) tasarıma sahip `HTML5`, `CSS3` ve API servisleriyle asenkron haberleşmeyi sağlayan modern `JavaScript`.
* **Veri Tabanı Mimarisi:** `SQLite3` (İlişkisel Veri Modeli). Hafif, taşınabilir ve gömülü yapısı tercih edilmiş; veri bütünlüğü yabancı anahtarlar (Foreign Keys) ve kısıtlamalarla optimize edilmiştir.
* **Güvenlik Katmanı:** Kullanıcı şifreleri veri tabanında açık metin olarak değil, tek yönlü kriptografik `SHA-256` hashleme teknolojisiyle maskelenerek saklanmaktadır. Rol Tabanlı Yetkilendirme (RBAC) mekanizması entegre edilmiştir.

---

## 💾 Kurulum Adımları

Sistemi yerel geliştirme ortamınızda sorunsuz bir şekilde kurmak ve bağımlılıkları hazırlamak için aşağıdaki adımları sırasıyla uygulayınız:

1. **Projeyi Klonlayın:**
   Öncelikle projeyi GitHub üzerinden bilgisayarınıza indirin ve ilgili proje dizinine geçiş yapın:
```bash
   git clone [https://github.com/kullanici_adi/otel_operations.git](https://github.com/kullanici_adi/otel_operations.git)
   cd otel_operations/otel_sistemi
```
2. **Gerekli Bağımlılıkları / Kütüphaneleri Yükleyin:**
   Sistemde kullanılan harici Python kütüphanelerini paket yöneticisi (pip) aracılığıyla terminalinizde yükleyin:
```bash
   pip install flask flask-cors customtkinter
```
3. **Veri Tabanının Hazırlanması:**
   Herhangi bir SQL scripti çalıştırmanıza gerek yoktur. Sistem ilk kez başlatıldığında database.py modülü otomatik olarak devreye girerek ana dizinde otel.db SQLite dosyasını oluşturur; şemaları hazırlar ve     test süreçleri için gerekli olan lookup tablolarını (roller, odalar, örnek kullanıcılar) içerisine enjekte (seed) eder.
   
---

## 🚀 Çalıştırma Adımları

Proje yapısı gereği tek bir veri tabanı ve iş mantığı çekirdeğini (services.py) paylaşan üç farklı arayüz sunmaktadır. İhtiyacınıza göre ilgili komutu ana dizindeyken terminalinizde yürütmeniz yeterlidir:

**1. Seçenek: Konsol Arayüzünü (CLI) Başlatma**

Metin tabanlı, hafif ve hızlı çalışan tüm rol menülerini (Yönetici, Resepsiyon, Kat Görevlisi, Müşteri) terminal üzerinden test etmek için:
```bash
   python main.py
```

**2. Seçenek: Masaüstü Yönetim Panelini (GUI) Başlatma**

Yönetici raporlama ekranları, resepsiyonist oda atama pencereleri ve kat görevlisi panellerini içeren CustomTkinter tabanlı gelişmiş masaüstü uygulamasını çalıştırmak için:
```bash
   python gui.py
```

**3. Seçenek: Flask REST API Sunucusunu ve Web Arayüzünü Başlatma(Tavsiye Edilen)**

Müşterilerin oda kapısı açma, süreli QR kod üretme ve dijital oda servisi/temizlik talebi gönderme süreçlerini içeren mobil uyumlu web platformunu ayağa kaldırmak için:
```bash
   python api_server.py
```
Sunucu başarıyla başladıktan sonra herhangi bir modern web tarayıcısından http://127.0.0.1:5000/ adresine giderek arayüze erişebilirsiniz.

---

## 📂 Klasör Yapısı

Projenin temiz kod (clean code) prensiplerine uygun, sorumlulukların ayrılması (Separation of Concerns) ilkesini gözeten dizin hiyerarşisi aşağıdaki gibidir:

```text
otel_operations/
└── otel_sistemi/
    ├── database.py         # SQLite3 bağlantı yönetimi, tablo şemaları ve seed verileri
    ├── services.py         # Çekirdek iş mantığı, CRUD fonksiyonları, şifre hashleme ve loglama
    ├── main.py             # Konsol tabanlı (CLI) rol menüleri ve terminal simülasyonu
    ├── gui.py              # CustomTkinter ile kodlanmış pencereli masaüstü uygulaması
    ├── api_server.py       # Flask REST API uç noktaları (Endpoints) ve web sunucu yönetimi
    ├── otel.db             # Uygulama çalıştığında otomatik oluşan ilişkisel SQLite veri tabanı dosyası
    ├── static/             # Web frontend platformuna ait statik varlıklar (Assets)
    │   ├── app.js          # REST API ile asenkron (Fetch) haberleşen istemci kontrol kodları
    │   └── style.css       # Mobil ve tablet cihazlarla uyumlu responsive arayüz stil dosyası
    └── templates/          # Flask mimarisine uygun HTML şablonları
        └── index.html      # Müşteri işlemlerini ve web giriş ekranını barındıran ana sayfa
