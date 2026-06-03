# “Akıllı Tarım Yönetim Sistemi”- Proje Akışı ve Haftalık İlerleme

Bu dosya, “Veri Sİhirbazları“ takımının haftalık proje ilerlemesini ve üyelerin görev dağılımlarını içermektedir.

## 1. Hafta (4 Mayıs - 10 Mayıs)

### Yiğit Alper Ayhan (Scrum Master / Yönetici): Proje Yönetim Aracı Kurulumu ve Konfigürasyonu

__Proje Tanımı__
Belge, Akıllı Tarım Yönetim Sistemi projesinin yönetim aracı kurulumunu ve konfigürasyonunu ele almaktadır. Sistem; IoT sensörleri aracılığıyla veri toplama, toprak nemi analizi ve akıllı sulama önerisi gibi temel işlevlere sahiptir.

__Kullanılan Teknolojiler__
Teknoloji	    Kullanım Alanı
Python	        Ana programlama dili
Django	        Web framework (Backend)
MQTT	        IoT iletişim protokolü
PostgreSQL	    Veritabanı
IoT Sensörleri	Saha veri toplama

Proje Yönetim Aracı: Jira
__Jira'nın tercih edilme nedenleri:__

**Görev takibi —** Tüm görevlerin izlenmesi ve atanması

**Sprint yönetimi —** Agile metodolojiye uygun çalışma döngüleri

**Ekip koordinasyonu —** Takım üyeleri arası iş birliği ve iletişim

__İş Akışı (Workflow)__
Projede üç aşamalı basit bir iş akışı tanımlanmıştır:

To Do  →  In Progress  →  Done

To Do — Görev oluşturulur ve backlog'a eklenir
In Progress — Görev üzerinde aktif olarak çalışılır
Done — Görev tamamlanır ve kapatılır

__Sprint Planı__
Proje 4 sprint halinde planlanmıştır:

Sprint	    Odak Alanı	Açıklama
Sprint 1	IoT	        Sensör entegrasyonu ve veri toplama altyapısı
Sprint 2	Backend	    Django tabanlı sunucu tarafı geliştirme
Sprint 3	Analiz	    Toplanan verilerin analizi ve modelleme
Sprint 4	Arayüz	    Kullanıcı arayüzü tasarımı ve geliştirme

__ÇALIŞMA DOSYALARI__

[Proje Yönetim Aracı Kurulumu ve Konfigürasyonu Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/feature/proje-y%C3%B6netim-arac%C4%B1-kurulumu-ve-konfig%C3%BCrasyonu/OneDrive/Masa%C3%BCst%C3%BC/Proje)

### Cihan Akalın: IoT Sensörleri Araştırması ve Seçimi
__1. Donanım Seçimleri__

**Toprak Nemi Sensörü:** Direnç tipi (FC-28) ve kapasitif tip (v1.2) karşılaştırılmış; korozyon riski taşımayan ve daha uzun ömürlü olan Kapasitif Sensör v1.2 seçilmiştir.

**Hava Sıcaklık ve Nem Sensörü:** DHT11 ve DHT22 modelleri incelenmiş; daha yüksek hassasiyet ve geniş ölçüm aralığı sunan DHT22 (AM2302) tercih edilmiştir.

**Mikrodenetleyici:** Düşük güç tüketimi ve dahili Wi-Fi desteği nedeniyle ESP32 geliştirme kartı seçilmiştir.

__2. İletişim Protokolü__

**MQTT Protokolü:** HTTP ile kıyaslandığında daha düşük enerji tüketimi, hafif veri yapısı ve gerçek zamanlı asenkron veri akışı (Publish/Subscribe) sağladığı için tercih edilmiştir.

__3. Enerji ve Maliyet Özeti__

**ESP32:** Aktif kullanımda ~240mA, derin uyku (Deep Sleep) modunda ~10µA tüketim. (Maliyet: Orta)

**DHT22:** Aktif ölçümde ~1.5mA tüketim. (Maliyet: Düşük)

**Kapasitif Sensör:** Aktif ölçümde ~5mA tüketim. (Maliyet: Çok Düşük)

__ÇALIŞMA DOSYALARI__

[IoT Sensörleri Araştırması ve Seçimi Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/IoT%20Sens%C3%B6rleri%20Ara%C5%9Ft%C4%B1rmas%C4%B1%20ve%20Secimi.pdf)

[Sensör ve Donanım Seçimi Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/docs/research/Hafta1_Sensor_ve_Donanim_Secimi.pdf)

### Zehra Özdemir: Backend Altyapı Araştırması ve Kurulumu
Bu görevde Akıllı Tarım Yönetim Sistemi için backend altyapısı kurulmuştur. Python ve Django kullanılarak proje oluşturulmuş, PostgreSQL veritabanı ile bağlantı sağlanmıştır.
Geliştirme ortamı için sanal ortam oluşturulmuş ve gerekli kütüphaneler (Django, Django REST Framework, psycopg2 vb.) kurulmuştur. Daha sonra Django projesi başlatılmış ve temel ayarlar yapılmıştır.
Veritabanı olarak PostgreSQL kullanılmış, gerekli ayarlamalar yapılarak projeye entegre edilmiştir. Ayrıca .env dosyası kullanılarak veritabanı bilgileri daha güvenli hale getirilmiştir.
Son olarak Django REST Framework ile basit bir API yapısı kurulmuş ve örnek olarak sensör verilerini tutan bir model oluşturulmuştur.
Bu çalışmalar sonucunda projenin backend temeli hazır hale getirilmiştir.

__ÇALIŞMA DOSYALARI__

[Backend Altyapı Config Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Zehra/config)

[Backend Altyapı Config Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Zehra/config/__pycache__)

[Config asgi.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/config/asgi.py)

[Config settings.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/config/settings.py)

[Config urls.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/config/urls.py)

[Config wsgi.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/config/wsgi.py)

[Backend Altyapı tarim_api Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Zehra/tarim_api)

