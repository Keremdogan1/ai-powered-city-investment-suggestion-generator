import json
from datetime import datetime
import requests
import time
from scrape_ced_selenium import scrape_ced_with_selenium
from dotenv import load_dotenv
import os

CIKTI_KLASORU = r"C:\ProgrammingFile\Python\IstanbulUlasimProjesi\ciktilar"

print("=" * 70)
print("🤖 CLAUDE AI ÖNERİ SİSTEMİ v5 - EÇED ENTEGRASYONLU 🗺️")
print("=" * 70)
print()

print("🔑 API Key kontrol ediliyor...")
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY or API_KEY == "your-api-key-here":
    print("❌ HATA: API Key bulunamadı!")
    exit(1)

print("✓ API Key bulundu\n")

# ===== 1. EÇED PROJELERİNİ ÇEK (GÜNCEL) =====
print("=" * 70)
print("🌐 EÇED DUYURU SİSTEMİNDEN İSTANBUL PROJELERİ ÇEKİLİYOR")
print("=" * 70)
print()

def scrape_ced_projeleri():
    """ced_istanbul_ulasim.json dosyasından İstanbul ulaşım projelerini yükler"""
    try:
        with open('ced_istanbul_ulasim.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        projeler = []
        istanbul_count = 0

        for proje in data:
            il_raw = proje.get("il", "")
            il_upper = il_raw.upper().replace('İ', 'I')
            sektor = proje.get("sektor", "").lower()
            alt_sektor = proje.get("alt_sektor", "").lower()
            proje_adi = proje.get("proje_adi", "")

            # İstanbul kontrolü
            if "ISTANBUL" in il_upper:
                istanbul_count += 1

                # Ulaşım anahtar kelimeleri
                ulasim_keywords = [
                    'metro','tramvay','otobüs','otobus','teleferik','köprü','kopru',
                    'tünel','tunel','yol','otopark','karayolu','raylı','rayli',
                    'sistem','hat','istasyon','ulaşım','ulasim','trafik',
                    'demiryolu','banliyö','banliyo','yht','hızlı tren','hizli tren'
                ]
                full_text = (proje_adi + " " + sektor + " " + alt_sektor).lower()

                if any(k in full_text for k in ulasim_keywords):
                    projeler.append(proje)

        # Tarihe göre sıralama (yeni → eski)
        def parse_tr(date_str):
            try: return datetime.strptime(date_str, "%d.%m.%Y")
            except: return datetime.min
        projeler.sort(key=lambda p: parse_tr(p.get('tarih','')), reverse=True)

        print("📊 JSON tarama sonucu:")
        print(f"   - İstanbul projesi: {istanbul_count}")
        print(f"   - İstanbul ulaşım: {len(projeler)}")
        print()
        return projeler

    except FileNotFoundError:
        print("❌ HATA: ced_istanbul_ulasim.json dosyası bulunamadı!")
        return []
    except json.JSONDecodeError:
        print("❌ HATA: ced_istanbul_ulasim.json bozuk!")
        return []

# EÇED projelerini çek
print("🔄 Her çalıştırmada EÇED projeleri Selenium ile güncelleniyor...")
scrape_ced_with_selenium()
print("✓ EÇED projeleri güncellendi\n")
ced_projeleri = scrape_ced_projeleri()

# ===== 2. ANALİZ VERİSİNİ YÜKLE =====
print("📂 Analiz verisi yükleniyor...")
try:
    with open(f"{CIKTI_KLASORU}/ai_analiz_verisi_39ilce_trafik.json", 'r', encoding='utf-8') as f:
        analiz_data = json.load(f)
    print("✓ Trafik verileriyle 39 ilçe analizi yüklendi")
except:
    try:
        with open(f"{CIKTI_KLASORU}/ai_analiz_verisi_39ilce.json", 'r', encoding='utf-8') as f:
            analiz_data = json.load(f)
        print("✓ 39 ilçe analizi yüklendi (trafik yok)")
    except:
        print("❌ HATA: 39 ilçe analiz dosyası bulunamadı!")
        exit(1)

print(f"  {len(analiz_data['en_sorunlu_ilceler'])} ilçe\n")

# ===== 3. ÖNCELİK GRUPLARI =====
ilceler = analiz_data['en_sorunlu_ilceler']

yuksek_oncelik = [ilce for ilce in ilceler if ilce['genel_eksiklik_skoru'] >= 70]
orta_oncelik = [ilce for ilce in ilceler if 40 <= ilce['genel_eksiklik_skoru'] < 70]
dusuk_oncelik = [ilce for ilce in ilceler if ilce['genel_eksiklik_skoru'] < 40]

print(f"📊 Öncelik Dağılımı:")
print(f"  🔴 Yüksek: {len(yuksek_oncelik)} ilçe")
print(f"  🟡 Orta: {len(orta_oncelik)} ilçe")
print(f"  🟢 Düşük: {len(dusuk_oncelik)} ilçe")
print()

# ===== 4. EÇED PROMPT HAZIRLA =====
ced_prompt_section = ""
if ced_projeleri:
    ced_prompt_section = f"""

🌐 EÇED DUYURU SİSTEMİNDEN PLANLANAN PROJELER:
{'=' * 60}
İstanbul'da ÇED sürecinde veya planlamada olan {len(ced_projeleri)} ulaşım projesi:

"""
    for idx, proje in enumerate(ced_projeleri, 1):
        ced_prompt_section += f"{idx}. {proje['proje_adi']}\n"
        ced_prompt_section += f"   - Sektör: {proje.get('sektor','')}\n"
        ced_prompt_section += f"   - Alt Sektör: {proje.get('alt_sektor','')}\n"
        ced_prompt_section += f"   - Proje Sahibi: {proje.get('proje_sahibi','')}\n"
        ced_prompt_section += f"   - Proje Türü: {proje.get('proje_turu','')}\n"
        ced_prompt_section += f"   - Durum: {proje.get('durum','')}\n"
        ced_prompt_section += f"   - Tarih: {proje.get('tarih','')}\n\n"

    # İlçe seti çıkar
    ced_ilce_set = set()
    for p in ced_projeleri:
        for name in p.get('ilce','').split(','):
            name = name.strip()
            if name:
                ced_ilce_set.add(name.upper())
    if ced_ilce_set:
        ced_prompt_section += "📍 İlçeler bazlı EÇED kapsamı: " + ", ".join(sorted(ced_ilce_set)) + "\n\n"

    ced_prompt_section += """
⚠️ ÖNEMLİ: Bu projeler zaten planlanıyor veya ÇED sürecinde!
- Aynı projeyi TEKRAR önerme
- Bu projeler varsa, "ced_durumu": "Zaten planlanıyor ✅" olarak belirt
- Tamamlayıcı projeler önerebilirsin
- Farklı alternatifler sunabilirsin

"""

# ===== 5. ANA PROMPT OLUŞTUR =====
gd = analiz_data.get('genel_durum', {})

prompt_text = f"""
Sen bir şehir planlama uzmanısın. İstanbul'un TÜM 39 İLÇESİ için ulaşım altyapısı önerileri sunacaksın.

📊 GENEL DURUM:
- Toplam Nüfus: {gd.get('toplam_nufus', 0):,}
- Raylı Sistem: {gd.get('toplam_metro_istasyon', 0)} istasyon
- Otopark: {gd.get('toplam_otopark', 313)}
- Ortalama Eksiklik: {gd.get('ortalama_eksiklik', 0):.1f}/100
"""

if 'ortalama_trafik' in gd:
    prompt_text += f"- Trafik Yoğunluğu: {gd['ortalama_trafik']:.1f}/100\n"

# EÇED projelerini ekle
prompt_text += ced_prompt_section

prompt_text += f"""

🎯 GÖREV: Tüm 39 ilçe için öneri hazırla (öncelik sırasına göre)

⚠️ KRİTİK: ÖNCELİK KURALLARI (SKOR BAZLI):
- 🔴 Yüksek Öncelik: 70-100 arası ({len(yuksek_oncelik)} ilçe)
- 🟡 Orta Öncelik: 40-70 arası ({len(orta_oncelik)} ilçe)
- 🟢 Düşük Öncelik: 0-40 arası ({len(dusuk_oncelik)} ilçe)

📋 39 İLÇE LİSTESİ:

"""

# İlçeleri gruplar halinde listele
prompt_text += f"🔴 YÜKSEK ÖNCELİK ({len(yuksek_oncelik)} İlçe):\n"
for i, ilce in enumerate(yuksek_oncelik, 1):
    prompt_text += f"{i}. {ilce.get('ilce','?')} - Nüfus: {ilce.get('nufus',0):,}, Skor: {ilce.get('genel_eksiklik_skoru',0):.1f}\n"

prompt_text += f"\n🟡 ORTA ÖNCELİK ({len(orta_oncelik)} İlçe):\n"
for i, ilce in enumerate(orta_oncelik, len(yuksek_oncelik)+1):
    prompt_text += f"{i}. {ilce.get('ilce','?')} - Nüfus: {ilce.get('nufus',0):,}, Skor: {ilce.get('genel_eksiklik_skoru',0):.1f}\n"

prompt_text += f"\n🟢 DÜŞÜK ÖNCELİK ({len(dusuk_oncelik)} İlçe):\n"
for i, ilce in enumerate(dusuk_oncelik, len(yuksek_oncelik)+len(orta_oncelik)+1):
    prompt_text += f"{i}. {ilce.get('ilce','?')} - Nüfus: {ilce.get('nufus',0):,}, Skor: {ilce.get('genel_eksiklik_skoru',0):.1f}\n"

prompt_text += """

⚠️ ÖNEMLİ KURALLAR:

1. **MALİYET (1$ = 42 TL)**:
   - Metro: ₺1.3-1.6 Milyar/km ($31-38 Milyon/km)
   - Tramvay: ₺150-200 Milyon/km ($3.5-4.7 Milyon/km)
   - Teleferik: ₺100-150 Milyon/km ($2.4-3.5 Milyon/km)
   - Yeni Arter: ₺200-300 Milyon/km ($4.7-7.1 Milyon/km)

2. **EÇED PROJELERİ** (ÖNEMLİ!):
   - Yukarıda listelenen projeler ZATEN planlanıyor
   - Aynı projeyi tekrar önerme
   - Eğer önerin zaten planlanan bir projeyle aynıysa, "ced_durumu": "Zaten planlanıyor ✅" ekle
   - Tamamlayıcı veya alternatif projeler önerebilirsin

3. **HER İLÇE İÇİN**:
   - Proje detayını yaz
   - Maliyet hesapla (₺ ve $)
   - ÖNCELİĞİ SKORUNA GÖRE BELİRLE!
   - EÇED'de varsa belirt!

JSON FORMATI (DETAYLI):
[
  {
    "ilce": "...",
    "oncelik": "Yüksek|Orta|Düşük",
    "proje_adi": "...",
    "proje_detay": "DETAYLI açıklama: Güzergah, istasyon sayısı, km, özellikler. En az 100 kelime!",
    "tahmini_maliyet": "₺X.X Milyar ($YYY Milyon)",
    "ced_durumu": "Yeni öneri" veya "Zaten planlanıyor ✅" veya "Tamamlayıcı proje",
    "beklenen_etki": "Detaylı etki analizi",
    "uygulama_suresi": "XX ay",
    "alternatif_cozumler": [
      "Alternatif 1 (maliyet - süre)",
      "Alternatif 2 (maliyet - süre)",
      "Alternatif 3 (maliyet - süre)"
    ],
    "yol_altyapisi": "Detaylı yol projeleri: Yeni arter yollar, kavşaklar, viyadükler, maliyetleriyle",
    "kisa_vade_etki": "İlk 1-2 yıl içindeki etkiler (%)",
    "orta_vade_etki": "3-5 yıl içindeki etkiler, ekonomik kazançlar",
    "uzun_vade_etki": "10 yıl sonraki vizyon, sürdürülebilirlik"
  }
]

⚠️ ÇOK ÖNEMLİ - DETAY SEVİYESİ:
- proje_detay: EN AZ 100 KELİME, spesifik güzergahlar, istasyon isimleri
- yol_altyapisi: Mutlaka ekle, her yol projesi ayrı maliyetli
- alternatif_cozumler: 3 alternatif + maliyet + süre
- kisa/orta/uzun_vade_etki: Her birini ayrı ayrı yaz, somut rakamlar ver

🎯 TÜM 39 İLÇE İÇİN ÖNERİ HAZIRLA!
ÖNCELİKLERİ MUTLAKA SKORLARA GÖRE BELİRLE!
EÇED PROJELERİNİ DİKKATE AL!
Sadece JSON döndür, açıklama ekleme.
"""

# ===== 6. CLAUDE'A GÖNDER =====
print("=" * 70)
print("🚀 Claude'a Gönderiliyor (EÇED Entegrasyonlu)...")
print("=" * 70)
print()
""" 
try:
    # Lokal importlar (güvenli): requests ve time eksikse hata çözümü
    import requests  # noqa
    import time      # noqa

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
    # OpenRouter yanıt biçimine göre güvenli erişim
    ai_response = (
        result.get('choices', [{}])[0]
              .get('message', {})
              .get('content', "")
    )
    
    usage = result.get('usage', {})
    total_tokens = usage.get('total_tokens')
    if total_tokens is not None:
        print(f"📊 Token Kullanımı: {total_tokens:,}")
    
    print("✅ Yanıt alındı!\n")
    
    # ===== 7. KAYDET =====
    print("=" * 70)
    print("💾 Kaydediliyor")
    print("=" * 70)
    print()
    
    # TXT kaydet
    with open(f"{CIKTI_KLASORU}/ai_yatirim_onerileri_v5_ced.txt", 'w', encoding='utf-8') as f:
        f.write("İSTANBUL ULAŞIM - AI ÖNERİLER v5 (EÇED ENTEGRASYONLU 🗺️)\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"EÇED'den {len(ced_projeleri)} planlanan proje dikkate alındı\n\n")
        f.write(ai_response)
    
    print("✅ TXT kaydedildi: ai_yatirim_onerileri_v5_ced.txt")
    
    # JSON parse ve kaydet
    try:
        json_text = ai_response.strip()
        # ```json bloklarını temizle
        if json_text.startswith("```"):
            lines = json_text.split('\n')
            # kod çitleri içinde ise ilk ve son satırı at
            json_text = '\n'.join(lines[1:-1])
        
        # Ek güvenlik: sadece JSON içeriğini ayıkla (ilk '[' veya '{' dan itibaren)
        first_brace = min(
            [i for i in [json_text.find('['), json_text.find('{')] if i != -1] or [0]
        )
        if first_brace > 0:
            json_text = json_text[first_brace:]
        
        ai_json = json.loads(json_text)
        if isinstance(ai_json, dict):
            ai_json = [ai_json]
        
        with open(f"{CIKTI_KLASORU}/ai_yatirim_onerileri_v5_ced.json", 'w', encoding='utf-8') as f:
            json.dump(ai_json, f, ensure_ascii=False, indent=2)
        
        print("✅ JSON kaydedildi: ai_yatirim_onerileri_v5_ced.json")
        print(f"  {len(ai_json)} ilçe önerisi\n")
        
        # ===== 8. İSTATİSTİKLER =====
        print("=" * 70)
        print("📊 PROJE İSTATİSTİKLERİ")
        print("=" * 70)
        print()
        
        # EÇED karşılaştırması
        zaten_planlanan = sum(
            1 for o in ai_json
            if 'ced_durumu' in o and 'planlan' in o.get('ced_durumu', '').lower()
        )
        yeni_oneriler = len(ai_json) - zaten_planlanan
        
        print(f"🌐 EÇED Analizi:")
        print(f"  - Zaten Planlanan: {zaten_planlanan} proje ✅")
        print(f"  - Yeni Öneri: {yeni_oneriler} proje 🆕")
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
        
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON hatası: {e}")
        print("   TXT dosyasını kontrol edin\n")

except Exception as e:
    print(f"❌ Hata: {e}\n")
    import traceback
    traceback.print_exc()
 """
print("=" * 70)
print("✅ TAMAMLANDI - EÇED ENTEGRASYONLU 🎉")
print("=" * 70)
print()
print("📌 Özellikler:")
print(f"   ✓ EÇED: {len(ced_projeleri)} proje")
print("   ✓ AI zaten planlanan projeleri dikkate alıyor")
print("   ✓ Tamamlayıcı ve alternatif öneriler")
print("   ✓ 39 ilçe tam analiz")
print()
print("💡 DAHA FAZLA EÇED PROJESİ İÇİN:")
print("   1. pip install selenium webdriver-manager")
print("   2. python scrape_ced_selenium.py")
print("   3. python ai_oneri_sistemi_v5_ced.py (tekrar)")
print("=" * 70)