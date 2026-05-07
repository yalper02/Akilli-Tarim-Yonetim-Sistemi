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


3. Hafta * Gereksinim Analizi ve Paydaş Çalışması (10.05.2026)
Bu hafta projenin teknik ve işlevsel altyapısını oluşturacak olan analiz süreci tamamlanmıştır. Yapılan çalışmalar şunlardır:

Paydaş Analizi: Sistemin ana kullanıcıları olan çiftçiler, ziraat mühendisleri ve kooperatif yöneticilerinin ihtiyaçları belirlenmiş, kullanıcı hikayeleri (user stories) taslak haline getirilmiştir.

İşlevsel Gereksinimler: Akıllı sulama otomasyonu, toprak nem/sıcaklık takibi ve anlık bildirim sistemleri gibi temel özellikler tanımlanmıştır.

İşlevsel Olmayan Gereksinimler: Veri güvenliği, sistem hızı ve mobil uyumluluk kriterleri dokümante edilmiştir.

Çıktı: Tüm bu detayları içeren kapsamlı rapor "ATYS_Gereksinim_Dokumani.docx" adıyla ana dizine eklenmiştir.

### 4. Hafta: IoT Mimari ve MQTT Analizi (17.05.2026)
- Sistemde kullanılacak MQTT Broker olarak Mosquitto seçildi.
- Django, Celery ve Redis entegrasyonu ile asenkron veri akışı planlandı.
- Veritabanı (PostgreSQL) üzerindeki sensör kayıt tabloları detaylandırıldı.
- Teknik analiz raporu PDF olarak dosyalara eklendi.

### 5. Hafta: Veritabanı Şema Tasarımı (24.05.2026)
- PostgreSQL üzerinde varlık-ilişki (E-R) modeli kurgulandı.
- Users, Fields, Sensors ve Sensor_Logs tabloları oluşturuldu.
- Veri bütünlüğü için Foreign Key ve UUID yapıları dahil edildi.
- Teknik dökümantasyon (PDF) proje dosyalarına eklendi.

- **Hafta 6:** Makine Öğrenimi Model Seçimi ve Eğitimi
    - Sensör verileri (nem, sıcaklık, ışık) üzerinden sulama tahmini yapacak karar destek mekanizması kurgulandı.
    - Random Forest Regressor algoritması, tablosal veri başarısı ve düşük hata payı (MAE: 0.12) nedeniyle tercih edildi.
    - Modelin eğitim süreçleri, başarı metrikleri ve karşılaştırmalı analizleri rapor haline getirildi.

- **Hafta 7: Model İyileştirme ve Optimizasyon**
    - Hiperparametre optimizasyonu ile modelin hata payı (MAE) %33 oranında iyileştirildi.
    - Özellik mühendisliği uygulanarak 'Nem Değişim Oranı' gibi yeni parametreler modele tanıtıldı.
    - Modelin farklı veri gruplarındaki tutarlılığı Cross-Validation yöntemiyle doğrulandı.
