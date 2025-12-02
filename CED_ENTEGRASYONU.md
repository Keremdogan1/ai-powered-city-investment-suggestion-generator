# 🌐 ÇED Entegrasyonu Dokümantasyonu

## 📋 Genel Bakış

Bu sistem, Çevre, Şehircilik ve İklim Değişikliği Bakanlığı'nın ÇED Duyuru Sistemi'nden İstanbul ile ilgili projeleri otomatik olarak çeker ve AI önerileriyle karşılaştırır.

## 🎯 Özellikler

### ✅ Şu Anda Aktif

- **Web Scraping:** ÇED sitesinden proje verisi çekme
- **Kategorizasyon:** Projleri otomatik kategorilere ayırma (ulaşım, sağlık, çevre, eğitim)
- **İstanbul Filtresi:** Sadece İstanbul projelerini seçme
- **Önbellek:** 1 saat cache ile performans optimizasyonu
- **Karşılaştırma:** AI önerileri vs ÇED projeleri
- **Fallback:** Bağlantı başarısız olursa örnek veri

### 🔜 Gelecek Özellikler

- **API Entegrasyonu:** Resmi API varsa kullanma
- **Detaylı Eşleştirme:** NLP ile daha iyi proje eşleştirme
- **İlçe Bazlı Filtreleme:** Proje lokasyonlarını ilçelere eşleştirme
- **Tarih Takibi:** Proje aşamalarını takip etme

---

## 🚀 Hızlı Başlangıç

### 1️⃣ Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

**Gerekli Paketler:**

- `Flask` - Web sunucu
- `requests` - HTTP istekleri
- `beautifulsoup4` - HTML parsing
- `lxml` - HTML parser

### 2️⃣ ÇED Bağlantısını Test Et

```bash
python ced_test.py
```

Bu script:

- ÇED sitesine bağlanır
- Sayfa yapısını analiz eder
- Örnek proje verisi çıkarır
- API endpoint'lerini test eder

### 3️⃣ Web Sunucusunu Başlat

```bash
python web_sunucu.py
```

---

## 📊 API Endpoint'leri

### Temel ÇED Endpoint'leri

#### 1. Tüm ÇED Projeleri

```http
GET /api/ced-projeleri
```

**Response:**

```json
{
  "projeler": [
    {
      "proje_adi": "Beylikdüzü Metro Hattı",
      "firma": "İBB",
      "il": "İstanbul",
      "sektor": "Ulaşım",
      "tarih": "2024",
      "kategori": "ulasim",
      "durum": "Planlama"
    }
  ],
  "toplam": 15,
  "son_guncelleme": "2024-11-22T10:30:00",
  "kaynak": "ÇED Duyuru Sistemi"
}
```

#### 2. Kategoriye Göre Filtrele

```http
GET /api/ced-projeleri?kategori=ulasim
GET /api/ced-projeleri?kategori=saglik
GET /api/ced-projeleri?kategori=cevre
GET /api/ced-projeleri?kategori=egitim
```

#### 3. AI Önerileri ile Karşılaştır

```http
GET /api/ulasim/ced-karsilastir
```

**Response:**

```json
{
  "toplam_ai_oneri": 39,
  "toplam_ced_proje": 15,
  "eslesen_proje": 3,
  "yeni_oneri": 36,
  "detaylar": [
    {
      "ilce": "Beylikdüzü",
      "ai_oneri": "Beylikdüzü Metro Hattı",
      "ai_maliyet": "₺28.5 Milyar",
      "ced_proje": "Beylikdüzü-Avcılar Metro",
      "ced_durum": "Planlama",
      "durum": "Zaten Planlanıyor",
      "eslesme_skoru": 1.0
    }
  ]
}
```

---

## 🔧 Teknik Detaylar

### Web Scraping Mantığı

```python
def scrape_ced_projeleri(kategori=None):
    # 1. ÇED sitesine bağlan
    response = requests.get(ced_url, headers=headers)

    # 2. HTML'i parse et
    soup = BeautifulSoup(response.content, 'html.parser')

    # 3. Proje elementlerini bul
    proje_kartlari = soup.find_all('div', class_='ui-panel')

    # 4. Her proje için bilgi çıkar
    for kart in proje_kartlari:
        proje = parse_ced_proje(kart)
        if is_istanbul_project(proje):
            projeler.append(proje)

    # 5. Kategoriye göre filtrele
    return filter_by_category(projeler, kategori)
```

### Kategorizasyon Algoritması

```python
def categorize_project(proje_adi, sektor):
    text = (proje_adi + " " + sektor).lower()

    # Keyword matching
    if any(k in text for k in ['metro', 'tramvay', 'yol']):
        return 'ulasim'

    if any(k in text for k in ['hastane', 'sağlık']):
        return 'saglik'

    # ... diğer kategoriler
    return 'diger'
```

### Önbellek Sistemi

```python
CED_CACHE = {
    "data": None,
    "timestamp": None,
    "cache_duration": 3600  # 1 saat
}

def get_cached_or_fetch():
    # Cache kontrolü
    if cache_is_valid():
        return CED_CACHE["data"]

    # Yeni veri çek
    new_data = scrape_ced_projeleri()
    CED_CACHE["data"] = new_data
    CED_CACHE["timestamp"] = datetime.now()

    return new_data
```

---

## 🎨 Kategoriler ve Anahtar Kelimeler

### 🚇 Ulaşım

```python
['metro', 'tramvay', 'otobüs', 'teleferik', 'köprü',
 'tünel', 'yol', 'otopark', 'karayolu', 'raylı sistem']
```

### 🏥 Sağlık

```python
['hastane', 'sağlık', 'klinik', 'tıp', 'poliklinik',
 'acil', 'ambulans', 'sağlık merkezi']
```