[tarim_api migrations Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Zehra/tarim_api/migrations)

[tarim_api admin.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/tarim_api/admin.py)

[tarim_api apps.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/tarim_api/apps.py)

[tarim_api models.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/tarim_api/models.py)

[tarim_api tests.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/tarim_api/tests.py)

[tarim_api views.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/tarim_api/views.py)

[Backend Altyapı .gitignore Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/.gitignore)

[Backend Altyapı db.sqlite3 Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/db.sqlite3)

[Backend Altyapı manage.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/manage.py)

[Backend Altyapı requirements.txt Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/requirements.txt)

### Şevval Yıldız: Proje Paydaşları ve Gereksinim Analizi
__1. Proje Paydaşları__
**Çiftçiler:** Sistemin ana kullanıcılarıdır; nem ve sıcaklık gibi verileri takip ederek sulama süreçlerini yönetir, iş yükünü azaltıp verimi artırmayı hedeflerler.

**Ziraat Mühendisleri:** Verileri analiz ederek üretim sürecini optimize eder ve çiftçilere rehberlik ederler.

**Kooperatif ve İşletme Yöneticileri:** Bölgesel istatistikleri ve lojistik süreçleri takip ederler.

**Geliştirici Ekip:** Yazılım ve IoT donanım altyapısını kurar, sistemin güvenli ve kesintisiz çalışmasını sağlarlar.

__2. İşlevsel Gereksinimler (Sistemin Yapacakları)__

**Veri Takibi:** Toprak nemi, hava sıcaklığı ve ışık şiddeti gibi verilerin sensörlerle gerçek zamanlı toplanması.

**Akıllı Otomatik Sulama:** Toprak nemi belirlenen eşik değerin altına düştüğünde sulamanın otomatik başlatılması.

**Uzaktan Kontrol:** Kullanıcıların pompa sistemini mobil veya web üzerinden manuel olarak yönetebilmesi.

**Bildirim Sistemi:** Don riski veya sensör arızası gibi kritik durumlarda kullanıcıya anlık uyarı gönderilmesi.

__3. İşlevsel Olmayan Gereksinimler (Sistemin Niteliği)__

**Kullanılabilirlik:** Sade ve her yaştan çiftçinin kullanabileceği anlaşılır bir arayüz.

**Performans:** Veri güncellemelerinde 5 saniyeyi geçmeyen düşük gecikme süresi.

**Güvenlik ve Süreklilik:** 7/24 çalışma kapasitesi, yetkisiz erişimin engellenmesi ve internet kesintisinde veri kaybı yaşanmaması.

__4. Varsayımlar ve Kısıtlar__

**Varsayımlar:** Kullanıcıların temel akıllı telefon bilgisine sahip olduğu, IoT donanımının kullanıcı tarafından sağlandığı ve harici bir meteoroloji API'si kullanılacağı varsayılmıştır.

**Kısıtlar:** Çevrimdışı modun kısıtlı işlevle çalışması, ilk fazda sadece Türkiye iklimi ve Türkçe dil desteği sunulması, bütçe nedeniyle görüntü tabanlı hastalık tespitinin 2. faza ertelenmesi.

__ÇALIŞMA DOSYALARI__

[Gereksinim Dokümanı Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/%C5%9Eevval/ATYS_Gereksinim_Dokumani.docx)

### Muhammed Cengiz:

### Abdulrahman Shawa:

## 2. Hafta (11 Mayıs - 17 Mayıs)

### Yiğit Alper Ayhan (Scrum Master / Yönetici): Özellik Mühendisliği Araştırması
Akıllı tarım sistemlerinde model performansını artırmak için sensörlerden elde edilen ham veriler işlenerek çeşitli türetilmiş özellikler elde edilebilir. Sıcaklık ve toprak nemi değişim hızları, bitkinin sulama ihtiyacını ve olası stres durumunu öngörmek için kritik göstergelerdir. Yağışın gecikmeli etkisi ve son 24 saatlik yağış miktarı gibi özellikler, sulama kararlarını optimize ederek ciddi su tasarrufu sağlar. Günün saatleri veya mevsim gibi zaman tabanlı veriler ile geçmiş saatlerin hareketli ortalamaları, modellerin gürültüden arınarak anlamlı kalıpları öğrenmesine yardımcı olur. Farklı çevresel verilerin birleştirilmesiyle oluşturulan bütünleşik bitki stres indeksleri, bitkinin zor durumda olup olmadığını doğrudan yansıtan çok güçlü özelliklerdir. Son olarak, geçmiş periyotlardaki durumları ifade eden gecikmeli veriler ve ani değişimleri yakalayan anomali göstergeleri, zaman serisi modellemelerinde ve erken uyarı sistemlerinde yüksek doğruluk elde edilmesini mümkün kılar.

__ÇALIŞMA DOSYALARI__

[Özellik Mühendisliği Araştırması Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/feature/%C3%B6zellik-m%C3%BChendisli%C4%9Fi-ara%C5%9Ft%C4%B1rmas%C4%B1/%C3%96zellik_M%C3%BChendisli%C4%9Fi_Ara%C5%9Ft%C4%B1rmas%C4%B1.pdf)

[ozellik_muhendisliği.py Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/feature/%C3%B6zellik-m%C3%BChendisli%C4%9Fi-ara%C5%9Ft%C4%B1rmas%C4%B1/ozellik_muhendisligi.py)

