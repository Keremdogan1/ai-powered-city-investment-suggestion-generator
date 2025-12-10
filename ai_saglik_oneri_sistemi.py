"""
İstanbul Sağlık - AI Öneri Sistemi
Claude Sonnet 4.5 ile sağlık altyapısı önerileri
"""

import json
import os
import requests
import time
from dotenv import load_dotenv

BASE_DIR = r"C:\ProgrammingFile\Python\IstanbulUlasimProjesi"
CIKTI_KLASORU = os.path.join(BASE_DIR, "ciktilar")

print("=" * 70)
print("🤖 CLAUDE AI SAĞLIK ÖNERİ SİSTEMİ - 39 İLÇE")
print("=" * 70)
print()

# API Key
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== 1. ANALİZ VERİSİNİ YÜKLE =====
print("📂 Analiz verisi yükleniyor...")
try:
    with open(f"{CIKTI_KLASORU}/ai_analiz_saglik_39ilce.json", 'r', encoding='utf-8') as f:
        analiz_data = json.load(f)
    print(f"✅ {len(analiz_data['en_sorunlu_ilceler'])} ilçe yüklendi")
except FileNotFoundError:
    print("❌ HATA: ai_analiz_saglik_39ilce.json bulunamadı!")
    print("   Önce saglik_analiz_motoru.py çalıştırın")
    exit(1)

print()

# ===== 2. ÖNCELİK GRUPLARI =====
ilceler = analiz_data['en_sorunlu_ilceler']

yuksek_oncelik = [ilce for ilce in ilceler if ilce['genel_saglik_skoru'] >= 60]
orta_oncelik = [ilce for ilce in ilceler if 30 <= ilce['genel_saglik_skoru'] < 60]
dusuk_oncelik = [ilce for ilce in ilceler if ilce['genel_saglik_skoru'] < 30]

print(f"📊 Öncelik Dağılımı:")
print(f"  🔴 Yüksek: {len(yuksek_oncelik)} ilçe")
print(f"  🟡 Orta: {len(orta_oncelik)} ilçe")
print(f"  🟢 Düşük: {len(dusuk_oncelik)} ilçe")
print()

# ===== 3. PROMPT HAZIRLA =====
gd = analiz_data.get('genel_durum', {})

prompt_text = f"""
Sen bir sağlık politikası uzmanısın. İstanbul'un TÜM 39 İLÇESİ için sağlık altyapısı önerileri sunacaksın.

📊 GENEL DURUM:
- Toplam Nüfus: {gd.get('toplam_nufus', 0):,}
- Toplam Hastane: {gd.get('toplam_hastane', 0)}
- Toplam Yatak: {gd.get('toplam_yatak', 0):,}
- Toplam Hekim: {gd.get('toplam_hekim', 0):,}
- Toplam ASM: {gd.get('toplam_asm', 0)}
- Ortalama Eksiklik: {gd.get('ortalama_eksiklik', 0):.1f}/100

🎯 DSÖ VE SAĞLIK BAKANLIĞI STANDARTLARI:
- 1000 kişiye 3.5 yatak
- 1000 kişiye 2.5 hekim
- 100,000 kişiye 2.5 hastane
- Acil erişim maksimum 10 dakika
- 5000 kişiye 1 ASM

🎯 GÖREV: Tüm 39 ilçe için öneri hazırla (öncelik sırasına göre)

⚠️ KRİTİK: ÖNCELİK KURALLARI (SKOR BAZLI):
- 🔴 Yüksek Öncelik: 60-100 arası ({len(yuksek_oncelik)} ilçe)
- 🟡 Orta Öncelik: 30-60 arası ({len(orta_oncelik)} ilçe)
- 🟢 Düşük Öncelik: 0-30 arası ({len(dusuk_oncelik)} ilçe)

📋 39 İLÇE LİSTESİ:

"""

# İlçeleri gruplar halinde listele
prompt_text += f"🔴 YÜKSEK ÖNCELİK ({len(yuksek_oncelik)} İlçe):\n"
for i, ilce in enumerate(yuksek_oncelik, 1):
    prompt_text += f"{i}. {ilce.get('ilce','?')} - Nüfus: {ilce.get('nufus',0):,}, Skor: {ilce.get('genel_saglik_skoru',0):.1f}\n"
    prompt_text += f"   Hastane: {ilce.get('hastane_sayisi',0)}, Yatak: {ilce.get('toplam_yatak',0)}, Hekim: {ilce.get('hekim_sayisi',0)}\n"

