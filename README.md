# İndirim Fişi

Trendyol, N11, Hepsiburada ve Amazon'un kendi kampanya sayfalarını otomatik
tarayıp, 1 Ağustos 2026 yönetmeliğiyle zorunlu olan "son 10 günün en düşük
fiyatı" referansına göre GERÇEK indirimi hesaplayan, kişisel/tek kullanıcılık
bir web uygulaması.

## İçindekiler
- `index.html` — arayüz (mağaza filtreleri, %eşik kaydırıcısı, ürün listesi)
- `scraper.py` — kampanya sayfalarını tarayıp `deals.json` üreten Python kodu
- `deals.json` — taranan ürünler (şu an örnek veri; ilk otomatik taramadan sonra gerçek veriyle değişir)
- `.github/workflows/tara.yml` — `scraper.py`'yi her 4 saatte bir otomatik çalıştıran ayar

## 1) Ücretsiz canlıya alma (~10 dakika)

1. [github.com](https://github.com) üzerinde ücretsiz bir hesap aç (yoksa).
2. Sağ üstten **New repository** ile yeni, **public** bir depo oluştur (adı önemli değil, örn. `indirim-fisi`).
3. Bu dört dosyayı (klasör yapısını koruyarak, yani `.github/workflows/tara.yml` içinde kalacak şekilde) o depoya yükle: GitHub'ın web arayüzünde **Add file → Upload files** ile sürükle-bırak yeterli.
4. Depo **Settings → Pages** kısmından: Source = *Deploy from a branch*, Branch = *main*, klasör = */ (root)* seç, Save'e bas. Birkaç dakika içinde siten `https://KULLANICI-ADIN.github.io/DEPO-ADI/` adresinde yayında olacak.
5. Depo **Settings → Actions → General** kısmından *Workflow permissions*'ı **Read and write permissions** yap ve kaydet (scraper'ın `deals.json`'ı commit'leyebilmesi için gerekli).
6. **Actions** sekmesine gidip *İndirim Tarama* iş akışını seç, **Run workflow** ile bir kere elle çalıştır — bu, sistemin uçtan uca çalıştığını görmenin en hızlı yolu.

Bu noktada site canlı ama `scraper.py` içindeki "BUL:" yerleri doldurulmadan
hep aynı örnek 7 ürünü gösterecek — bir sonraki adım bunun için.

## 2) Gerçek verinin akması için: seçicileri bul (mağaza başına ~5 dk)

`scraper.py` dosyasının en altında **"SEÇİCİLERİ BULMA REHBERİ"** var —
bilgisayarından Chrome ile ilgili mağazanın Kampanyalar/İndirimli Ürünler
sayfasını açıp sağ tık → İncele ile 4-5 class adını kopyalayıp dosyaya
yapıştırman yeterli. Trendyol'u yapınca diğer üçü aynı yöntemle çok daha hızlı gider.

Değişikliği kaydedip GitHub'a yeniden yükledikten sonra **Actions → Run workflow**
ile elle bir kez daha çalıştır, `deals.json`'ın gerçek verilerle güncellendiğini gör.

Bir mağazada "Hiç ürün kartı bulunamadı" hatası alırsan, o sayfa muhtemelen
JavaScript ile yükleniyordur — bunu bana söyle, o mağaza için Playwright
tabanlı alternatifi yazayım.

## 3) Telefona kurma

**Basit yol (şu an çalışır):** telefonunda Chrome'da siteni aç → sağ üstteki
⋮ menüsü → **Ana ekrana ekle**. Simge telefonuna düşer, tam ekran açılır.

**Gerçek bir .apk dosyası istiyorsan:** [pwabuilder.com](https://www.pwabuilder.com/)
adresine git, GitHub Pages linkini yapıştır, Android paketini indir. Çıkan
`.apk` dosyasını telefonuna atıp "bilinmeyen kaynaklardan yüklemeye" izin
vererek doğrudan kurabilirsin — Play Store'a hiç yüklemene gerek yok.

## Ayarlar

- **Eşik:** varsayılan %25, arayüzdeki kaydırıcıdan değiştirilebilir (backend'i yeniden çalıştırmaya gerek yok).
- **Tarama sıklığı:** `.github/workflows/tara.yml` içindeki `cron: '0 */4 * * *'` satırını değiştirerek ayarlanır (örn. her 2 saatte bir için `0 */2 * * *`).