### Cihan Akalın: IoT Sensör Veri Akışı ve MQTT Mimari Planlaması
Akıllı Tarım Yönetim Sistemi kapsamında, toprak nemi, sıcaklık ve hava durumu sensörlerinin entegrasyonu için güvenli ve ölçeklenebilir bir MQTT tabanlı veri akış mimarisi planlanmaktadır. Bu mimari çerçevesinde, cihazlar arasındaki iletişimi düzenlemek amacıyla hiyerarşik bir konu (topic) yapısı, uygun hizmet kalitesi (QoS) seviyeleri ve güvenlik standartları belirlenerek merkezi bir mesaj dağıtıcı (broker) yapılandırılacaktır. Sensörlerden gelen ham veriler, Python tabanlı bir MQTT istemcisi aracılığıyla gerçek zamanlı olarak dinlenecek ve veri kaybı olmadan sisteme dahil edilecektir. Toplanan sensör verileri, sensör türü, lokasyon ve zaman damgası gibi kritik bilgileri barındıracak şekilde tasarlanmış bir PostgreSQL veritabanı şemasına düzenli olarak kaydedilecektir. Sistemin arka planını oluşturan Django yapısı, bu veritabanı ile tam entegre çalışarak verilerin işlenmesi, analiz edilmesi ve kullanıcı paneline yansıtılması süreçlerini yönetecektir. Tüm bu uçtan uca veri aktarım süreci, sistemin genel işleyişini gösteren veri akış diyagramları ve yapısal taslakları barındıran kapsamlı bir mimari planlama dokümanı ile detaylandırılacaktır.

__ÇALIŞMA DOSYALARI__

[IoT Sensör Veri Akışı ve MQTT Mimari Planlaması Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/IoT%20Sens%C3%B6r%20Veri%20Ak%C4%B1%C5%9F%C4%B1%20ve%20MQTT%20Mimari%20Planlamas%C4%B1.pdf)

### Zehra Özdemir: Veri Seti Dokümantasyonu
Proje kapsamında kullanılacak veri setinin genel yapısını, temel özniteliklerini ve içerdiği değişkenlerin anlamlarını detaylandıran kapsamlı bir dokümantasyon hazırlanacaktır. Bu doküman içerisinde, verilerin toplandığı IoT sensör ağları, dış API servisleri veya referans veritabanları gibi tüm birincil ve ikincil veri kaynakları şeffaf bir biçimde belirtilecektir. Ham verilerin modellemeye uygun hale getirilmesi sürecinde uygulanan eksik veri tamamlama, aykırı değer tespiti, gürültü filtreleme ve veri normalizasyonu gibi temel ön işleme adımları sırasıyla açıklanacaktır. Veriler üzerinde gerçekleştirilen her türlü dönüşüm işlemi ve veri tiplerinin nasıl standartlaştırıldığı, ilerideki çalışmalar için tekrarlanabilirlik ilkesine uygun olarak raporlanacaktır. Kullanılacak veri setinin toplam boyutu, kapsadığı zaman aralığı ve değişken dağılımları gibi istatistiksel özet bilgileri detaylıca sunulacaktır. Hazırlanan bu standart veri dokümantasyonu, sistemin makine öğrenmesi modellerinin geliştirilmesi ve algoritmik analizlerin güvenilir bir şekilde yürütülmesi için kalıcı bir referans kaynağı görevi görecektir.

__ÇALIŞMA DOSYALARI__

[Veri Seti Dokümantasyonu Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/VERI_SETI.md)

### Şevval Yıldız: IoT Sensör Veri Akışı ve MQTT Mimari Analizi
Akıllı Tarım Yönetim Sistemi'nin sensör entegrasyonu için Mosquitto ve HiveMQ gibi popüler MQTT broker seçenekleri karşılaştırmalı olarak incelenerek performansı projeye en uygun olan altyapı belirlenecektir. Sahadan gelen verilerin düzenli bir şekilde yönlendirilmesini sağlamak adına, tarla numarası ve sensör tipi gibi değişkenleri içeren ölçeklenebilir bir MQTT konu (topic) hiyerarşisi tasarlanacaktır. Ham verilerin sisteme güvenilir ve sürekli bir biçimde aktarılması için Python paho-mqtt altyapısı kullanılarak sağlam bir abone olma ve mesaj yayınlama (subscribe/publish) mimarisi oluşturulacaktır. Toplanan bu verilerin zaman serisi mantığıyla kalıcı hale getirilmesi amacıyla, içerisinde sensör kimliği, zaman damgası ve ölçüm değeri gibi temel alanları barındıran bir PostgreSQL veritabanı şeması dizayn edilecektir. Sistemin asıl iş mantığını yürütecek olan Django mimarisi ile MQTT iletişim ağı arasındaki entegrasyon noktaları ve olası veri yığılmalarına karşı mesaj kuyruk yönetim stratejileri detaylıca planlanacaktır. Tüm bu analiz ve tasarım süreçlerinin sonucunda, sistemin uçtan uca işleyişini görselleştiren veri akış diyagramları ve detaylı teknik dokümanlar hazırlanarak ekip içi değerlendirmeye sunulacaktır.

__ÇALIŞMA DOSYALARI__

[IoT Sensör Veri Akışı ve MQTT Mimari Analizi Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/%C5%9Eevval/Hafta4_IoT_MQTT_Teknik_Rapor.pdf)

### Muhammed Cengiz: IoT Sensör Veri Akışı ve MQTT Mimari Analizi
Akıllı Tarım Yönetim Sistemi'nde kullanılacak çeşitli IoT sensörlerinden toplanacak verilerin sisteme sorunsuz aktarılması için yayıncı-abone modelini temel alan bir mimari planlaması yapılacaktır. Tasarım sürecinde, projenin performans ve ölçeklenebilirlik ihtiyaçlarına en uygun mesajlaşma altyapısını kurmak amacıyla Mosquitto ve HiveMQ gibi farklı MQTT broker seçenekleri detaylıca karşılaştırılacaktır. Cihazlar arası iletişimi organize etmek için tarla ve sensör tiplerini temel alan hiyerarşik bir konu (topic) yapısı oluşturulacak ve her bir sensörün sisteme veri gönderim sıklığı standartlaştırılacaktır. Ağ üzerindeki veri iletişiminin güvenilirliğini ve tutarlılığını sağlamak adına paketler için standart bir JSON şeması tasarlanacak ve ağ koşullarına uygun hizmet kalitesi (QoS) seviyeleri tanımlanacaktır. Geliştirilen bu IoT sensör ağı iletişim altyapısının, Python tabanlı kütüphaneler yardımıyla uygulamanın ana omurgasını oluşturan Django sistemi ile nasıl entegre edileceği planlanacaktır. Gerçekleştirilen tüm bu mimari kararlar, genel sistem entegrasyonunu gösteren veri akış diyagramları ile desteklenen kapsamlı bir analiz dokümanı haline getirilerek projelendirilecektir.