prompt_text += f"\n🟡 ORTA ÖNCELİK ({len(orta_oncelik)} İlçe):\n"
for i, ilce in enumerate(orta_oncelik, len(yuksek_oncelik)+1):
    prompt_text += f"{i}. {ilce.get('ilce','?')} - Nüfus: {ilce.get('nufus',0):,}, Skor: {ilce.get('genel_saglik_skoru',0):.1f}\n"

prompt_text += f"\n🟢 DÜŞÜK ÖNCELİK ({len(dusuk_oncelik)} İlçe):\n"
for i, ilce in enumerate(dusuk_oncelik, len(yuksek_oncelik)+len(orta_oncelik)+1):
    prompt_text += f"{i}. {ilce.get('ilce','?')} - Nüfus: {ilce.get('nufus',0):,}, Skor: {ilce.get('genel_saglik_skoru',0):.1f}\n"

prompt_text += """

⚠️ ÖNEMLİ KURALLAR:

1. **MALİYET TAHMİNİ (1$ = 42 TL)**:
   - Yeni Hastane (100 yatak): ₺250-350 Milyon ($6-8 Milyon)
   - Yeni Hastane (200 yatak): ₺500-700 Milyon ($12-17 Milyon)
   - Yeni Hastane (300 yatak): ₺800-1,200 Milyon ($19-29 Milyon)
   - ASM (Aile Sağlığı Merkezi): ₺15-25 Milyon ($350k-600k)
   - Poliklinik Genişletme: ₺50-100 Milyon ($1.2-2.4 Milyon)
   - Yoğun Bakım Ünitesi (10 yatak): ₺80-120 Milyon ($1.9-2.9 Milyon)

2. **HER İLÇE İÇİN**:
   - Proje detayını yaz (hastane türü, kapasite, bölüm sayısı)
   - Maliyet hesapla (₺ ve $)
   - ÖNCELİĞİ SKORUNA GÖRE BELİRLE!
   - Hekim ihtiyacını belirt

3. **PROJE TÜRLERİ**:
   - Yeni hastane (devlet/şehir/eğitim)
   - Mevcut hastane genişletme
   - ASM kurulumu/genişletme
   - Poliklinik açma
   - Yoğun bakım kapasitesi artırma
   - Acil servis iyileştirme

JSON FORMATI (DETAYLI):
[
  {
    "ilce": "...",
    "oncelik": "Yüksek|Orta|Düşük",
    "proje_adi": "...",
    "proje_detay": "DETAYLI açıklama: Hastane türü, kapasite, bölümler, teknolojik donanım. En az 100 kelime!",
    "tahmini_maliyet": "₺X.X Milyar ($YYY Milyon)",
    "beklenen_etki": "Detaylı etki analizi",
    "uygulama_suresi": "XX ay",
    "hekim_ihtiyaci": {
      "uzman_hekim": 50,
      "pratisyen": 30,
      "asistan": 20,
      "toplam": 100
    },
    "bina_ozellikleri": {
      "yatak_kapasitesi": 200,
      "yogun_bakim": 30,
      "ameliyathane": 8,
      "poliklinik": 40,
      "acil_servis": "7/24 tam donanımlı"
    },
    "alternatif_cozumler": [
      "Alternatif 1 (maliyet - süre)",
      "Alternatif 2 (maliyet - süre)",
      "Alternatif 3 (maliyet - süre)"
    ],
    "kisa_vade_etki": "İlk 1-2 yıl içindeki etkiler",
    "orta_vade_etki": "3-5 yıl içindeki etkiler",
    "uzun_vade_etki": "10 yıl sonraki vizyon"
  }
]

⚠️ ÇOK ÖNEMLİ - DETAY SEVİYESİ:
- proje_detay: EN AZ 100 KELİME, spesifik bölümler, teknoloji
- hekim_ihtiyaci: Uzmanlık alanlarına göre dağılım yap
- bina_ozellikleri: Tüm teknik detaylar
- alternatif_cozumler: 3 alternatif + maliyet + süre
- kisa/orta/uzun_vade_etki: Her birini ayrı ayrı yaz

🎯 TÜM 39 İLÇE İÇİN ÖNERİ HAZIRLA!
ÖNCELİKLERİ MUTLAKA SKORLARA GÖRE BELİRLE!
Sadece JSON döndür, açıklama ekleme.
"""

