CREATE TABLE IF NOT EXISTS siparisler (
    id SERIAL PRIMARY KEY,
    urun_adi VARCHAR(255) NOT NULL,
    kategori VARCHAR(255) NOT NULL,
    fiyat NUMERIC(10, 2) NOT NULL,
    adet INT NOT NULL,
    toplam_tutar NUMERIC(10, 2) NOT NULL,
    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);