__ÇALIŞMA DOSYALARI__

[docs Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/docs)

[backend Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/backend)

[simulator Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/simulator)

[docker Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/docker)

### Abdulrahman Shawa:

## 3. Hafta (18 Mayıs - 24 Mayıs)

### Yiğit Alper Ayhan (Scrum Master / Yönetici): Veri Toplama ve Analiz Modülü Tasarımı
Akıllı Tarım Yönetim Sistemi için IoT sensörlerinden elde edilen ham verileri merkezi olarak toplayacak, temizleyecek ve analiz edecek kapsamlı bir veri işleme modülü tasarlanmaktadır. Sisteme akan verilerin kalitesini artırmak amacıyla eksik değerlerin doldurulması, aykırı değerlerin ayıklanması ve farklı veri formatlarının standartlaştırılması gibi doğrulama adımları detaylı bir şekilde uygulanacaktır. Temizlenen bu veriler üzerinde hem temel istatistiksel analiz yöntemleri hem de gelişmiş makine öğrenmesi algoritmaları kullanılarak geleceğe yönelik tarımsal tahmin modelleri oluşturulacaktır. Geliştirilecek olan bu güçlü analiz modülü, Python tabanlı veri bilimi kütüphaneleriyle desteklenerek uygulamanın omurgasını oluşturan Django mimarisiyle kesintisiz çalışan bir arka plan servisi olarak entegre edilecektir. Kullanıcılara anlaşılır ve hızlı bilgiler sunabilmek için, elde edilen analiz sonuçları modern JavaScript görselleştirme kütüphaneleri kullanılarak etkileşimli grafikler ve gösterge panellerine (dashboard) dönüştürülecektir. Bu entegre sistem sayesinde, sahadan toplanan karmaşık sensör verileri, üreticilerin anlık karar alma süreçlerini destekleyecek eyleme dönüştürülebilir anlamlı içgörülere çevrilecektir.

__ÇALIŞMA DOSYALARI__

[Veri Toplama ve Analiz Modülü Tasarımı Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/feature/veri-toplama-ve-analiz-mod%C3%BCl%C3%BC-tasar%C4%B1m%C4%B1/Veri_Toplama_ve_Analiz_Mod%C3%BCl%C3%BC_Tasar%C4%B1m%C4%B1_tex.pdf)

[veri_analiz_modulu Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/feature/veri-toplama-ve-analiz-mod%C3%BCl%C3%BC-tasar%C4%B1m%C4%B1/veri_analiz_modulu)

### Cihan Akalın: Web Tabanlı Yönetim Paneli Arayüz Tasarımı
Akıllı Tarım Yönetim Sistemi'nin paydaşlar tarafından verimli bir şekilde kullanılabilmesi amacıyla, sezgisel ve modern bir web tabanlı yönetim paneli arayüzü tasarlanacaktır. Kullanıcıların karşısına çıkacak olan ana sayfada (dashboard), anlık sensör verileri, kritik sistem uyarıları ve tarımsal süreçleri özetleyen temel metrikler kolay anlaşılır grafiklerle sunulacaktır. Menü yönlendirmeleri, veri giriş formları, cihaz yönetim ekranları ve diğer tüm etkileşimli öğeler, kullanıcı deneyimini en üst seviyeye çıkaracak şekilde sadeleştirilecektir. Sistemdeki farklı sorumlulukları güvenli bir şekilde yönetmek için sistem yöneticisi, ziraat uzmanı ve çiftçi gibi çeşitli kullanıcı rollerine özel erişim yetkileri ve özelleştirilmiş ekranlar planlanacaktır. Tüm bu sayfaların yerleşimi, kullanıcı akışları ve görsel hiyerarşisi, yazılım geliştirme sürecinden önce Figma veya Adobe XD gibi profesyonel araçlar kullanılarak yüksek çözünürlüklü prototipler haline getirilecektir. Ortaya çıkarılacak olan bu görsel arayüz tasarımları, karmaşık tarımsal verilerin yönetimini kolaylaştırmayı ve kullanıcılara kusursuz bir dijital deneyim sunmayı amaçlamaktadır.

__ÇALIŞMA DOSYALARI__

[Sistem gereksinimleri Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/SISTEM_GEREKSINIMLERI.txt)

[requirements Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/requirements.txt)

[core/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/core)

[visualization/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/visualization)

[scripts/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/scripts)

[locale/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/locale)

### Zehra Özdemir: Raporlama ve Tahmin Algoritmaları Tasarımı
Sistemde toplanan tarihsel ve anlık tarımsal veriler kullanılarak, optimum sulama zamanlaması ve beklenen ürün rekoltesi gibi kritik konularda proaktif tahminler üretecek algoritmaların mimarisi tasarlanacaktır. Bu tahminleme işlemleri için verinin yapısına uygun olarak çoklu doğrusal regresyon, rastgele orman (random forest) ve zaman serisi analizi gibi makine öğrenmesi modelleri seçilerek temel hiperparametreleri belirlenecektir. Geliştirilen bu algoritmaların gerçek dünya senaryolarında doğruluğunu ve güvenilirliğini en üst düzeye çıkarmak amacıyla k-katlı çapraz doğrulama (k-fold cross validation) gibi sağlam test teknikleri uygulanacaktır. Tahmin modellerinin yanı sıra, sistemdeki sensör verilerini dönemsel olarak analiz eden ve tarlanın genel sağlık durumunu özetleyen kapsamlı istatistiksel raporlar otomatik bir döngüde üretilecektir. Hazırlanacak olan bu raporların içeriği, kullanıcıların kolayca yorumlayabileceği grafiklerle desteklenerek PDF veya e-tablo formatlarında dışa aktarılabilir şekilde standartlaştırılacaktır. Planlanan bu analitik ve algoritmik altyapı, üreticilerin salt veri okumasından ziyade geleceğe yönelik veri odaklı, verimli ve stratejik tarım kararları alabilmesine olanak tanıyacaktır.

