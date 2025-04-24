# Araç Kiralama Takip Sistemi

Bu proje, araç kiralama firmalarının araç bilgilerini, kiralama tarihlerini ve müşteri kayıtlarını yönetmesini sağlayan bir web uygulamasıdır.

## Özellikler

- Müşteri ve yönetici girişi/kaydı
- Araç listesi görüntüleme
- Araç kiralama işlemleri
- İstatistik ve raporlama
- Responsive tasarım

## Teknolojiler

- Flask (Python web framework)
- Tailwind CSS (CSS framework)
- HTML5
- JavaScript

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Flask uygulamasını başlatın:
```bash
python app.py
```

3. Tarayıcınızda http://localhost:5000 adresine gidin.

## Sayfalar

### Ana Sayfa
- Sistem genel bakış
- Hızlı erişim kartları
- Giriş/kayıt seçenekleri

### Müşteri İşlemleri
- Giriş yap
- Kayıt ol
- Araç kiralama
- Kiralama geçmişi

### Yönetici İşlemleri
- Yönetici girişi
- Yönetici kaydı
- Araç yönetimi
- İstatistikler ve raporlar

### Araçlar
- Araç listesi
- Filtreleme seçenekleri
- Detaylı araç bilgileri

### Kiralama
- Müşteri bilgileri
- Kiralama detayları
- Ödeme işlemleri

### İstatistikler
- Toplam araç sayısı
- Aktif kiralama sayısı
- Aylık gelir
- Popüler araçlar
- Son kiralama işlemleri

## Geliştirme

Proje Flask ve Tailwind CSS kullanılarak geliştirilmiştir. Veritabanı bağlantısı olmadan çalışan bir prototip olarak tasarlanmıştır.

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın. 