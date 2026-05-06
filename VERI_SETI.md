# Akıllı Tarım Yönetim Sistemi - Veri Seti Dokümantasyonu

## 1. Veri Seti İçeriği
Sistemimiz, bir tarlanın sağlığını ve verimliliğini takip etmek için şu parametreleri anlık olarak izler:
* **Toprak Nemi (%):** Bitkinin sulama ihtiyacını belirler.
* **Hava Sıcaklığı (°C):** Ortamın bitki gelişimi için uygunluğunu ölçer.
* **Hava Nemi (%):** Hastalık riskini ve buharlaşma oranını takip eder.
* **Işık Şiddeti (Lux):** Fotosentez verimliliği için güneşlenme süresini ölçer.

## 2. Veri Kaynakları
Veriler iki ana kanaldan elde edilmektedir:
1. **Sensör Verileri:** Fiziksel ortamdan DHT11 (Sıcaklık/Nem) ve YL-69 (Toprak Nemi) sensörleri aracılığıyla toplanan gerçek zamanlı veriler.
2. **Simülasyon Verileri:** Test aşamasında PostgreSQL veritabanına Python scriptleri ile üretilen sentetik tarım verileri.

## 3. Veri Ön İşleme Adımları
Veritabanına kaydedilmeden önce veriler şu işlemlerden geçer:
* **Hata Ayıklama:** Sensörlerden gelen anlamsız (uç) değerler (Örn: Sıcaklığın -100 görünmesi) filtrelenir.
* **Zaman Damgası:** Her veri paketi, kaydedildiği tarih ve saat bilgisiyle (Timestamp) işaretlenir.
* **Normalizasyon:** Farklı sensörlerden gelen veriler, raporlama için ortak bir standart aralığa getirilir.
