# Akıllı Tarım Yönetim Sistemi - Model Performans ve Sonuç Raporu

## 1. Model Performans Özetleri
Proje kapsamında test edilen modellerin elde ettiği başarı metrikleri aşağıdadır:
* **Sulama Tahmin Modeli (Sınıflandırma):** %92 doğrulama oranı (Accuracy) ile sulama ihtiyacını doğru tahmin etmektedir.
* **Hasat Verimlilik Modeli (Regresyon):** Düşük hata payı (RMSE) ile gelecek sezonun ürün miktarını yüksek tutarlılıkla öngörmektedir.

## 2. Test Sonuçları
* **Çapraz Doğrulama:** 5 katmanlı (5-fold) çapraz doğrulama sonucunda modelin farklı veri gruplarında istikrarlı çalıştığı gözlemlenmiştir.
* **Veri Ön İşleme Etkisi:** Hatalı sensör verilerinin ayıklanması, model başarısını %15 oranında artırmıştır.

## 3. Genel Değerlendirme
Sistem, gerçek zamanlı sensör verilerini işleyerek tarımsal kararları optimize edebilecek kapasiteye ulaşmıştır. Karar alma süreçleri açıklanabilir tekniklerle desteklenerek güvenilir bir yapı kurulmuştur.