import json
from fastapi import FastAPI
from redis import Redis
from fastapi.responses import HTMLResponse

app = FastAPI()

kuyruk = Redis(host="redis_kuyruk", port=6379, decode_responses=True)

@app.get("/", response_class=HTMLResponse)
def ana_sayfa():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/siparis")
def siparis_al(urun: str, kategori: str, fiyat: float, adet: int):
    siparis_verisi = {
        "urun_adi": urun,
        "kategori": kategori,
        "fiyat": fiyat,
        "adet": adet
    }
    kuyruk.rpush("siparis_havuzu", json.dumps(siparis_verisi))
    return {"durum": "Basarili", "mesaj": f"{urun} siparisi alindi ve siraya eklendi"}