# ===== 4. CLAUDE'A GÖNDER =====
print("=" * 70)
print("🚀 Claude'a Gönderiliyor...")
print("=" * 70)
print()

try:
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-sonnet-4.5",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.7,
        "max_tokens": 100000
    }
    
    print("⏳ İstek gönderiliyor...")
    start_time = time.time()
    
    response = requests.post(url, headers=headers, json=data, timeout=300)
    
    elapsed = time.time() - start_time
    print(f"⏱️ Yanıt süresi: {elapsed:.1f} saniye\n")
    
    if response.status_code != 200:
        print(f"❌ API Hatası: {response.status_code}")
        print(response.text)
        exit(1)
    
    result = response.json()
    ai_response = (
        result.get('choices', [{}])[0]
              .get('message', {})
              .get('content', "")
    )
    
    usage = result.get('usage', {})
    total_tokens = usage.get('total_tokens')
    if total_tokens:
        print(f"📊 Token Kullanımı: {total_tokens:,}")
    
    print("✅ Yanıt alındı!\n")
    
    # ===== 5. KAYDET =====
    print("=" * 70)
    print("💾 Kaydediliyor")
    print("=" * 70)
    print()
    
    # TXT kaydet
    with open(f"{CIKTI_KLASORU}/ai_saglik_onerileri_39ilce.txt", 'w', encoding='utf-8') as f:
        f.write("İSTANBUL SAĞLIK - AI ÖNERİLER (39 İLÇE)\n")
        f.write("=" * 70 + "\n\n")
        f.write(ai_response)
    
    print("✅ TXT kaydedildi: ai_saglik_onerileri_39ilce.txt")
    
    # JSON parse ve kaydet
    try:
        json_text = ai_response.strip()
        # ```json bloklarını temizle
        if json_text.startswith("```"):
            lines = json_text.split('\n')
            json_text = '\n'.join(lines[1:-1])
        
        # İlk '[' veya '{' dan itibaren al
        first_brace = min(
            [i for i in [json_text.find('['), json_text.find('{')] if i != -1] or [0]
        )
        if first_brace > 0:
            json_text = json_text[first_brace:]
        
        ai_json = json.loads(json_text)
        if isinstance(ai_json, dict):
            ai_json = [ai_json]
        
        with open(f"{CIKTI_KLASORU}/ai_saglik_onerileri_39ilce.json", 'w', encoding='utf-8') as f:
            json.dump(ai_json, f, ensure_ascii=False, indent=2)
        
        print("✅ JSON kaydedildi: ai_saglik_onerileri_39ilce.json")
        print(f"  {len(ai_json)} ilçe önerisi\n")
        
        # ===== 6. İSTATİSTİKLER =====
        print("=" * 70)
        print("📊 PROJE İSTATİSTİKLERİ")
        print("=" * 70)
        print()
        
        # Öncelik dağılımı
        oncelikler = {'Yüksek': 0, 'Orta': 0, 'Düşük': 0}
        for o in ai_json:
            onc = o.get('oncelik', 'Orta')
            if onc in oncelikler:
                oncelikler[onc] += 1
        
        print("🎯 AI'ın Verdiği Öncelik Dağılımı:")
        for onc, sayi in oncelikler.items():
            print(f"  - {onc}: {sayi} ilçe")
        print()
        
        # Toplam maliyet
        toplam_maliyet = 0
        for o in ai_json:
            maliyet_text = o.get('tahmini_maliyet', '')
            import re
            match = re.search(r'₺([\d.,]+)', maliyet_text)
            if match:
                maliyet_str = match.group(1).replace(',', '.')
                try:
                    toplam_maliyet += float(maliyet_str)
                except:
                    pass
        
        if toplam_maliyet > 0:
            dolar_maliyet = toplam_maliyet / 42
            print(f"💰 Toplam Tahmini Yatırım:")
            print(f"   ₺{toplam_maliyet:.1f} Milyar")
            print(f"   ≈ ${dolar_maliyet:.0f} Milyon")
        print()
        
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON hatası: {e}")
        print("   TXT dosyasını kontrol edin\n")

except Exception as e:
    print(f"❌ Hata: {e}\n")
    import traceback
    traceback.print_exc()

print("=" * 70)
print("✅ TAMAMLANDI! 🎉")
print("=" * 70)
print()
print("📌 Sonraki Adım: Web Entegrasyonu")
print("   - web_sunucu.py'ye /api/saglik endpoint'leri ekle")
print("   - saglik.html arayüzünü oluştur")
print("=" * 70)