### 🌳 Çevre

```python
['atık', 'çevre', 'park', 'yeşil alan',
 'arıtma', 'kanalizasyon']
```

### 🏫 Eğitim

```python
['okul', 'üniversite', 'eğitim', 'kampüs',
 'öğrenci', 'öğretmen']
```

---

## 🔍 Sorun Giderme

### Problem 1: ÇED sitesine bağlanılamıyor

**Belirti:**

```
❌ ÇED sitesine bağlanılamadı: Connection refused
```

**Çözümler:**

1. İnternet bağlantısını kontrol et
2. ÇED sitesinin erişilebilir olduğunu doğrula: https://eced-duyuru.csb.gov.tr
3. Firewall ayarlarını kontrol et
4. VPN kullanıyorsan kapat/aç

**Fallback:** Sistem otomatik olarak örnek veri gösterir.

---

### Problem 2: Proje verisi çıkarılamıyor

**Belirti:**

```
⚠️ 0 proje bulundu
```

**Çözümler:**

1. `ced_test.py` çalıştır ve sayfa yapısını analiz et
2. ÇED sitesinin HTML yapısı değişmiş olabilir
3. `web_sunucu.py` içindeki selector'ları güncelle:

```python
# Eski
proje_kartlari = soup.find_all('div', class_='ui-panel')

# Yeni (sitenin yapısına göre)
proje_kartlari = soup.find_all('tr', class_='proje-satiri')
```

4. Tarayıcıdan siteye gir ve Developer Tools ile elementleri incele

---

### Problem 3: Kategoriler yanlış atanıyor

**Belirti:**

```
Hastane projesi "ulaşım" olarak kategorize edildi
```

**Çözüm:** `categorize_project()` fonksiyonundaki keyword'leri güncelle:

```python
# Daha spesifik keyword'ler ekle
saglik_keywords = [
    'hastane', 'sağlık merkezi', 'poliklinik',
    'acil servis', 'ameliyathane', 'yoğun bakım'
]
```

---

### Problem 4: İstanbul projeleri filtrelenmiyor

**Belirti:**

```
Ankara projeleri de geliyor
```

**Çözüm:** `is_istanbul_project()` fonksiyonunu güçlendir:

```python
def is_istanbul_project(proje):
    il = proje.get('il', '').lower()
    proje_adi = proje.get('proje_adi', '').lower()
    firma = proje.get('firma', '').lower()

    istanbul_keywords = [
        'istanbul', 'İstanbul', 'ISTANBUL',
        'ibb', 'istanbul büyükşehir'
    ]

    return any(k.lower() in (il + proje_adi + firma)
               for k in istanbul_keywords)
```

---

## 📈 Performans Optimizasyonu

### 1. Önbellek Kullanımı

```python
# 1 saat cache
CED_CACHE["cache_duration"] = 3600

# Daha uzun cache için (4 saat)
CED_CACHE["cache_duration"] = 14400
```

### 2. Timeout Ayarları

```python
# Bağlantı timeout'u
response = requests.get(url, timeout=10)

# Daha uzun timeout
response = requests.get(url, timeout=30)
```

### 3. Rate Limiting

```python
# Flask-Limiter ile
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])

@app.route('/api/ced-projeleri')
@limiter.limit("20 per minute")
def get_ced_projeleri():
    ...
```

---

## 🔐 Güvenlik

### User-Agent Kullanımı

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

### SSL Doğrulama

```python
# SSL hatası varsa (önerilmez)
response = requests.get(url, verify=False)
```

### Error Handling

```python
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout Error: {e}")
```

---

## 📊 İstatistikler ve Raporlama

### ÇED Durum Raporu

```http
GET /api/durum
```

```json
{
  "ced_sistem": {
    "durum": "Aktif ✅",
    "son_kontrol": "2024-11-22T10:30:00",
    "cache_proje_sayisi": 15
  }
}
```

### Karşılaştırma Raporu

```python
# Eşleşme oranı
eslesme_orani = eslesen_proje / toplam_ai_oneri * 100

# Yeni öneri oranı
yeni_oneri_orani = yeni_oneri / toplam_ai_oneri * 100
```

---

## 🚀 Gelecek Geliştirmeler

### 1. NLP Tabanlı Eşleştirme

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def advanced_matching(ai_oneri, ced_proje):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([ai_oneri, ced_proje])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return similarity
```

### 2. İlçe Bazlı Haritalama

```python
def map_project_to_district(proje):
    # Proje lokasyonunu ilçeye eşleştir
    for ilce in ISTANBUL_ILCELERI:
        if ilce.lower() in proje['proje_adi'].lower():
            return ilce
    return None
```

### 3. Otomatik Bildirim

```python
def check_new_projects():
    # Yeni proje eklendi mi kontrol et
    if new_project_count > 0:
        send_notification(f"{new_project_count} yeni proje!")
```

---

## 📚 Kaynaklar

- **ÇED Ana Sayfa:** https://eced-duyuru.csb.gov.tr/eced-prod/duyurular.xhtml
- **İBB Açık Veri:** https://data.ibb.gov.tr
- **Flask Dokümantasyonu:** https://flask.palletsprojects.com/
- **BeautifulSoup Dokümantasyonu:** https://www.crummy.com/software/BeautifulSoup/

---

## 🤝 Katkıda Bulunma

ÇED entegrasyonunu geliştirmek için:

1. `ced_test.py` ile mevcut durumu test et
2. `web_sunucu.py` içindeki parsing fonksiyonlarını optimize et
3. Yeni kategoriler ekle
4. NLP tabanlı eşleştirme geliştir

---

**Son Güncelleme:** 2024-11-22  
**Versiyon:** v1.0  
**Durum:** Aktif ✅
