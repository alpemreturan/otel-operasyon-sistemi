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

| Üye | Sorumluluk |
|---|---|
| Beril - Deniz | Gereksinim Analizi |
| Zeynep | Veri Tabanı Tasarımı |
| Tuğba | UML Diyagramları |
| Umut | Arayüz Tasarımı |

---

# 🧪 Gelecekteki Geliştirmeler

- Gerçek ödeme sistemi entegrasyonu
- Bildirim sistemi
- Online rezervasyon desteği
- Çoklu dil desteği
- Yapay zekâ destekli operasyon yönetimi
- Cloud deployment desteği

---

# 📄 Dokümantasyon

Bu proje kapsamında detaylı olarak:

- Fonksiyonel Gereksinimler
- Fonksiyonel Olmayan Gereksinimler
- İş Kuralları
- Veri Tabanı Tasarımı
- UML Diyagramları
- Wireframe Tasarımları
- Proje Planlaması

dokümante edilmiştir.

---
.
