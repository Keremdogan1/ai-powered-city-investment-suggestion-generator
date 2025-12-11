"""
İstanbul Sağlık Analiz Motoru
İlçe bazlı sağlık altyapısı eksiklik analizi
"""

import pandas as pd
import json
import os

BASE_DIR = r"C:\ProgrammingFile\Python\IstanbulUlasimProjesi"
VERI_KLASORU = os.path.join(BASE_DIR, "data", "ham_veri", "saglik")  # ← saglik eklendi
CIKTI_KLASORU = os.path.join(BASE_DIR, "outputs")

print("=" * 70)
print("🏥 İSTANBUL SAĞLIK ALTYAPISI ANALİZ MOTORU")
print("=" * 70)
print()

# ====== 1. VERİLERİ YÜKLE ======
print("📂 data yükleniyor...")

try:
    saglik_df = pd.read_csv(f"{VERI_KLASORU}/ilce_saglik_birlesik_tahmini.csv", encoding='utf-8')
    print(f"✅ Sağlık datai: {len(saglik_df)} ilçe")
    
    # Metadata yükle
    try:
        with open(f"{VERI_KLASORU}/veri_metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"✅ Metadata yüklendi")
        print(f"   Model: {metadata['metodoloji']}")
        print(f"   ⚠️  {metadata['uyari']}")
    except:
        print("⚠️  Metadata bulunamadı")
        
except FileNotFoundError:
    print("❌ HATA: ilce_saglik_birlesik_tahmini.csv bulunamadı!")
    print("   Önce health_data_estimation.py çalıştırın")
    exit(1)

print()

# ====== 2. STANDARTLAR VE HEDEFLER ======
print("=" * 70)
print("🎯 SAĞLIK STANDARTLARI (DSÖ ve Sağlık Bakanlığı)")
print("=" * 70)

STANDARTLAR = {
    'yatak_1000_kisi': 3.5,        # DSÖ standardı: 1000 kişiye 3.5 yatak
    'hekim_1000_kisi': 2.5,        # Hedef: 1000 kişiye 2.5 hekim
    'hastane_100k_kisi': 2.5,      # 100,000 kişiye 2.5 hastane
    'acil_erisim_max_dk': 10,      # Maksimum 10 dakika acil erişim
    'yogun_bakim_oran': 0.15,      # Toplam yatağın %15'i yoğun bakım
    'asm_5000_kisi': 1             # 5000 kişiye 1 ASM
}

for key, value in STANDARTLAR.items():
    print(f"  {key}: {value}")
print()

# ====== 3. EKSİKLİK SKORLARI HESAPLA ======
print("=" * 70)
print("📊 EKSİKLİK SKORU HESAPLAMALARI")
print("=" * 70)
print()

# 3.1 Yatak Kapasitesi Eksikliği
print("🛏️ Yatak Kapasitesi Skoru...")
saglik_df['Gerekli_Yatak'] = (saglik_df['Nufus'] / 1000) * STANDARTLAR['yatak_1000_kisi']
saglik_df['Yatak_Eksigi'] = saglik_df['Gerekli_Yatak'] - saglik_df['Toplam_Yatak']
saglik_df['Yatak_Eksigi'] = saglik_df['Yatak_Eksigi'].clip(lower=0)
saglik_df['Yatak_Eksiklik_Skoru'] = (
    saglik_df['Yatak_Eksigi'] / saglik_df['Gerekli_Yatak'] * 100
).fillna(0).clip(0, 100)

print(f"  ✅ Ortalama yatak eksikliği: {saglik_df['Yatak_Eksiklik_Skoru'].mean():.1f}/100")

# 3.2 Hekim Eksikliği
print("👨‍⚕️ Hekim Eksiklik Skoru...")
saglik_df['Gerekli_Hekim'] = (saglik_df['Nufus'] / 1000) * STANDARTLAR['hekim_1000_kisi']
saglik_df['Hekim_Eksigi'] = saglik_df['Gerekli_Hekim'] - saglik_df['Hekim_Sayisi']
saglik_df['Hekim_Eksigi'] = saglik_df['Hekim_Eksigi'].clip(lower=0)
saglik_df['Hekim_Eksiklik_Skoru'] = (
    saglik_df['Hekim_Eksigi'] / saglik_df['Gerekli_Hekim'] * 100
).fillna(0).clip(0, 100)

print(f"  ✅ Ortalama hekim eksikliği: {saglik_df['Hekim_Eksiklik_Skoru'].mean():.1f}/100")

# 3.3 Hastane Eksikliği
print("🏥 Hastane Eksiklik Skoru...")
saglik_df['Gerekli_Hastane'] = (saglik_df['Nufus'] / 100000) * STANDARTLAR['hastane_100k_kisi']
saglik_df['Hastane_Eksigi'] = saglik_df['Gerekli_Hastane'] - saglik_df['Toplam_Hastane']
saglik_df['Hastane_Eksigi'] = saglik_df['Hastane_Eksigi'].clip(lower=0)
saglik_df['Hastane_Eksiklik_Skoru'] = (
    saglik_df['Hastane_Eksigi'] / saglik_df['Gerekli_Hastane'] * 100
).fillna(0).clip(0, 100)

print(f"  ✅ Ortalama hastane eksikliği: {saglik_df['Hastane_Eksiklik_Skoru'].mean():.1f}/100")

# 3.4 Acil Erişim Skoru
print("🚑 Acil Erişim Skoru...")
saglik_df['Acil_Erisim_Skoru'] = (
    (saglik_df['Acil_Erisim_Dk'] - STANDARTLAR['acil_erisim_max_dk']) / 
    STANDARTLAR['acil_erisim_max_dk'] * 100
).clip(0, 100)

print(f"  ✅ Ortalama acil erişim sorunu: {saglik_df['Acil_Erisim_Skoru'].mean():.1f}/100")

# 3.5 ASM Eksikliği
print("🏥 ASM Eksiklik Skoru...")
saglik_df['Gerekli_ASM'] = saglik_df['Nufus'] / 5000
saglik_df['ASM_Eksigi'] = saglik_df['Gerekli_ASM'] - saglik_df['ASM_Sayisi']
saglik_df['ASM_Eksigi'] = saglik_df['ASM_Eksigi'].clip(lower=0)
saglik_df['ASM_Eksiklik_Skoru'] = (
    saglik_df['ASM_Eksigi'] / saglik_df['Gerekli_ASM'] * 100
).fillna(0).clip(0, 100)

print(f"  ✅ Ortalama ASM eksikliği: {saglik_df['ASM_Eksiklik_Skoru'].mean():.1f}/100")

# 3.6 Genel Sağlık Eksiklik Skoru
print("⚖️ Genel Sağlık Eksiklik Skoru...")
saglik_df['Genel_Saglik_Skoru'] = (
    saglik_df['Yatak_Eksiklik_Skoru'] * 0.30 +
    saglik_df['Hekim_Eksiklik_Skoru'] * 0.25 +
    saglik_df['Hastane_Eksiklik_Skoru'] * 0.20 +
    saglik_df['Acil_Erisim_Skoru'] * 0.15 +
    saglik_df['ASM_Eksiklik_Skoru'] * 0.10
)

print(f"  ✅ Ortalama genel eksiklik: {saglik_df['Genel_Saglik_Skoru'].mean():.1f}/100")
print()

# ====== 4. EN SORUNLU İLÇELER ======
print("=" * 70)
print("🚨 EN SORUNLU 15 İLÇE (Önizleme)")
print("=" * 70)
print()

en_sorunlu = saglik_df.nlargest(15, 'Genel_Saglik_Skoru')

for idx, row in en_sorunlu.iterrows():
    print(f"{row['Ilce']:20} | Nüfus: {int(row['Nufus']):>8,} | "
          f"Hastane: {int(row['Toplam_Hastane']):>2} | "
          f"Yatak: {int(row['Toplam_Yatak']):>4} | "
          f"Hekim: {int(row['Hekim_Sayisi']):>4} | "
          f"Skor: {row['Genel_Saglik_Skoru']:>5.1f}/100")

print()

# ====== 5. ÖNCELİK GRUPLARI ======
yuksek_oncelik = saglik_df[saglik_df['Genel_Saglik_Skoru'] >= 60]
orta_oncelik = saglik_df[(saglik_df['Genel_Saglik_Skoru'] >= 30) & 
                         (saglik_df['Genel_Saglik_Skoru'] < 60)]
dusuk_oncelik = saglik_df[saglik_df['Genel_Saglik_Skoru'] < 30]

print(f"📊 Öncelik Dağılımı:")
print(f"  🔴 Yüksek: {len(yuksek_oncelik)} ilçe")
print(f"  🟡 Orta: {len(orta_oncelik)} ilçe")
print(f"  🟢 Düşük: {len(dusuk_oncelik)} ilçe")
print()

# ====== 6. AI İÇİN VERİ HAZIRLA ======
print("=" * 70)
print("🤖 YAPAY ZEKA İÇİN VERİ HAZIRLANIYOR - TÜM 39 İLÇE")
print("=" * 70)
print()

# Öncelik sırasına göre tüm 39 ilçe
tum_ilceler = saglik_df.sort_values('Genel_Saglik_Skoru', ascending=False)

ai_data = {
    "genel_durum": {
        "toplam_nufus": int(saglik_df['Nufus'].sum()),
        "toplam_hastane": int(saglik_df['Toplam_Hastane'].sum()),
        "toplam_yatak": int(saglik_df['Toplam_Yatak'].sum()),
        "toplam_hekim": int(saglik_df['Hekim_Sayisi'].sum()),
        "toplam_asm": int(saglik_df['ASM_Sayisi'].sum()),
        "ortalama_eksiklik": float(saglik_df['Genel_Saglik_Skoru'].mean()),
        "analiz_edilen_ilce_sayisi": 39,
        "standartlar": STANDARTLAR,
        "veri_turu": "hibrit",  # ← Eklendi
        "uyari": "Hekim, ASM, acil servis ve ameliyathane datai bilimsel tahminlerdir"  # ← Eklendi
    },
    "en_sorunlu_ilceler": []
}

# TÜM 39 İLÇEYİ EKLE
for idx, row in tum_ilceler.iterrows():
    sorunlar = []
    
    if row['Yatak_Eksiklik_Skoru'] > 50:
        sorunlar.append(f"Yatak kapasitesi {int(row['Yatak_Eksigi'])} eksik")
    
    if row['Hekim_Eksiklik_Skoru'] > 50:
        sorunlar.append(f"Hekim sayısı {int(row['Hekim_Eksigi'])} eksik")
    
    if row['Hastane_Eksiklik_Skoru'] > 50:
        sorunlar.append(f"Hastane sayısı yetersiz")
    
    if row['Acil_Erisim_Dk'] > STANDARTLAR['acil_erisim_max_dk']:
        sorunlar.append(f"Acil erişim {int(row['Acil_Erisim_Dk'])} dk (>{STANDARTLAR['acil_erisim_max_dk']} dk)")
    
    if row['ASM_Eksiklik_Skoru'] > 50:
        sorunlar.append(f"ASM sayısı {int(row['ASM_Eksigi'])} eksik")
    
    ilce_dict = {
        "ilce": row['Ilce'],
        "nufus": int(row['Nufus']),
        "hastane_sayisi": int(row['Toplam_Hastane']),
        "devlet_hastanesi": int(row['Devlet_Hastanesi']),
        "ozel_hastane": int(row['Ozel_Hastane']),
        "egitim_hastanesi": int(row['Egitim_Hastanesi']),
        "toplam_yatak": int(row['Toplam_Yatak']),
        "yogun_bakim": int(row['Yogun_Bakim']),
        "yatak_eksigi": float(row['Yatak_Eksigi']),
        "hekim_sayisi": int(row['Hekim_Sayisi']),
        "uzman_hekim": int(row['Uzman_Hekim']),
        "pratisyen": int(row['Pratisyen']),
        "hekim_eksigi": float(row['Hekim_Eksigi']),
        "acil_erisim_dk": int(row['Acil_Erisim_Dk']),
        "asm_sayisi": int(row['ASM_Sayisi']),
        "asm_eksigi": float(row['ASM_Eksigi']),
        "genel_saglik_skoru": float(row['Genel_Saglik_Skoru']),
        "sorunlar": sorunlar
    }
    
    ai_data["en_sorunlu_ilceler"].append(ilce_dict)

# JSON kaydet
os.makedirs(CIKTI_KLASORU, exist_ok=True)
with open(f"{CIKTI_KLASORU}/ai_analiz_saglik_39ilce.json", 'w', encoding='utf-8') as f:
    json.dump(ai_data, f, ensure_ascii=False, indent=2)

print(f"✅ AI verisi (39 ilçe): ai_analiz_saglik_39ilce.json")
print(f"📋 Hazırlanan ilçe sayısı: {len(ai_data['en_sorunlu_ilceler'])}")
print()

# CSV rapor kaydet
rapor = saglik_df.sort_values('Genel_Saglik_Skoru', ascending=False)
rapor_cols = [
    'Ilce', 'Nufus', 'Toplam_Hastane', 'Toplam_Yatak', 'Hekim_Sayisi',
    'Acil_Erisim_Dk', 'ASM_Sayisi', 'Genel_Saglik_Skoru'
]
rapor_ozet = rapor[rapor_cols]
rapor_ozet.to_csv(f"{CIKTI_KLASORU}/ilce_saglik_raporu_39ilce.csv", 
                  index=False, encoding='utf-8-sig')

print("✅ CSV rapor kaydedildi: ilce_saglik_raporu_39ilce.csv")
print()

print("=" * 70)
print("✅ ANALİZ TAMAMLANDI - 39 İLÇE HAZIR!")
print("=" * 70)
print()
print("📌 Sonraki Adım: AI Öneri Sistemi (39 İlçe)")
print("   python ai_health_recommendations.py")
print("=" * 70)