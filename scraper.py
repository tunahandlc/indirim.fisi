"""
İndirim Fişi — Otomatik İndirim Tarayıcı
==========================================
Her mağazanın kendi "Kampanyalar / İndirimli Ürünler" sayfasını tarar,
1 Ağustos 2026 yönetmeliğiyle zorunlu hale gelen "son 10 günün en düşük
fiyatı" referansına göre GERÇEK indirim yüzdesini hesaplar, eşiği (varsayılan
%25) geçenleri deals.json dosyasına yazar. Bu dosyayı index.html okuyor.

ÖNEMLİ — BEN (Claude) BUNU SENİN YERİNE TEST EDEMEDİM:
Şu an çalıştığım ortamın ağ erişimi Trendyol/N11/Hepsiburada/Amazon'a kapalı,
yani bu siteleri kendim açıp doğrulayamıyorum. Aşağıdaki her STORE bloğunda
"BUL:" yazan 2 şey var — bunları SEN, kendi tarayıcından, 5 dakikada
bulacaksın. Nasıl bulunacağı en alttaki "SEÇİCİLERİ BULMA REHBERİ"nde.

Kurulum (kendi bilgisayarında bir kere dene):
    pip install requests beautifulsoup4
    python scraper.py
"""

import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

MIN_DISCOUNT = 25          # yüzde eşiği — istersen değiştir
REQUEST_DELAY_SECONDS = 3  # siteyi yormamak için istekler arası bekleme
TIMEOUT = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9",
}


@dataclass
class Deal:
    store: str
    name: str
    price: float
    ref_price: float
    url: str
    checked_at: str

    @property
    def discount_pct(self) -> int:
        if self.ref_price <= 0:
            return 0
        return round((self.ref_price - self.price) / self.ref_price * 100)


