import os 
import time
import json
from redis import Redis
import psycopg2
import sys

print("data worker calisiyor", flush=True)

kuyruk = Redis(host="redis_kuyruk", port=6379, decode_responses=True)

while True:
    try:
        db = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor = db.cursor()
        print("veritabani baglantisi kuruldu", flush=True)
        break
    except psycopg2.OperationalError as e:
        print(f"Veritabani hazir degil Hata: {e}", flush=True)
        time.sleep(3)

while True:
    ham_siparis = kuyruk.blpop("siparis_havuzu", timeout=0)
    
    if ham_siparis:
        siparis = json.loads(ham_siparis[1])
        
        urun = siparis["urun_adi"]
        kategori = siparis["kategori"]
        fiyat = float(siparis["fiyat"])
        adet = int(siparis["adet"])
        toplam_tutar = fiyat * adet
        
        print(f"Yeni Siparis isleniyor: {adet} adet {urun}. Toplam: {toplam_tutar} TL", flush=True)
        
        try:
            sql = """
                INSERT INTO siparisler (urun_adi, kategori, fiyata, adet, toplam_tutar)
                VALUES (%s, %s, %s, %s, %s);
            """
            
            sql = sql.replace("fiyata", "fiyat") 
            cursor.execute(sql, (urun, kategori, fiyat, adet, toplam_tutar))
            db.commit()
            print(f"✔ {urun} siparişi depoya başarıyla kaydedildi.", flush=True)
        except Exception as e:
            print(f"❌ Veritabanına yazarken hata oluştu: {e}", flush=True)
            db.rollback()