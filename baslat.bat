@echo off
color 0b
echo ==========================================
echo    ATYS KOMUTA MERKEZI BASLATILIYOR...
echo ==========================================

:: 1. Terminal: Web Arayüzü (Dashboard)
start "Django Server" cmd /k "python manage.py runserver"

:: 2. Terminal: MQTT Veri İşleyici (Asenkron Köprü)
start "MQTT Worker" cmd /k "python scripts/mqtt_worker.py"

:: 3. Terminal: Telegram Botu (Alarm Sistemi)
start "Telegram Bot" cmd /k "python scripts/telegram_bot.py"

:: 4. Terminal: Sensör Simülatörü (Dinamik Veri Akışı)
echo Sensor simulatoru 5 saniye icinde devreye girecek...
timeout /t 5 >nul
start "Sensor Simulator" cmd /k "python scripts/simulate_sensors.py"

echo.
echo [+] Tüm servisler başarıyla tetiklendi!
echo [+] Dashboard: http://127.0.0.1:8000/dashboard/
echo.
pause