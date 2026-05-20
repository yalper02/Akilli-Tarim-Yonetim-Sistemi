import os
import json
import sqlite3
from datetime import datetime

# =========================================================
# Proje Yönetim Aracı - Kurulum ve Konfigürasyon Simülasyonu
# =========================================================

CONFIG_FILE = "pm_config.json"
DB_FILE = "pm_tool.db"

def setup_configuration():
    """1. Adım: Sistemin temel konfigürasyon dosyasını oluşturma"""
    print(">>> 1. Konfigürasyon dosyası ayarlanıyor...")
    
    config_data = {
        "system_name": "Akıllı Tarım Proje Yönetim Sistemi",
        "version": "1.0.0",
        "admin_email": "admin@akillitarim.local",
        "database_path": DB_FILE,
        "features_enabled": {
            "task_tracking": True,
            "time_logging": True,
            "agile_boards": True,
            "notifications": False
        }
    }
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)
        
    print(f"    - {CONFIG_FILE} başarıyla oluşturuldu.\n")
    return config_data


def setup_database(db_path):
    """2. Adım: Veritabanı tablolarını ve ilişkileri kurma"""
    print(f">>> 2. Veritabanı ({db_path}) başlatılıyor...")
    
    # Eğer eski bir DB varsa temizleyerek temiz kurulum simüle edelim
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Projeler tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    # Görevler (Tasks) tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        title TEXT NOT NULL,
        assigned_to INTEGER,
        status TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (assigned_to) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    print("    - Veritabanı tabloları (users, projects, tasks) başarıyla oluşturuldu.\n")
    return conn

def insert_initial_data(conn):
    """3. Adım: Sistem konfigüre edildikten sonra örnek verilerin girilmesi"""
    print(">>> 3. Başlangıç (Örnek) verileri sisteme yükleniyor...")
    cursor = conn.cursor()
    
    # Kullanıcı Ekleme
    users = [
        ('ahmet_yilmaz', 'Admin'),
        ('ayse_kaya', 'Developer'),
        ('mehmet_demir', 'Tester')
    ]
    cursor.executemany("INSERT INTO users (username, role) VALUES (?, ?)", users)
    
    # Proje Ekleme
    projects = [
        ('Akıllı Sulama Otomasyonu', 'Active'),
        ('Sensör Veri Analizi Arayüzü', 'Planning')
    ]
    cursor.executemany("INSERT INTO projects (name, status) VALUES (?, ?)", projects)
    
    # Görev Ekleme
    tasks = [
        (1, 'Toprak nem sensörleri entegrasyonu', 2, 'In Progress'),
        (1, 'Sulama motoru röle kontrolü', 2, 'To Do'),
        (2, 'Dashboard arayüzü tasarımı', 3, 'To Do')
    ]
    cursor.executemany("INSERT INTO tasks (project_id, title, assigned_to, status) VALUES (?, ?, ?, ?)", tasks)
    
    conn.commit()
    print("    - Örnek kullanıcılar, projeler ve görevler eklendi.\n")


def display_system_status(conn):
    """4. Adım: Kurulum sonrası sistem durumunu raporlama"""
    print(">>> 4. Sistem Kurulum Özeti ve Raporu:")
    cursor = conn.cursor()
    
    print("\n--- Aktif Kullanıcılar ---")
    cursor.execute("SELECT id, username, role FROM users")
    for row in cursor.fetchall():
        print(f"[{row[0]}] {row[1]} (Rol: {row[2]})")
        
    print("\n--- Projeler ve Görevler ---")
    cursor.execute("SELECT id, name, status FROM projects")
    for proj in cursor.fetchall():
        print(f"Proje: {proj[1]} [{proj[2]}]")
        cursor.execute("SELECT title, status, assigned_to FROM tasks WHERE project_id=?", (proj[0],))
        for task in cursor.fetchall():
            assigned_user = cursor.execute("SELECT username FROM users WHERE id=?", (task[2],)).fetchone()[0]
            print(f"   -> Görev: {task[0]} | Durum: {task[1]} | Atanan: {assigned_user}")
            
    print("\n=========================================================")
    print(f"Kurulum başarıyla tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=========================================================\n")


if __name__ == "__main__":
    print("=== PROJE YÖNETİM ARACI KURULUM VE KONFİGÜRASYON BAŞLATILIYOR ===\n")
    
    # 1. Konfigürasyon oluştur
    config = setup_configuration()
    
    # 2. Veritabanını kur
    db_conn = setup_database(config['database_path'])
    
    # 3. Örnek verileri gir
    insert_initial_data(db_conn)
    
    # 4. Durumu göster
    display_system_status(db_conn)
    
    # Kaynakları serbest bırak
    db_conn.close()
