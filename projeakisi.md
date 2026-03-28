# “…….”- Proje Akışı ve Haftalık İlerleme
Bu dosya, “……. “ takımının haftalık proje ilerlemesini ve üyelerin görev dağılımlarını içermektedir.
## 1. Hafta (Örn: 9-15 Mart)
* *”….. (Scrum Master / Yönetici):* GitHub reposu oluşturuldu, branch koruma kuralları (main) ayarlandı. Ekibe iş akışı eğitimi verildi. Proje akış dokümanı oluşturuldu.
* *Şevval Yıldız (Yazılım Mühendisi / Proje Analizi)
      Proje Analizi ve Kapsam Belirleme Raporu
  Grup Görevi:
 Akıllı Tarım Yönetim Sistemi (ATYS) projesinin hedeflerinin belirlenmesi, sistem kapsamının tanımlanması ve proje paydaşlarının beklentilerinin analiz edilmesi.
  Proje Tanımı:
Akıllı Tarım Yönetim Sistemi, Nesnelerin İnterneti (IoT) sensörlerinden elde edilen verileri kullanarak tarım süreçlerinin daha verimli ve kontrollü şekilde yönetilmesini amaçlayan bir yazılım sistemidir. Sistem; toprak nemi, sıcaklık ve hava durumu gibi çevresel verileri analiz ederek sulama ve gübreleme süreçlerinin optimize edilmesini hedeflemektedir.
  Fonksiyonel Gereksinimler
*Tarım alanına yerleştirilen IoT sensörlerinden düzenli olarak veri toplanması
*Sensörlerden gelen verilerin sistem tarafından işlenmesi ve veritabanında saklanması
*Kullanıcıların verileri web tabanlı bir yönetim paneli üzerinden görüntüleyebilmesi
*Toplanan veriler doğrultusunda sulama ve tarımsal karar süreçlerinin desteklenmesi
  Teknik Altyapı
*Backend geliştirme sürecinde Python programlama dili ve Django framework kullanılması planlanmıştır.
*Sensörlerden elde edilen verilerin güvenli ve düzenli şekilde saklanması için PostgreSQL veritabanı tercih edilmiştir.
*IoT cihazları ile sistem arasındaki veri iletişiminin sağlanması için MQTT protokolünün kullanılması planlanmaktadır.
  Beklenen Sonuçlar
Bu proje ile birlikte tarım alanlarından elde edilen verilerin dijital ortamda analiz edilmesi ve su kullanımının daha verimli hale getirilmesi hedeflenmektedir. Ayrıca kullanıcıların sensör verilerini kolayca takip edebileceği bir yönetim sistemi oluşturularak tarımsal verimliliğin artırılması amaçlanmaktadır.
  

## 2. Hafta * Tasarım, Mimari ve UI/UX Wireframe (28.03.2026)
Bu hafta Akıllı Tarım Yönetim Sistemi (ATYS) projesinin görsel ve teknik planlaması yapılmıştır.

1. UI/UX Wireframe (Arayüz Taslağı)
Sistemin kullanıcı arayüzü Expo Go (React Native) kullanılarak tasarlanmıştır:

Giriş Ekranı: Çiftçi/Kullanıcı giriş arayüzü.

Ana Panel: Sensör verilerinin (Stok, Nem, Durum vb.) listeleneceği yönetim ekranı.
(Ekran görüntüleri GitHub reposuna "Giris.jpeg" ve "AnaPanel.jpeg" olarak yüklenmiştir.)

2. Veritabanı Şeması (PostgreSQL)
Verilerin düzenli tutulması için şu tablolar planlanmıştır:

Users: (id, ad, eposta, sifre)

Sensors: (id, tip, konum, durum)

Sensor_Logs: (id, sensor_id, deger, zaman)

3. API Tasarımı (Endpoints)
Frontend ve Backend arasındaki iletişim için şu uç noktalar belirlenmiştir:

POST /api/login/: Kullanıcı doğrulama.

GET /api/dashboard/: Canlı sensör verilerini çekme.