def parse_price(text: str) -> float:
    """'1.249,00 TL' ya da '1249,00₺' gibi metni 1249.0 sayısına çevirir."""
    cleaned = re.sub(r"[^\d,.]", "", text)
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def scrape_store(store: dict) -> list[Deal]:
    """
    Genel amaçlı tarayıcı: her mağaza için aynı mantığı,
    o mağazanın kendi seçicileriyle çalıştırır.
    """
    deals: list[Deal] = []
    resp = requests.get(store["listing_url"], headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cards = soup.select(store["card_selector"])
    if not cards:
        print(
            f"[{store['name']}] Hiç ürün kartı bulunamadı — sayfa muhtemelen "
            "JavaScript ile yükleniyor (aşağıdaki rehberin 'Yöntem B' kısmına bak) "
            "ya da card_selector artık yanlış."
        )
        return deals

    now = datetime.now(timezone.utc).isoformat()
    for card in cards:
        name_el = card.select_one(store["name_selector"])
        price_el = card.select_one(store["price_selector"])
        ref_el = card.select_one(store["ref_price_selector"])
        link_el = card.select_one(store.get("link_selector", "a"))
        if not (name_el and price_el and ref_el):
            continue

        href = link_el["href"] if (link_el and link_el.has_attr("href")) else ""
        if href and href.startswith("/"):
            href = store["base_url"] + href

        deals.append(
            Deal(
                store=store["name"],
                name=name_el.get_text(strip=True),
                price=parse_price(price_el.get_text()),
                ref_price=parse_price(ref_el.get_text()),
                url=href or store["listing_url"],
                checked_at=now,
            )
        )
    return deals


# ----------------------------------------------------------------------------
# MAĞAZA AYARLARI — "BUL:" yazan yerleri kendi tarayıcından doldur.
# Dördü de aynı desende; ilkini (Trendyol) doldurduktan sonra diğerleri
# aynı yöntemle 5'er dakika sürer.
# ----------------------------------------------------------------------------
STORES = [
    {
        "name": "trendyol",
        "base_url": "https://www.trendyol.com",
        "listing_url": "BUL: Trendyol'da Kampanyalar/İndirimli Ürünler sayfasını aç, URL'yi buraya yapıştır",
        "card_selector": "BUL: bir ürün kutusunu sağ tıkla > İncele, ortak class'ını yaz",
        "name_selector": "BUL: ürün adının class'ı",
        "price_selector": "BUL: şu anki fiyatın class'ı",
        "ref_price_selector": "BUL: üstü çizili / son 10 gün fiyatının class'ı",
        "link_selector": "a",
    },
    {
        "name": "n11",
        "base_url": "https://www.n11.com",
        "listing_url": "BUL: n11'de Kampanyalar sayfasının URL'si",
        "card_selector": "BUL",
        "name_selector": "BUL",
        "price_selector": "BUL",
        "ref_price_selector": "BUL",
        "link_selector": "a",
    },
    {
        "name": "hepsiburada",
        "base_url": "https://www.hepsiburada.com",
        "listing_url": "BUL: Hepsiburada'da Fırsat Ürünleri sayfasının URL'si",
        "card_selector": "BUL",
        "name_selector": "BUL",
        "price_selector": "BUL",
        "ref_price_selector": "BUL",
        "link_selector": "a",
    },
    {
        "name": "amazon",
        "base_url": "https://www.amazon.com.tr",
        "listing_url": "BUL: Amazon.com.tr'de Günün Fırsatları sayfasının URL'si",
        "card_selector": "BUL",
        "name_selector": "BUL",
        "price_selector": "BUL",
        "ref_price_selector": "BUL",
        "link_selector": "a",
    },
]


def main():
    all_deals: list[Deal] = []
    for store in STORES:
        if store["listing_url"].startswith("BUL"):
            print(f"[{store['name']}] atlandı — listing_url henüz dolduruLMADI.")
            continue
        try:
            found = scrape_store(store)
            print(f"[{store['name']}] {len(found)} ürün tarandı.")
            all_deals.extend(found)
        except Exception as e:
            print(f"[{store['name']}] HATA: {e}")
        time.sleep(REQUEST_DELAY_SECONDS)

    # NOT: eşik filtrelemesi burada değil index.html'deki kaydırıcıda yapılıyor.
    # Böylece eşiği değiştirmek için scraper'ı yeniden çalıştırman gerekmiyor —
    # taranan her ürün deals.json'a yazılır, arayüz istediğin yüzdeye göre süzer.
    all_deals.sort(key=lambda d: d.discount_pct, reverse=True)
    genuine_count = sum(1 for d in all_deals if d.discount_pct >= MIN_DISCOUNT)

    output = [{**asdict(d), "discount_pct": d.discount_pct} for d in all_deals]
    with open("deals.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nToplam {len(all_deals)} ürün tarandı, {genuine_count} tanesi %{MIN_DISCOUNT}+ gerçek indirimde.")
    print("Hepsi deals.json dosyasına yazıldı — eşik filtresi arayüzde uygulanıyor.")


if __name__ == "__main__":
    main()


# ------------------------------------------------------------------------
# SEÇİCİLERİ BULMA REHBERİ (her mağaza için ~5 dakika, bir kere yapılır)
# ------------------------------------------------------------------------
# YÖNTEM A — düz HTML çalışıyorsa (çoğu site SEO için ilk sayfayı böyle sunar):
#   1. Telefon değil BİLGİSAYARDAN Chrome ile mağazanın Kampanyalar/İndirimli
#      Ürünler sayfasını aç. O URL'yi listing_url'e yapıştır.
#   2. Herhangi bir ürün kutusuna sağ tıkla > İncele (Inspect).
#   3. Açılan panelde ürünü saran <div> ya da <li>'nin class'ını gör
#      (örn. class="p-card-wrppr") — bunu card_selector'a yaz: ".p-card-wrppr"
#   4. Aynı kutunun içinde ürün adını, şu anki fiyatı ve üstü çizili/son 10
#      gün fiyatını gösteren elemanların class'larını aynı şekilde bul.
#   5. Bu dosyayı çalıştır: python scraper.py
#      "Hiç ürün kartı bulunamadı" derse card_selector yanlış ya da
#      YÖNTEM B gerekiyor demektir.
#
# YÖNTEM B — sayfa JavaScript ile yükleniyorsa (kartlar bulunamıyorsa):
#   requests+BeautifulSoup düz HTML okur, tarayıcının çalıştırdığı JS'i
#   çalıştırmaz. Bu durumda gerçek bir tarayıcıyı kod ile yöneten Playwright
#   gerekir ("pip install playwright", "playwright install chromium").
#   İstersen bu scraper'ın Playwright sürümünü de yazarım — hangi mağazada
#   YÖNTEM A boş döndüyse söyle, onun için yazayım.
# ------------------------------------------------------------------------
