Gerçek zamanlı sipariş toplama ve analiz pipeline'ı. FastAPI tabanlı bir sipariş simülatöründen gelen verileri Redis kuyruğu üzerinden işleyip PostgreSQL'e kaydeden, ardından Metabase ile görselleştiren tam yığın bir veri mühendisliği projesidir.

---

##  Mimari

```
[ Web Arayüzü ]
       │
       │ POST /siparis
       ▼
[ FastAPI - :8000 ]
       │
       │ rpush
       ▼
[ Redis Kuyruğu ]
       │
       │ blpop
       ▼
[ Data Worker (Python) ]
       │
       │ INSERT
       ▼
[ PostgreSQL DB ] <────> [ Metabase BI - :3000 ]
```

---

---

##  Nasıl Çalışır?

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

## 🛠️ Kullanılan Teknolojiler

- **[FastAPI](https://fastapi.tiangolo.com/)** — Modern, hızlı Python web framework
- **[Redis](https://redis.io/)** — In-memory mesaj kuyruğu
- **[PostgreSQL](https://www.postgresql.org/)** — İlişkisel veritabanı
- **[Metabase](https://www.metabase.com/)** — Açık kaynak BI ve analitik platformu
- **[Docker Compose](https://docs.docker.com/compose/)** — Çoklu konteyner orkestrasyonu

---

##  Notlar
- `data_worker`, veritabanı hazır olana kadar 3 saniyede bir yeniden bağlanmayı dener.
