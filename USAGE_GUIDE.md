# 🚀 Proje Çalıştırma Kılavuzu

## 📋 Ön Hazırlık

### 1. Bağımlılıkları Yükle
```bash
pip install -r src/requirements.txt
```

### 2. API Key Ayarla
Proje kök dizininde `.env` dosyası oluşturun:
```
OPENROUTER_API_KEY=your-api-key-here
```

**Not:** `.env` dosyası zaten `.gitignore`'da, güvenli.

---

## 🎯 Çalıştırma Sırası

### Seçenek 1: Sadece Web Arayüzünü Çalıştır (Önceden üretilmiş verilerle)

Eğer `outputs/` klasöründe önceden üretilmiş JSON dosyaları varsa, direkt web sunucusunu başlatabilirsiniz:

```bash
python src/web_server.py
```

**Erişim:** http://localhost:5000

---

### Seçenek 2: Tüm Modülleri Çalıştır (Tam Analiz)

#### 🌳 ÇEVRE MODÜLÜ

**Adım 1: Analiz Motoru**
```bash
python src/environment_analysis_engine.py
```
**Çıktılar:**
- `outputs/ai_analiz_cevre_39ilce.json`
- `outputs/ilce_cevre_raporu_39ilce.csv`

**Adım 2: AI Önerileri** (API key gerekli)
```bash
python src/ai_environment_recommendations.py
```
**Çıktılar:**
- `outputs/ai_cevre_onerileri_39ilce.json`
- `outputs/ai_cevre_onerileri_39ilce.txt`

---

#### 🏥 SAĞLIK MODÜLÜ

**Adım 1: Veri Tahmini**
```bash
python src/health_data_estimation.py
```
**Çıktılar:**
- `data/ham_veri/saglik/ilce_saglik_birlesik_tahmini.csv`
- `data/ham_veri/saglik/veri_metadata.json`

**Adım 2: Analiz Motoru**
```bash
python src/health_analysis_engine.py
```
**Çıktılar:**
- `outputs/ai_analiz_saglik_39ilce.json`
- `outputs/ilce_saglik_raporu_39ilce.csv`

**Adım 3: AI Önerileri** (API key gerekli)
```bash
python src/ai_health_recommendations.py
```
**Çıktılar:**
- `outputs/ai_saglik_onerileri_39ilce.json`
- `outputs/ai_saglik_onerileri_39ilce.txt`

---

#### 🚇 ULAŞIM MODÜLÜ

**Adım 1: Analiz Motoru**
```bash
python src/transportation_analysis_engine.py
```
**Çıktılar:**
- `outputs/ai_analiz_verisi_39ilce_trafik.json`
- `outputs/ai_analiz_verisi_39ilce.json`
- `outputs/ilce_eksiklik_raporu_39ilce.csv`

**Adım 2: AI Önerileri** (API key gerekli)
```bash
python src/ai_transportation_recommendations.py
```
**Çıktılar:**
- `outputs/ai_yatirim_onerileri_v5_ced.json`
- `outputs/ai_yatirim_onerileri_v5_ced.txt`

---

#### 🌐 WEB SUNUCUSU

Tüm analizler tamamlandıktan sonra:

```bash
python src/web_server.py
```

**Erişim:**
- Ana Sayfa: http://localhost:5000
- Ulaşım: http://localhost:5000/ulasim
- Sağlık: http://localhost:5000/saglik
- Çevre: http://localhost:5000/cevre

---

## 📊 Hızlı Başlangıç (Tüm Modüller)

Tüm modülleri sırayla çalıştırmak için:

```bash
# 1. Çevre Modülü
python src/environment_analysis_engine.py
python src/ai_environment_recommendations.py

# 2. Sağlık Modülü
python src/health_data_estimation.py
python src/health_analysis_engine.py
python src/ai_health_recommendations.py

# 3. Ulaşım Modülü
python src/transportation_analysis_engine.py
python src/ai_transportation_recommendations.py

# 4. Web Sunucusu
python src/web_server.py
```

---

## ⚠️ Önemli Notlar

### API Key Gereksinimi
- **AI öneri sistemleri** (`ai_*_recommendations.py`) için API key **ZORUNLU**
- Analiz motorları (`*_analysis_engine.py`) API key gerektirmez
- `.env` dosyasında `OPENROUTER_API_KEY` tanımlı olmalı

### Veri Bağımlılıkları

**Çevre Modülü:**
- `data/ham_veri/ilce_nufus_temiz.xlsx` (zorunlu)
- `data/ham_veri/_yesil_alanlar_verileri.xlsx` (zorunlu)
- `data/ham_veri/yaysis_mahal_geo_data.geojson` (zorunlu)

**Sağlık Modülü:**
- `data/ham_veri/saglik/hastane_sayisi.csv` (zorunlu)
- `data/ham_veri/saglik/ilce_tahmini_yatak_sayisi.csv` (zorunlu)
- `data/ham_veri/ilce_nufus_temiz.xlsx` (zorunlu)

**Ulaşım Modülü:**
- `data/ham_veri/ilce_nufus_temiz.xlsx` (zorunlu)
- `data/ham_veri/ilce_metro_manuel.csv` (zorunlu)
- `data/ham_veri/ispark_otopark.csv` (zorunlu)
- `data/ham_veri/ilce_trafik_skoru.csv` (opsiyonel)

---

## 🔍 Durum Kontrolü

Web sunucusu çalışırken durum kontrolü:

```bash
curl http://localhost:5000/api/durum
```

veya tarayıcıda: http://localhost:5000/api/durum

---

## 📝 Çıktı Dosyaları

Tüm çıktılar `outputs/` klasöründe:

**Analiz Verileri:**
- `ai_analiz_cevre_39ilce.json`
- `ai_analiz_saglik_39ilce.json`
- `ai_analiz_verisi_39ilce_trafik.json`

**AI Önerileri:**
- `ai_cevre_onerileri_39ilce.json`
- `ai_saglik_onerileri_39ilce.json`
- `ai_yatirim_onerileri_v5_ced.json`

**CSV Raporlar:**
- `ilce_cevre_raporu_39ilce.csv`
- `ilce_saglik_raporu_39ilce.csv`
- `ilce_eksiklik_raporu_39ilce.csv`

---

## 🐛 Sorun Giderme

### Hata: "API Key bulunamadı"
**Çözüm:** `.env` dosyasını kontrol edin, `OPENROUTER_API_KEY` tanımlı olmalı.

### Hata: "Dosya bulunamadı"
**Çözüm:** `data/ham_veri/` klasöründeki gerekli dosyaları kontrol edin.

### Hata: "Module not found"
**Çözüm:** `pip install -r src/requirements.txt` çalıştırın.

---

## ✅ Başarı Kriterleri

Tüm modüller başarıyla çalıştığında:
- ✅ `outputs/` klasöründe JSON ve CSV dosyaları oluşur
- ✅ Web sunucusu hatasız başlar
- ✅ http://localhost:5000 adresinde ana sayfa görünür
- ✅ Her kategori için analiz sayfaları çalışır

