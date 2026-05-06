# Akıllı Tarım Yönetim Sistemi - Algoritma ve Raporlama Tasarımı

## 1. Tahmin Algoritmaları
Sistemimizde verimliliği artırmak için şu makine öğrenmesi modelleri planlanmıştır:
* **Sulama Tahmini (Sınıflandırma):** Toprak nemi ve sıcaklık verilerine bakarak "Sulama Gerekli mi?" sorusuna Karar Ağaçları (Decision Trees) algoritması ile yanıt verilecektir.
* **Hasat Verimliliği (Regresyon):** Geçmiş veriler ışığında, mevcut parametrelerle beklenen ürün miktarı Lineer Regresyon modeli ile tahmin edilecektir.

## 2. Doğrulama ve Güvenilirlik
Algoritmaların hata payını en aza indirmek için şu teknikler kullanılacaktır:
* **Çapraz Doğrulama (Cross-Validation):** Veri seti farklı parçalara bölünerek modelin her parçada doğru çalışıp çalışmadığı test edilecektir.
* **Eğitim/Test Ayrımı:** Verilerin %80'i modelin eğitimi, %20'si ise performans ölçümü için kullanılacaktır.

## 3. Raporlama Formatı
Kullanıcılara (çiftçilere) sunulacak raporlar şu içeriklere sahip olacaktır:
* **Günlük Durum Özeti:** Anlık sıcaklık, nem ve sistemin verdiği "sulama" kararı.
* **Haftalık Grafik:** Nem oranlarındaki değişim ve verimlilik tahmin grafikleri.
* **Uyarı Bildirimleri:** Kritik eşik değerleri aşıldığında (Örn: Aşırı sıcaklık) üretilen anlık raporlar.