__ÇALIŞMA DOSYALARI__

[ALGORİTMA_TASARIMI.md Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/ALGOR%C4%B0TMA_TASARIMI.md)

### Şevval Yıldız: Veritabanı Şema Tasarımı
Akıllı Tarım Yönetim Sistemi'nin temel verilerini güvenli ve yapılandırılmış bir şekilde saklamak amacıyla, projenin tüm ihtiyaçlarını kapsayan ilişkisel bir PostgreSQL veritabanı şeması tasarlanacaktır. Tasarım sürecinde, sistem kullanıcıları, IoT sensör cihazları, çevresel ölçüm verileri, tarımsal ürün bilgileri ve geçmiş sulama operasyonları gibi temel bileşenler için ayrı tablolar oluşturularak bu varlıkların veri tipleri detaylandırılacaktır. Tablolar arasındaki veri tutarlılığını sağlamak ve referans bütünlüğünü korumak için her tabloya uygun birincil anahtarlar (primary key) ve aralarındaki bağları kuracak yabancı anahtarlar (foreign key) tanımlanacaktır. Özellikle sürekli kayıt alan sensör tabloları gibi yüksek hacimli veri barındıran yapılar üzerinde, gelecekteki sorgu ve analiz performansını maksimize edecek özel indeksleme stratejileri kurgulanacaktır. Oluşturulan veri modellerinin ve tabloların birbirleriyle olan karmaşık bağlantıları, projenin şeffaflığını artırmak adına ilişkisel veri diyagramları (ER Diyagramı) ile görsel hale getirilecektir. Planlanan tüm bu mimari tasarım, yazılım geliştirme aşamasında doğrudan veritabanına uygulanabilecek bir Veri Tanımlama Dili (DDL) betiğine dönüştürülerek dokümantasyon sürecine eklenecektir.

__ÇALIŞMA DOSYALARI__

[Veritabanı Şema Tasarımı Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/%C5%9Eevval/Hafta5_Veritabani_Sema_V2_Final.pdf)

### Muhammed Cengiz: IoT Sensör Entegrasyon Mimarisi Tasarımı
Projede yer alan toprak nemi, hava sıcaklığı ve meteorolojik ölçüm cihazları gibi çeşitli IoT sensörlerinden toplanacak verilerin sisteme kesintisiz aktarımı için MQTT tabanlı bir entegrasyon mimarisi tasarlanacaktır. Sahadaki farklı sensör türleri tarafından üretilen karmaşık metrikler, önceden belirlenmiş standart JSON formatlarına dönüştürülerek merkezi bir mesajlaşma aracı (broker) üzerinden uygulamaya iletilecektir. İletilen bu ham sensör verileri, sistemin arka planında sürekli çalışan dinleyici servisler tarafından anlık olarak yakalanarak gerekli filtreleme ve doğrulama süreçlerinden geçirilecektir. Ağ üzerindeki iletişimin ve cihazların güvenliğini en üst düzeye çıkarmak amacıyla, sensörlerin kimlik doğrulama işlemleri zorunlu kılınacak ve tüm veri aktarımı şifreli kanallar üzerinden gerçekleştirilecektir. Doğrulanıp işlenen veriler, ilerleyen dönemlerde sisteme dahil olabilecek binlerce yeni sensörün yaratacağı anlık veri trafiğini darboğaz yaratmadan kaldırabilecek ölçeklenebilir bir veritabanı altyapısında saklanacaktır. Hazırlanacak olan bu kapsamlı entegrasyon planı, verinin sahadan alınıp bulut ortamına aktarılmasına kadar geçen tüm süreçleri standartlaştırarak sistemin güvenli bir şekilde büyümesine olanak tanıyacaktır.

__ÇALIŞMA DOSYALARI__

[docs Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/docs)

[backend Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/backend)

[simulator Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/simulator)

[docker Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/docker)

### Abdulrahman Shawa:

## 4. Hafta (25 Mayıs - 31 Mayıs)

### Yiğit Alper Ayhan (Scrum Master / Yönetici): Model Validasyonu
Model validasyonu, geliştirilen modelin genelleme yeteneğini ölçmek, aşırı öğrenme (overfitting) riskini azaltmak ve en iyi modeli seçmek amacıyla uygulanan kritik bir süreçtir. Veriyi yalnızca tek bir eğitim-test setine ayırmak yerine, verinin birden çok parçaya bölündüğü ve her parçanın sırayla test edildiği çapraz doğrulama (cross-validation) teknikleri kullanılır. Yaygın olarak kullanılan K-Fold yönteminde, veri seti belirlenen parça sayısı kadar bölünür ve her iterasyonda farklı bir parça test seti yapılarak elde edilen performans skorlarının ortalaması alınır. Zaman faktörünün önemli olduğu tarım projeleri gibi çalışmalarda ise, zaman eksenindeki kronolojik sıralamayı bozmayan zaman serisi çapraz doğrulama (Time Series Cross Validation) yöntemi tercih edilmelidir. Modeli değerlendirirken sulama miktarı tahmini gibi regresyon görevlerinde mutlak ve karesel hataları ölçen MAE, RMSE veya R² metriklerine bakılır. Sulama gerekip gerekmediğine karar verilen sınıflandırma problemlerinde ise performans; accuracy, precision, recall ve F1-score gibi metriklerle ölçülmektedir.

__ÇALIŞMA DOSYALARI__

[Model Validasyonu Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/feature/model-validasyonu)

