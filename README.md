# 🛒 E-Commerce Analytics Pipeline

Gerçek zamanlı sipariş toplama ve analiz pipeline'ı. FastAPI tabanlı bir sipariş simülatöründen gelen verileri Redis kuyruğu üzerinden işleyip PostgreSQL'e kaydeden, ardından Metabase ile görselleştiren tam yığın bir veri mühendisliği projesidir.

---

## 🏗️ Mimari

```
┌──────────────────┐      POST /siparis      ┌──────────────────┐
│   Web Arayüzü    │ ──────────────────────► │   FastAPI (API)  │
│  (index.html)    │                         │   :8000          │
└──────────────────┘                         └────────┬─────────┘
                                                      │ rpush
                                                      ▼
                                             ┌──────────────────┐
                                             │   Redis Kuyruğu  │
                                             │  siparis_havuzu  │
                                             └────────┬─────────┘
                                                      │ blpop
                                                      ▼
                                             ┌──────────────────┐
                                             │   Data Worker    │
                                             │   (Python)       │
                                             └────────┬─────────┘
                                                      │ INSERT
                                                      ▼
                                             ┌──────────────────┐      ┌──────────────────┐
                                             │   PostgreSQL DB  │ ◄──► │    Metabase BI   │
                                             │  sirket_analiz   │      │    :3000         │
                                             └──────────────────┘      └──────────────────┘
```

---

## 🧩 Servisler

| Servis | Teknoloji | Port | Açıklama |
|---|---|---|---|
| `web_api` | FastAPI + Uvicorn | 8000 | Sipariş alma API'si ve web arayüzü |
| `data_worker` | Python | — | Redis kuyruğunu dinler, DB'ye yazar |
| `redis_kuyruk` | Redis 7 | — | Sipariş mesaj kuyruğu |
| `analiz_db` | PostgreSQL 15 | 5432 | Kalıcı veri deposu |
| `metabase-bi` | Metabase | 3000 | BI görselleştirme paneli |

---

## 📁 Proje Yapısı

```
ecommerce-analytics-pipeline/
│
├── docker-compose.yml          # Tüm servislerin orkestrasyonu
├── .env                        # Ortam değişkenleri (DB bilgileri)
├── .gitignore
│
├── db_init/
│   └── 01-init.sql             # PostgreSQL başlangıç şeması
│
├── web_api/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI uygulaması
│   ├── index.html              # Sipariş simülatörü arayüzü
│   └── requirements.txt
│
└── data_worker/
    ├── Dockerfile
    ├── worker.py               # Kuyruk tüketici worker
    └── requirements.txt
```

---

## ⚙️ Nasıl Çalışır?

### 1. Sipariş Alma (`web_api`)
- Kullanıcı tarayıcıda `http://localhost:8000` adresine gider.
- Ürün kartlarından birine (Bilgisayar, Telefon, Tablet) tıklar.
- FastAPI `/siparis` endpoint'i siparişi JSON olarak Redis'e (`siparis_havuzu` listesi) kuyruğa ekler.

### 2. Kuyruk İşleme (`data_worker`)
- Worker, `BLPOP` komutuyla `siparis_havuzu` kuyruğunu sürekli dinler.
- Kuyruktan gelen her siparişi işler: `toplam_tutar = fiyat × adet`
- İşlenen veriyi PostgreSQL'deki `siparisler` tablosuna kaydeder.

### 3. Analiz (`metabase-bi`)
- Metabase, `http://localhost:3000` adresinde PostgreSQL'e bağlanır.
- `siparisler` tablosu üzerinde dashboard ve grafikler oluşturulabilir.

---

## 🗄️ Veritabanı Şeması

```sql
CREATE TABLE siparisler (
    id              SERIAL PRIMARY KEY,
    urun_adi        VARCHAR(255)   NOT NULL,
    kategori        VARCHAR(255)   NOT NULL,
    fiyat           NUMERIC(10,2)  NOT NULL,
    adet            INT            NOT NULL,
    toplam_tutar    NUMERIC(10,2)  NOT NULL,
    olusturma_tarihi TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- [Docker](https://www.docker.com/) ve Docker Compose

### 1. Repoyu klonla
```bash
git clone <repo-url>
cd ecommerce-analytics-pipeline
```

### 2. `.env` dosyasını oluştur
`.env.example` dosyasını kopyalayıp kendi değerlerinle doldur:
```bash
cp .env.example .env
```
Ardından `.env` dosyasını düzenle:
```env
DB_USER=guclu_bir_kullanici
DB_PASSWORD=guclu_bir_sifre
DB_NAME=sirket_analiz
DB_HOST=analiz_db
```
> ⚠️ `.env` dosyası `.gitignore`'a eklidir — asla GitHub'a gitmez.

### 3. Tüm servisleri başlat
```bash
docker compose up --build
```

### 4. Servislere eriş

| Adres | Servis |
|---|---|
| http://localhost:8000 | Sipariş Simülatörü (Web Arayüzü) |
| http://localhost:8000/docs | FastAPI Swagger Dokümantasyonu |
| http://localhost:3000 | Metabase BI Paneli |
| localhost:5432 | PostgreSQL (DBeaver vb. ile bağlan) |

---

## 🔌 API Referansı

### `POST /siparis`
Yeni bir sipariş oluşturur ve Redis kuyruğuna ekler.

**Query Parametreleri:**

| Parametre | Tip | Açıklama |
|---|---|---|
| `urun` | string | Ürün adı |
| `kategori` | string | Ürün kategorisi |
| `fiyat` | float | Birim fiyat (TL) |
| `adet` | int | Sipariş adedi |

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/siparis?urun=Bilgisayar&kategori=Teknoloji&fiyat=45000&adet=1"
```

**Başarılı Yanıt:**
```json
{
  "durum": "Basarili",
  "mesaj": "Bilgisayar siparisi alindi ve siraya eklendi"
}
```

---

## 🛠️ Kullanılan Teknolojiler

- **[FastAPI](https://fastapi.tiangolo.com/)** — Modern, hızlı Python web framework
- **[Redis](https://redis.io/)** — In-memory mesaj kuyruğu
- **[PostgreSQL](https://www.postgresql.org/)** — İlişkisel veritabanı
- **[Metabase](https://www.metabase.com/)** — Açık kaynak BI ve analitik platformu
- **[Docker Compose](https://docs.docker.com/compose/)** — Çoklu konteyner orkestrasyonu

---

## 📊 Örnek Kullanım Senaryosu

1. `docker compose up --build` ile sistemi ayağa kaldır
2. `http://localhost:8000` adresine git
3. Ürün kartlarına tıklayarak test siparişleri ver
4. Worker loglarından siparişlerin işlendiğini gözlemle:
   ```
   Yeni Siparis isleniyor: 1 adet Bilgisayar. Toplam: 45000.0 TL
   ✔ Bilgisayar siparişi depoya başarıyla kaydedildi.
   ```
5. `http://localhost:3000` Metabase'de veriyi analiz et

---

## 📝 Notlar

- İlk açılışta Metabase kurulum sihirbazını tamamlaman gerekir.
- PostgreSQL bağlantı bilgileri `.env` dosyasından okunur; production ortamında güçlü şifreler kullan.
- `data_worker`, veritabanı hazır olana kadar 3 saniyede bir yeniden bağlanmayı dener.
