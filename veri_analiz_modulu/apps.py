from django.apps import AppConfig


class VeriAnalizModuluConfig(AppConfig):
    """
    Veri Toplama ve Analiz Modülü Django App Konfigürasyonu.
    
    Bu modül, IoT sensörlerinden gelen tarımsal verileri toplar,
    istatistiksel analiz ve makine öğrenmesi algoritmaları ile işler,
    ve sonuçları görselleştirir.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'veri_analiz_modulu'
    verbose_name = 'Veri Toplama ve Analiz Modülü'

    def ready(self):
        """Uygulama başlatıldığında çalışacak kodlar."""
        import veri_analiz_modulu.signals  # noqa: F401
