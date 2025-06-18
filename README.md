# Araç Kiralama Takip Sistemi Rapor

## Öğrenci Bilgileri
- **Ad:** Lütfullah
- **Soyad:** Kaya
- **Sınıf:** Bilgisayar Programcılığı 2. Sınıf
- **Ders:** İnternet Programcılığı Final Ödevi
- **GitHub:** https://github.com/ltf2323361/int-prog/

## Proje Özeti
Bu proje, modern web teknolojileri kullanılarak geliştirilmiş kapsamlı bir araç kiralama yönetim sistemidir. Sistem, kullanıcı dostu bir arayüz ile araç kiralama işlemlerini kolaylaştırmayı hedeflemektedir.

## Kullanılan Teknolojiler

### Backend
- **Flask Framework:** Web uygulaması için ana framework
- **SQLAlchemy:** Veritabanı işlemleri için ORM
- **Flask-Login:** Kullanıcı kimlik doğrulama ve oturum yönetimi

### Frontend
- **Tailwind CSS:** Modern ve responsive tasarım
- **Font Awesome:** İkonlar için
- **HTML5:** Sayfa yapısı

## Veritabanı Yapısı

### Tablolar
1. **User (Kullanıcı)**
   - Kullanıcı bilgileri (id, isim, email, şifre)
   - Rol bazlı yetkilendirme (admin/müşteri)

2. **Arac**
   - Araç detayları (marka, model, fiyat)
   - Kiralama durumu takibi
   - Resim URL desteği

3. **Kiralama**
   - Kiralama işlem kayıtları
   - Tarih ve süre bilgileri
   - Ödeme tutarı
   - Durum takibi (beklemede/onaylandı/reddedildi)

4. **Yorum**
   - Kullanıcı yorumları
   - Puanlama sistemi
   - Tarih bilgisi

5. **Favori**
   - Kullanıcıların favori araçları

## Özellikler

### Kullanıcı Yönetimi
- Kayıt ve giriş sistemi
- Rol bazlı yetkilendirme (Admin/Müşteri)
- Profil yönetimi

### Araç Yönetimi
- Araç ekleme/düzenleme (Admin)
- Araç listeleme ve detay görüntüleme
- Araç resmi yükleme desteği

### Kiralama Sistemi
- Online kiralama işlemleri
- Ödeme sistemi entegrasyonu
- Kiralama durumu takibi

### Yorum ve Değerlendirme
- Araç puanlama sistemi
- Kullanıcı yorumları
- Ortalama puan hesaplama

### Arayüz Özellikleri
- Responsive tasarım
- Kullanıcı dostu navigasyon
- Flash mesajları ile bilgilendirme
- Dinamik içerik yönetimi

## Güvenlik Özellikleri
- Şifre hashleme
- Oturum yönetimi
- Yetkilendirme kontrolleri
- Güvenli dosya yükleme

## Teknik Detaylar
- SQLite veritabanı kullanımı
- Modüler kod yapısı
- Template inheritance
- RESTful yapı

## Geliştirme Ortamı
Proje için gerekli paketler:
```
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
```

## Sonuç
Bu proje, modern web teknolojilerini kullanarak geliştirilmiş, güvenli ve kullanıcı dostu bir araç kiralama sistemidir. Rol bazlı yetkilendirme, detaylı araç yönetimi, kiralama takibi ve kullanıcı etkileşimi gibi özellikler ile tam kapsamlı bir çözüm sunmaktadır.