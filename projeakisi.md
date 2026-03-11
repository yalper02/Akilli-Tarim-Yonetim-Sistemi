# “…….”- Proje Akışı ve Haftalık İlerleme
Bu dosya, “……. “ takımının haftalık proje ilerlemesini ve üyelerin görev dağılımlarını içermektedir.
## 1. Hafta (Örn: 9-15 Mart)
* *”….. (Scrum Master / Yönetici):* GitHub reposu oluşturuldu, branch koruma kuralları (main) ayarlandı. Ekibe iş akışı eğitimi verildi. Proje akış dokümanı oluşturuldu.
* **Cihan Akalın (Yazılım Mühendisi / Teknoloji Araştırması):**
    ### 🎯 Teknoloji Araştırması ve Mimari Seçimi Raporu
    **Grup Görevi:** Proje altyapısının belirlenmesi ve teknik fizibilite çalışması.
    * **Mimari Yaklaşım:** Projemiz, IoT cihazlarından gelen anlık ve yoğun veri trafiğini (sıcaklık, nem vb.) asenkron olarak yönetebilmek adına **Event-Driven (Olay Güdümlü)** bir mimari üzerine kurgulanmıştır.
    * **Seçilen Teknoloji Yığını (Tech Stack) ve Analiz:**
        * **Backend (Django):** Veri modelleme hızı ve yerleşik admin paneli sayesinde "Web Yönetim Paneli" teslimatı için en güvenli liman olarak seçildi. Özellikle **PostgreSQL** ile olan yerleşik uyumu, tarım verilerinin yüksek tutarlılıkla saklanmasını sağlar.
        * **Veritabanı (PostgreSQL):** Standart SQL yapısının yanında sunduğu **JSONB** desteği sayesinde, farklı IoT sensörlerinden gelebilecek değişken veri formatlarına (NoSQL esnekliğiyle) uyum sağlayabildiği için tercih edildi.
        * **Protokol (MQTT):** Klasik HTTP protokolünün aksine, çok düşük bant genişliği ve güç tüketimiyle çalışan **Publish/Subscribe** modeli sayesinde sahadaki sensörlerin pil ömrünü maksimize eder.
        * **Tahmin Algoritmaları:** Python tabanlı **Scikit-Learn** kütüphanesi kullanılarak, geçmiş hava durumu verileri üzerinden "Gelecek 24 saatlik sulama/gübreleme ihtiyacı" tahmini yapılması planlanmıştır.
    * **💡 Sıkça Sorulan Sorular ve Teknik Kararlar:**
        * **Neden Flask değil de Django?** Proje teslimatında "Yönetim Paneli" zorunlu bir modül olduğu için Django'nun hazır Admin sistemi geliştirme maliyetini ve süresini ciddi oranda düşürecektir.
        * **Veri Güvenliği:** IoT cihazları ile sunucu arasındaki iletişimde **TLS/SSL** sertifikaları kullanılacak; API katmanında ise **Rate Limiting** ile kaba kuvvet saldırılarına karşı önlem alınacaktır.