### Cihan Akalın: Hiperparametre Optimizasyonu
Hiperparametre optimizasyonu, makine öğrenmesi modellerinin veriden otomatik olarak öğrenemediği ve dışarıdan manuel olarak ayarlanan yapılandırma değerlerinin en iyi kombinasyonunu bulma sürecidir. Bu süreçte modelin öğrenme oranı (learning rate), karar ağacı derinliği veya ağaç sayısı gibi performans üzerinde doğrudan etkili olan kritik parametreler belirlenir. Yaygın olarak kullanılan Grid Search yöntemi, tanımlanan parametre değerlerinin tüm olası kombinasyonlarını sistematik olarak deneyerek kesin, ancak hesaplama maliyeti yüksek bir arama yapar. Daha büyük arama uzaylarında zaman tasarrufu sağlamak amacıyla, parametre kombinasyonlarını rastgele test eden Random Search yöntemi genellikle çok daha hızlı ve etkili sonuçlar sunar. Gelişmiş bir yöntem olan Bayes Optimizasyonu (Bayesian Optimization) ise önceki denemelerin sonuçlarını rehber alarak arama sürecini daha akıllıca yönlendirir. Başarılı bir hiperparametre optimizasyonu, hem modelin performans metriklerini üst düzeye çıkarır hem de aşırı öğrenme (overfitting) gibi kritik problemlerin engellenmesine yardımcı olur.

__ÇALIŞMA DOSYALARI__

[Sistem gereksinimleri Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/SISTEM_GEREKSINIMLERI.txt)

[requirements Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/requirements.txt)

[core/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/core)

[visualization/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/visualization)

[scripts/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/scripts)

### Zehra Özdemir: Model Açıklanabilirliği
Model açıklanabilirliği (XAI), karmaşık makine öğrenmesi algoritmalarının nasıl karar verdiğini ve hangi özelliklerin bu kararları etkilediğini şeffaf hale getiren teknikler bütünüdür. Sıklıkla "kara kutu" olarak adlandırılan karmaşık modellerin ürettiği sonuçların arkasındaki mantığı anlamak, tarım yönetimi gibi kritik sistemlere duyulan güveni artırır. SHAP (SHapley Additive exPlanations) yöntemi, oyun teorisine dayanarak her bir değişkenin modelin tahmini üzerindeki olumlu veya olumsuz etkisini detaylı bir şekilde hesaplar. LIME (Local Interpretable Model-agnostic Explanations) tekniği ise, spesifik bir veri noktasındaki tahmini açıklamak için o veri etrafında basit ve yorumlanabilir yerel bir model oluşturur. Özellik önem dereceleri (Feature Importance) analizleri, modelin bir karara varırken sıcaklık, toprak nemi veya yağış gibi verilerden hangilerine en çok ağırlık verdiğini genel bir bakışla ortaya koyar. Bu teknikler sayesinde, hem modelin yaptığı potansiyel hatalar daha hızlı tespit edilip düzeltilebilir hem de alınan kararların mantıksal dayanakları son kullanıcılara anlaşılır bir şekilde sunulabilir.

__ÇALIŞMA DOSYALARI__

[MODEL_ACIKLANABILIRLIGI.md Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/MODEL_ACIKLANABILIRLIGI.md)

### Şevval Yıldız: Model Seçimi ve Eğitimi
Model seçimi ve eğitimi, problemin doğasına en uygun makine öğrenmesi algoritmalarının belirlenip mevcut verilerle öğretilmesi sürecidir. Tarımsal verimlilik veya sulama tahmini gibi regresyon ve sınıflandırma problemlerinde genellikle Random Forest, XGBoost veya destek vektör makineleri (SVM) gibi güçlü algoritmalar tercih edilir. Seçilen bu algoritmalar, ön işlemlerden geçmiş ve özellik mühendisliği ile zenginleştirilmiş eğitim veri setleri kullanılarak eğitilir. Eğitim aşamasında model, veri setindeki çevresel girdiler ile hedeflenen sonuçlar arasındaki karmaşık matematiksel örüntüleri algılamaya ve öğrenmeye çalışır. Aşırı öğrenmeyi (overfitting) engellemek amacıyla eğitim süreci, çapraz doğrulama teknikleri ve düzenlileştirme (regularization) parametreleri ile dikkatlice kontrol edilir. Eğitim tamamlandığında, modelin daha önce hiç karşılaşmadığı test verileri üzerindeki performansı ölçülerek en yüksek doğruluk oranına sahip olan algoritma ana model olarak konumlandırılır.

__ÇALIŞMA DOSYALARI__

[Model Seçimi ve Eğitimi Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/%C5%9Eevval/Hafta6_Model_Egitimi_Raporu.pdf)

### Muhammed Cengiz:

### Abdulrahman Shawa:

## 5. Hafta (1 Haziran - 7 Haziran)

### Yiğit Alper Ayhan (Scrum Master / Yönetici): Model Entegrasyonu
Model entegrasyonu, eğitilmiş makine öğrenmesi algoritmalarını gerçek zamanlı sensör verileriyle çalışacak şekilde canlı sistemlere dahil etme sürecidir. Bu süreçte modelin Django backend'i içine doğrudan gömülmesi yerine, ölçeklenebilirliği ve performansı artıran ayrı bir mikroservis (API) olarak çalıştırılması profesyonel bir yaklaşım olarak önerilir. IoT cihazlarından MQTT protokolü ile anlık olarak alınan veriler, veri tabanına kaydedilmeden hemen önce model tarafından işlenerek otomatik tahminlerin üretilmesini sağlar. Gerçek zamanlı verilerin işlenmesinde, eğitim aşamasında kullanılan ön işleme (preprocessing) yöntemlerinin tamamen aynı kalmasını sağlayan standartlaştırılmış veri boru hatları (pipeline) kullanılır. Modelin ürettiği sulama tahminleri ve temel sensör değerleri PostgreSQL veritabanında saklanarak, kullanıcı panosu (dashboard) üzerinden grafikler ve uyarı bildirimleri halinde görselleştirilir. Ayrıca, sistemin sürekli yüksek doğrulukla çalışması için arka planda planlanmış görevler yardımıyla modelin yeni verilerle düzenli aralıklarla yeniden eğitilmesi (retraining) sağlanır.

