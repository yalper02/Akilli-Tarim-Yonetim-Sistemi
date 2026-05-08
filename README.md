# Akıllı Tarım Yönetim Sistemi

IoT sensörlerden gelen toprak nemi, sıcaklık, pH ve NPK verilerini kullanarak sulama ve gübreleme kararlarını optimize eden akıllı tarım yönetim sistemi.

## Özellikler

- Gerçek zamanlı sensör verisi izleme (MQTT + WebSocket)
- Otomatik sulama kuralları ve hava durumu entegrasyonu
- Haftalık gübreleme önerileri
- Makine öğrenmesi tabanlı verim tahminleri
- Rol tabanlı erişim (çiftçi, tarım yöneticisi, sistem yöneticisi)
- CSV / Excel dışa aktarma

## Teknoloji Yığını

| Katman | Teknolojiler |
|---|---|
| Backend | Python 3.11, Django 5, DRF, Django Channels, Celery |
| Veritabanı | TimescaleDB (PostgreSQL), Redis |
| Mesajlaşma | Mosquitto MQTT broker, paho-mqtt |
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Altyapı | Docker Compose |

## Ön Koşullar

| Araç | Minimum Sürüm |
|---|---|
| Docker Desktop | 24.x |
| Docker Compose | 2.x (Docker Desktop ile gelir) |
| Poetry | 1.8.x |
| Node.js | 20.x LTS |
| Python | 3.11+ |

## Hızlı Başlangıç

### 1. Repoyu klonla

```bash
git clone <repo-url>
cd akilli-tarim-yonetim
```

### 2. Ortam değişkenlerini ayarla

```bash
cp .env.example .env
# .env dosyasını düzenle — geliştirme için varsayılanlar çalışır
```

### 3. Altyapıyı başlat (TimescaleDB, Redis, Mosquitto)

```bash
docker compose up -d db redis mosquitto
```

### 4. Backend'i başlat

```bash
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### 5. Frontend'i başlat

```bash
cd frontend
npm install
npm run dev
```

### 6. Sensör simülatörünü başlat

```bash
cd simulator
poetry install
poetry run python simulator.py
```

### Tek komutla tamamını başlat (tüm servisler Docker ile)

```bash
docker compose up
```

Arayüze `http://localhost:3000` adresinden ulaşabilirsiniz.
API dökümanı için: `http://localhost:8000/api/schema/swagger-ui/`

## Proje Yapısı

```
akilli-tarim-yonetim/
├── backend/        # Django + DRF + Channels + Celery
├── frontend/       # Next.js 15 App Router
├── simulator/      # Python sensör simülatörü
├── docker/         # Mosquitto, TimescaleDB, Nginx konfigürasyonları
└── docs/           # API referansı, MQTT yapısı, sunum notları
```

Mimari kararlar ve detaylı tasarım için `CLAUDE.md` dosyasına bakın.

## Geliştirici Notları

- `CLAUDE.md` — değişmez mimari referans (dokunma)
- `TODO.md` — yaşayan ilerleme defteri
- Kod dili: İngilizce; UI dili: Türkçe
- Pre-commit hook'ları: Black + Ruff (backend), Prettier + ESLint (frontend)

## Lisans

Okul projesi — Fırat Üniversitesi, 2026
