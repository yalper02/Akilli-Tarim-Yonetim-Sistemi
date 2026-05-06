# Akıllı Tarım Yönetim Sistemi - Model Açıklanabilirliği Tasarımı

## 1. Amaç
Makine öğrenmesi modellerinin verdiği kararların (örneğin sulama kararı veya verimlilik tahmini) hangi kriterlere dayandığını şeffaf bir şekilde ortaya koymaktır.

## 2. Kullanılacak Teknikler
* **Özellik Önem Sıralaması (Feature Importance):** Karar verilirken toprak neminin mi, hava sıcaklığının mı daha etkili olduğunu yüzdesel olarak raporlayacağız.
* **SHAP (SHapley Additive exPlanations):** Modelin verdiği her bir kararın arkasındaki temel değişkenleri görselleştirerek kullanıcıya (çiftçiye) neden-sonuç ilişkisi sunacağız.

## 3. Kullanıcıya Sunum
Kullanıcı arayüzünde sadece "Sulama Gerekli" yazmayacak; yanında "Düşük toprak nemi nedeniyle sulama öneriliyor" gibi açıklayıcı metinler yer alacaktır.