__ÇALIŞMA DOSYALARI__

[Model Entegrasyonu Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/feature/model-entegrasyonu)

### Cihan Akalın: Model Kalibrasyonu
Model kalibrasyonu, bir makine öğrenmesi modelinin ürettiği tahmin olasılıklarının, gerçek hayattaki gerçekleşme olasılıklarını doğru bir şekilde yansıtmasını sağlayan kritik bir süreçtir. Eğer bir model bir bitkinin %80 olasılıkla sulanması gerektiğini tahmin ediyorsa, mükemmel kalibre edilmiş bir sistemde benzer vakaların tam olarak %80'inde gerçekten sulama yapılması beklenir. Random Forest, SVM veya bazı derin öğrenme algoritmaları oldukça yüksek doğrulukla sınıflandırma yapsalar da, ürettikleri ham olasılık skorları çoğunlukla güvenilmez ve kalibresizdir. Bu uyumsuzluğu gidermek için, modelin ürettiği ham tahmin değerlerini gerçek olasılık dağılımlarına dönüştüren Platt Scaling veya Isotonic Regression gibi yaygın teknikler kullanılır. Aşırı öğrenmeyi engellemek amacıyla, kalibrasyon işlemi modelin eğitimi sırasında görmediği ayrı bir validasyon veri seti üzerinde titizlikle uygulanmalıdır. Başarılı bir şekilde kalibre edilmiş olasılık tahminleri, akıllı tarım sistemlerinde hem gereksiz kaynak tüketimini önler hem de alınacak otonom kararların güvenilirliğini en üst düzeye çıkarır.

__ÇALIŞMA DOSYALARI__

[core/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/core)

[scripts/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Cihan/scripts)

[requirements.txt Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Cihan/requirements.txt)

### Zehra Özdemir: Sonuçların Raporlanması
Model sonuçlarının raporlanması, geliştirilen makine öğrenmesi algoritmalarının sahadaki başarısını ve verimliliğini paydaşlara şeffaf bir şekilde sunma sürecidir. Ayrıntılı bir rapor oluşturulurken, modelin doğruluk oranlarıyla birlikte sistemin aşırı veya eksik sulama gibi temel tarımsal sorunları ne ölçüde çözdüğü özellikle vurgulanmalıdır. Üretilen tahminler ve analiz edilen IoT sensör verileri, doğrudan bir son kullanıcı gösterge paneli (dashboard) üzerine aktarılarak canlı veriler eşliğinde görselleştirilir. Hazırlanan raporda, zaman içindeki toprak nemi değişimleri ve haftalık su tüketim miktarları gibi önemli metrikler grafiklerle desteklenerek anlaşılır bir biçimde sunulmalıdır. Ayrıca, sistemin mevcut çevresel koşullara göre ürettiği otonom uyarılar da raporun aksiyona dönüşen en kritik parçasını oluşturur. Başarılı bir şekilde tasarlanan bu raporlama yapısı, hem teknik olmayan son kullanıcıların (çiftçilerin) karmaşık verileri kolayca yorumlamasını sağlar hem de projenin sağladığı faydayı somutlaştırır.

__ÇALIŞMA DOSYALARI__

[SONUC_RAPORU.md Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/Zehra/SONUC_RAPORU.md)

### Şevval Yıldız: Model İyileştirme
Model iyileştirme, makine öğrenmesi sistemlerinde elde edilen başlangıç performansını daha yüksek doğruluk ve kararlılık seviyelerine taşımak için yürütülen tekrarlı bir süreçtir. Bu süreçteki en etkili yöntemlerden biri, mevcut ham verilerden hareketli ortalamalar veya bütünleşik bitki stres indeksleri gibi hedef değişkeni daha iyi açıklayan yeni özelliklerin türetilmesidir. Sadece yeni özellikler eklemekle kalmayıp, algoritmanın kafasını karıştıran ve gürültü yaratan önemsiz verilerin ayıklanması (feature selection) da model başarısını ciddi şekilde artırır. Temel algoritmaların sınırlarına ulaşıldığında, XGBoost veya LightGBM gibi daha karmaşık ve gelişmiş mimarilere sahip algoritmalar denenerek performans iyileştirilir. Ayrıca birden fazla modelin tahminlerini birleştiren topluluk (ensemble) öğrenme yöntemleri kullanılarak sistemin zayıf yönleri dengelenir ve daha kararlı bir yapı elde edilir. Yapılan tüm bu yapısal değişikliklerin ve özellik mühendisliği adımlarının başarısı, çapraz doğrulama testleriyle ölçülerek modelin gerçek hayattaki genelleme yeteneğinin arttığı teyit edilir.

__ÇALIŞMA DOSYALARI__

[Model İyileştirme Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/%C5%9Eevval/Hafta7_Model_Iyilesitirme_Raporu.pdf)

### Muhammed Cengiz: Hata Analizi
Hata analizi, makine öğrenmesi modelinin test verisi üzerinde gerçekleştirdiği yanlış tahminleri sistematik olarak inceleyerek bu hataların temel nedenlerini keşfetme sürecidir. Bu aşamada karmaşıklık matrisi (confusion matrix) gibi araçlar kullanılarak, örneğin sistemin sulama gerekmeyen durumlarda neden "sulama gerekli" kararı verdiği (False Positive) detaylıca saptanır. Bu hataların altında yatan başlıca nedenler arasında arızalı sensörlerden gelen gürültülü veriler, sınıflar arası dengesizlikler veya modelin ani don gibi ekstrem hava koşullarını yeterince öğrenmemiş olması bulunur. Yanlış sınıflandırılan örnekler incelendiğinde, modelin belirli özelliklere aşırı odaklanıp bazı kritik eşikleri (örneğin yağış sonrası toprak nemi gecikmesi) gözden kaçırdığı gibi yapısal kör noktalar açığa çıkar. Elde edilen bulgular, eğitim veri setinin nasıl zenginleştirilmesi gerektiğine, özellik mühendisliği aşamasında hangi adımların atılacağına ve hiperparametrelerin ne yönde güncelleneceğine doğrudan rehberlik eder. Düzenli olarak uygulanan detaylı bir hata analizi, modelin zayıf yönlerini onararak tarımsal otomasyon süreçlerindeki tahmin doğruluğunu ve sistem güvenilirliğini sürekli olarak yukarı taşır.

[backend/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/backend)

[frontend/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/frontend)

[docs/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/docs)

[simulator/ Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Muhammed/simulator)

### Abdulrahman Shawa:

## 6. Hafta (8 Haziran - 14 Haziran)

### Yiğit Alper Ayhan (Scrum Master / Yönetici): Final Sunum Hazırlığı
Akıllı Tarım Yönetim Sistemi projesinin final sunumu, geleneksel tarımdaki aşırı sulama ve verimsiz kaynak kullanımı gibi temel problemleri vurgulayarak başlar. Çözüm aşamasında, IoT sensörlerinden elde edilen anlık çevresel verilerin makine öğrenmesi algoritmalarıyla nasıl gerçek zamanlı analiz edildiği katılımcılara açıklanır. Sistemin arka planındaki teknik mimariyi göstermek amacıyla Python, Django, PostgreSQL ve MQTT gibi kullanılan modern teknolojiler görsel bir yapı içinde sunulur. Katılımcıların sonuçları daha rahat kavraması için, zaman içerisindeki toprak nemi trendlerini ve günlük su tüketim miktarlarını detaylandıran net çizgi ve çubuk grafikler oluşturulmuştur. Ayrıca, projenin son kullanıcı deneyimini sergilemek adına anlık sıcaklık, hava nemi oranları ve otomatik sulama uyarılarını barındıran örnek bir "dashboard" arayüzü sunuma dahil edilir. Görsel materyallerle desteklenen bu profesyonel sunum, sadece teknik başarıları anlatmakla kalmaz, projenin tarlada sağladığı somut su tasarrufunu ve verimlilik artışını da etkili biçimde kanıtlar.

__ÇALIŞMA DOSYALARI__

[Final Sunum Hazırlığı Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/feature/final-sunum-haz%C4%B1rl%C4%B1%C4%9F%C4%B1)

### Cihan Akalın:

### Zehra Özdemir: Sunum Provası ve Geri Bildirim
Akıllı Tarım Yönetim Sistemi projesinin tamamlanmasının ardından, paydaşlara ve yatırımcılara yapılacak olan final sunumunun hazırlıkları için kapsamlı bir genel prova gerçekleştirilecektir. Bu prova oturumu sırasında; projenin teknik mimarisi, IoT sensör entegrasyon süreçleri ve sistemin sağladığı tarımsal faydalar belirlenen süre sınırlarına katı bir şekilde uyularak anlatılacaktır. Sunum esnasında kullanılacak veri görselleştirmelerinin, akış diyagramlarının ve arayüz prototiplerinin izleyiciler üzerindeki etkisi ve anlaşılırlığı detaylıca test edilecektir. Prova sunumunun hemen ardından tüm proje ekibi bir değerlendirme toplantısında bir araya gelerek, anlatım akıcılığı ve içerik vurguları gibi konularda yapıcı geri bildirimlerde bulunacaktır. Ekip üyelerinden toplanan bu değerli değerlendirmeler doğrultusunda, sunumdaki karmaşık teknik detayların daha sade ifade edilmesi gibi gerekli son iyileştirmeler hızla yapılacaktır. Gerçekleştirilen bu titiz prova ve geri bildirim döngüsü sayesinde, projenin yenilikçi vizyonunun hedef kitleye en profesyonel ve ikna edici şekilde aktarılması güvence altına alınacaktır.

__ÇALIŞMA DOSYALARI__

[Sunum Provası ve Geri Bildirim Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/tree/dev/Zehra)

### Şevval Yıldız: Proje Tamamlama ve Test
__1.__ Akıllı Tarım Yönetim Sistemi projesinin tüm tasarım aşamaları ve teorik bileşenleri modüler Python backend yapısı altında eksiksiz olarak kodlanmıştır.

__2.__ Geliştirilen veri temizleme modülü ile IoT sensörlerinden gelen fiziksel sınır dışı ve istatistiksel aykırı verilerin elenmesi ile eksik değerlerin doldurulması başarıyla sağlanmaktadır.

__3.__ Özellik mühendisliği modülü sayesinde ham sensör verilerinden sıcaklık değişimleri, hareketli ortalamalar, bitki stres indeksi ve olası anomali durumları otomatik olarak türetilmektedir.

__4.__ Makine öğrenmesi modeli olarak entegre edilen rastgele orman algoritması, zaman serisi çapraz doğrulama yöntemiyle test edilerek yüksek başarıyla valide edilmiştir.

__5.__ Kurulan uçtan uca çıkarım boru hattı ve MQTT simülasyonu sayesinde akan anlık sensör verilerine göre sulama tahminleri ve stres skorları gerçek zamanlı üretilmektedir.

__6.__ Sistem genelindeki tüm preprocessing, makine öğrenmesi ve veri akış adımları, hazırlanan kapsamlı otomatik test paketiyle tam başarıyla doğrulanmıştır.

__ÇALIŞMA DOSYALARI__

[Proje Tamamlama ve Test Link](https://github.com/yalper02/Akilli-Tarim-Yonetim-Sistemi/blob/dev/%C5%9Eevval/Hafta8_Proje_Tamamlama_ve_Test.pdf)

### Muhammed Cengiz:

### Abdulrahman Shawa: