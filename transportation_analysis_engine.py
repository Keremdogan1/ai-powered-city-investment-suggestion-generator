"""
İstanbul Ulaşım Projesi - Analiz Motoru v3 (39 İlçe - Tam Versiyon)
İlçe bazlı eksiklikleri tespit eder, trafik skorlarını ekler ve AI için TÜM 39 İLÇE verisini hazırlar
"""

import pandas as pd
import json
import os

# ====== DOSYA YOLLARI ======
VERI_KLASORU = r"C:\ProgrammingFile\Python\IstanbulUlasimProjesi\data\ham_veri"
CIKTI_KLASORU = r"C:\ProgrammingFile\Python\IstanbulUlasimProjesi\outputs"

print("=" * 70)
print("İSTANBUL ULAŞIM ANALİZ MOTORU v3 - 39 İLÇE TAM ANALİZ")
print("=" * 70)
print()

# ====== 1. VERİLERİ YÜKLE ======
print("📂 data yükleniyor...")

# İlçe nüfus
ilce_nufus = pd.read_excel(f"{VERI_KLASORU}/ilce_nufus_temiz.xlsx")
print(f"✓ İlçe nüfus: {len(ilce_nufus)} ilçe")

# Metro istasyonları (Manuel) - GÜNCEL CSV
try:
    ilce_metro = pd.read_csv(f"{VERI_KLASORU}/ilce_metro_manuel.csv", encoding='utf-8')
    print(f"✓ Metro datai: {len(ilce_metro)} ilçe")
    
    # Sütun adlarını kontrol et ve düzelt
    sutun_donusum = {
        'Rayil_Sistem_Istasyon': 'Metro_Istasyon_Sayisi',
        'Hatlar': 'Metro_Hatlari',
        'rayil_sistem_istasyon': 'Metro_Istasyon_Sayisi',
        'hatlar': 'Metro_Hatlari'
    }
    
    for eski, yeni in sutun_donusum.items():
        if eski in ilce_metro.columns and yeni not in ilce_metro.columns:
            ilce_metro.rename(columns={eski: yeni}, inplace=True)
            print(f"  ℹ️  Sütun güncellendi: {eski} → {yeni}")
    
    # Gerekli sütunlar yoksa oluştur
    if 'Metro_Istasyon_Sayisi' not in ilce_metro.columns:
        print("  ⚠️  Metro_Istasyon_Sayisi bulunamadı, 0 olarak ayarlanıyor")
        ilce_metro['Metro_Istasyon_Sayisi'] = 0
    
    if 'Metro_Hatlari' not in ilce_metro.columns:
        print("  ℹ️  Metro_Hatlari oluşturuluyor")
        ilce_metro['Metro_Hatlari'] = 'Yok'
    
except FileNotFoundError:
    print("❌ HATA: ilce_metro_manuel.csv bulunamadı!")
    exit(1)

# İSPARK otoparklar
ispark = pd.read_csv(f"{VERI_KLASORU}/ispark_otopark.csv", encoding='utf-8')
print(f"✓ İSPARK otoparklar: {len(ispark)} otopark")

# Trafik skorları (YENİ!)
try:
    trafik_skoru = pd.read_csv(f"{VERI_KLASORU}/ilce_trafik_skoru.csv", encoding='utf-8')
    print(f"✓ Trafik skorları: {len(trafik_skoru)} ilçe")
    trafik_var = True
except FileNotFoundError:
    print("⚠️  Trafik skoru dosyası bulunamadı (ilce_trafik_skoru.csv)")
    print("   Trafik skorları olmadan devam ediliyor...")
    trafik_var = False

print()

# ====== 2. VERİLERİ BİRLEŞTİR ======
print("🔗 data birleştiriliyor...")

# İlçe adlarını standartlaştır
ilce_nufus['Ilce_Upper'] = ilce_nufus['Ilce'].str.upper().str.strip()
ilce_metro['Ilce_Upper'] = ilce_metro['Ilce'].str.upper().str.strip()
ispark['COUNTY_UPPER'] = ispark['COUNTY_NAME'].str.upper().str.strip()

# Metro dataini birleştir
analiz_df = ilce_nufus.merge(
    ilce_metro[['Ilce_Upper', 'Metro_Istasyon_Sayisi', 'Metro_Hatlari']],
    on='Ilce_Upper',
    how='left'
)

# Metro olmayanları 0 yap
analiz_df['Metro_Istasyon_Sayisi'] = analiz_df['Metro_Istasyon_Sayisi'].fillna(0)
analiz_df['Metro_Hatlari'] = analiz_df['Metro_Hatlari'].fillna('Yok')

# Otopark dataini birleştir
otopark_ilce = ispark.groupby('COUNTY_UPPER').agg({
    'PARK_NAME': 'count',
    'CAPACITY_OF_PARK': 'sum'
}).rename(columns={
    'PARK_NAME': 'Otopark_Sayisi',
    'CAPACITY_OF_PARK': 'Toplam_Kapasite'
})

analiz_df = analiz_df.merge(
    otopark_ilce,
    left_on='Ilce_Upper',
    right_index=True,
    how='left'
)

# Otopark olmayanları 0 yap
analiz_df['Otopark_Sayisi'] = analiz_df['Otopark_Sayisi'].fillna(0)
analiz_df['Toplam_Kapasite'] = analiz_df['Toplam_Kapasite'].fillna(0)

# Trafik skorlarını birleştir (YENİ!)
if trafik_var:
    trafik_skoru['Ilce_Upper'] = trafik_skoru['Ilce'].str.upper().str.strip()
    analiz_df = analiz_df.merge(
        trafik_skoru[['Ilce_Upper', 'Trafik_Yogunluk_Skoru', 'Trafik_Aciklama']],
        on='Ilce_Upper',
        how='left'
    )
    # Trafik skoru olmayanlar için ortalama
    ortalama_trafik = analiz_df['Trafik_Yogunluk_Skoru'].mean()
    analiz_df['Trafik_Yogunluk_Skoru'] = analiz_df['Trafik_Yogunluk_Skoru'].fillna(ortalama_trafik)
    analiz_df['Trafik_Aciklama'] = analiz_df['Trafik_Aciklama'].fillna('Veri yok')

print(f"✓ {len(analiz_df)} ilçe için analiz hazır")

# Tekrar eden ilçeleri kontrol et
tekrar_edenler = analiz_df[analiz_df.duplicated(subset=['Ilce'], keep=False)]
if len(tekrar_edenler) > 0:
    print(f"⚠️  UYARI: {len(tekrar_edenler)} tekrar eden ilçe bulundu!")
    print(f"  Tekrar edenler: {tekrar_edenler['Ilce'].unique().tolist()}")
    # Tekrarları sil (ilk kaydı tut)
    analiz_df = analiz_df.drop_duplicates(subset=['Ilce'], keep='first')
    print(f"  ✓ Temizlendi: {len(analiz_df)} benzersiz ilçe kaldı")

print()

# ====== 3. EKSİKLİK SKORLARI HESAPLA ======
print("=" * 70)
print("📊 EKSİKLİK SKORU HESAPLAMALARI")
print("=" * 70)
print()

# 3.1 Metro Eksikliği
print("🚇 Metro Eksiklik Skoru...")
METRO_STANDART = 1  # istasyon / 100K kişi
analiz_df['Gerekli_Metro'] = analiz_df['Nufus'] / 100000 * METRO_STANDART
analiz_df['Metro_Eksigi'] = analiz_df['Gerekli_Metro'] - analiz_df['Metro_Istasyon_Sayisi']
analiz_df['Metro_Eksigi'] = analiz_df['Metro_Eksigi'].clip(lower=0)

analiz_df['Metro_Eksiklik_Skoru'] = (
    analiz_df['Metro_Eksigi'] / analiz_df['Gerekli_Metro'] * 100
).fillna(100).clip(0, 100)

print(f"  ✓ Ortalama metro eksikliği: {analiz_df['Metro_Eksiklik_Skoru'].mean():.1f}/100")

# 3.2 Otopark Eksikliği
print("🅿️  Otopark Eksiklik Skoru...")
OTOPARK_STANDART = 5
analiz_df['Bin_Kisi_Basina_Otopark'] = (
    analiz_df['Toplam_Kapasite'] / analiz_df['Nufus'] * 1000
)
analiz_df['Otopark_Eksiklik_Skoru'] = (
    (OTOPARK_STANDART - analiz_df['Bin_Kisi_Basina_Otopark']) / OTOPARK_STANDART * 100
).clip(0, 100)

print(f"  ✓ Ortalama otopark eksikliği: {analiz_df['Otopark_Eksiklik_Skoru'].mean():.1f}/100")

# 3.3 Genel Eksiklik Skoru (Trafik Dahil)
print("⚖️  Genel Eksiklik Skoru (Trafik AĞIRLIKLI)...")

if trafik_var:
    # Trafik skorunu normalize et (0-100)
    analiz_df['Trafik_Normalized'] = analiz_df['Trafik_Yogunluk_Skoru']
    
    # AĞIRLIKLI skor: %50 Metro + %20 Otopark + %30 Trafik
    analiz_df['Genel_Eksiklik_Skoru'] = (
        analiz_df['Metro_Eksiklik_Skoru'] * 0.5 +
        analiz_df['Otopark_Eksiklik_Skoru'] * 0.2 +
        analiz_df['Trafik_Normalized'] * 0.3
    )
    print("  ✓ Trafik datai ağırlığa dahil edildi (%30)")
else:
    # Trafik yoksa eski formül
    analiz_df['Genel_Eksiklik_Skoru'] = (
        analiz_df['Metro_Eksiklik_Skoru'] * 0.7 +
        analiz_df['Otopark_Eksiklik_Skoru'] * 0.3
    )
    print("  ⚠️  Trafik verisi yok, standart ağırlık kullanıldı")

print(f"  ✓ Ortalama genel eksiklik: {analiz_df['Genel_Eksiklik_Skoru'].mean():.1f}/100")
print()

# ====== 4. EN SORUNLU İLÇELER ======
print("=" * 70)
print("🚨 EN SORUNLU 10 İLÇE (Önizleme)")
print("=" * 70)
print()

en_sorunlu = analiz_df.nlargest(10, 'Genel_Eksiklik_Skoru')

for idx, row in en_sorunlu.iterrows():
    trafik_info = f" | Trafik: {int(row.get('Trafik_Yogunluk_Skoru', 0))}" if trafik_var else ""
    print(f"{row['Ilce']:20} | Nüfus: {int(row['Nufus']):>7,} | "
          f"Metro: {int(row['Metro_Istasyon_Sayisi']):>2} | "
          f"Otopark: {int(row['Otopark_Sayisi']):>3}{trafik_info} | "
          f"Skor: {row['Genel_Eksiklik_Skoru']:>5.1f}/100")

print()

# ====== 5. ÖZET İSTATİSTİKLER ======
print("=" * 70)
print("📈 ÖZET İSTATİSTİKLER")
print("=" * 70)
print(f"Toplam Nüfus: {analiz_df['Nufus'].sum():,}")
print(f"Toplam Metro İstasyonu: {int(analiz_df['Metro_Istasyon_Sayisi'].sum())}")
print(f"Metro Olan İlçe: {(analiz_df['Metro_Istasyon_Sayisi'] > 0).sum()}/39")
print(f"Otopark Olan İlçe: {(analiz_df['Otopark_Sayisi'] > 0).sum()}/39")
print(f"Ortalama Eksiklik Skoru: {analiz_df['Genel_Eksiklik_Skoru'].mean():.1f}/100")
if trafik_var:
    print(f"Ortalama Trafik Yoğunluğu: {analiz_df['Trafik_Yogunluk_Skoru'].mean():.1f}/100")
print()

# ====== 6. AI İÇİN VERİ HAZIRLA - TÜM 39 İLÇE ======
print("=" * 70)
print("🤖 YAPAY ZEKA İÇİN VERİ HAZIRLIĞI - TÜM 39 İLÇE")
print("=" * 70)
print()

# ÖNCELİK SIRALAMASINA GÖRE TÜM 39 İLÇE
tum_ilceler = analiz_df.sort_values('Genel_Eksiklik_Skoru', ascending=False)

ai_data = {
    "genel_durum": {
        "toplam_nufus": int(analiz_df['Nufus'].sum()),
        "toplam_metro_istasyon": int(analiz_df['Metro_Istasyon_Sayisi'].sum()),
        "toplam_otopark": int(analiz_df['Otopark_Sayisi'].sum()),
        "ortalama_eksiklik": float(analiz_df['Genel_Eksiklik_Skoru'].mean()),
        "analiz_edilen_ilce_sayisi": 39
    },
    "en_sorunlu_ilceler": []
}

# Trafik genel durumu varsa ekle
if trafik_var:
    ai_data["genel_durum"]["ortalama_trafik"] = float(analiz_df['Trafik_Yogunluk_Skoru'].mean())

# TÜM 39 İLÇEYİ EKLE
for idx, row in tum_ilceler.iterrows():
    sorunlar = []
    
    if row['Metro_Istasyon_Sayisi'] == 0:
        sorunlar.append("Metro bağlantısı YOK")
    elif row['Metro_Eksigi'] > 0:
        sorunlar.append(f"Metro istasyonu {int(row['Metro_Eksigi'])} eksik")
    
    if row['Otopark_Sayisi'] == 0:
        sorunlar.append("Hiç otopark YOK")
    elif row['Otopark_Eksiklik_Skoru'] > 50:
        sorunlar.append("Otopark kapasitesi yetersiz")
    
    # Trafik sorunu varsa ekle
    if trafik_var and row['Trafik_Yogunluk_Skoru'] > 70:
        sorunlar.append(f"Yüksek trafik yoğunluğu ({int(row['Trafik_Yogunluk_Skoru'])}/100)")
    
    ilce_dict = {
        "ilce": row['Ilce'],
        "nufus": int(row['Nufus']),
        "metro_istasyon": int(row['Metro_Istasyon_Sayisi']),
        "metro_eksigi": float(row['Metro_Eksigi']),
        "otopark_sayisi": int(row['Otopark_Sayisi']),
        "otopark_kapasitesi": int(row['Toplam_Kapasite']),
        "genel_eksiklik_skoru": float(row['Genel_Eksiklik_Skoru']),
        "sorunlar": sorunlar
    }
    
    # Trafik bilgisi varsa ekle
    if trafik_var:
        ilce_dict["trafik_yogunluk_skoru"] = int(row['Trafik_Yogunluk_Skoru'])
        ilce_dict["trafik_aciklama"] = row['Trafik_Aciklama']
    
    ai_data["en_sorunlu_ilceler"].append(ilce_dict)

# JSON kaydet
os.makedirs(CIKTI_KLASORU, exist_ok=True)

# Trafik varsa ayrı dosyaya kaydet
if trafik_var:
    with open(f"{CIKTI_KLASORU}/ai_analiz_verisi_39ilce_trafik.json", 'w', encoding='utf-8') as f:
        json.dump(ai_data, f, ensure_ascii=False, indent=2)
    print("✅ AI verisi (39 ilçe + trafik): ai_analiz_verisi_39ilce_trafik.json")
else:
    with open(f"{CIKTI_KLASORU}/ai_analiz_verisi_39ilce.json", 'w', encoding='utf-8') as f:
        json.dump(ai_data, f, ensure_ascii=False, indent=2)
    print("✅ AI verisi (39 ilçe): ai_analiz_verisi_39ilce.json")

print()
print(f"📋 Hazırlanan ilçe sayısı: {len(ai_data['en_sorunlu_ilceler'])}")
print()

# CSV rapor kaydet
rapor = analiz_df.sort_values('Genel_Eksiklik_Skoru', ascending=False)
rapor_cols = [
    'Ilce', 'Nufus', 'Metro_Istasyon_Sayisi', 'Metro_Hatlari',
    'Otopark_Sayisi', 'Toplam_Kapasite', 'Genel_Eksiklik_Skoru'
]
if trafik_var:
    rapor_cols.append('Trafik_Yogunluk_Skoru')

rapor_ozet = rapor[rapor_cols]
rapor_ozet.to_csv(f"{CIKTI_KLASORU}/ilce_eksiklik_raporu_39ilce.csv", index=False, encoding='utf-8-sig')

print("✅ CSV rapor kaydedildi: ilce_eksiklik_raporu_39ilce.csv")
print()

print("=" * 70)
print("✅ ANALİZ TAMAMLANDI - 39 İLÇE HAZIR!")
print("=" * 70)
print()
print("📌 Sonraki Adım: AI Öneri Sistemi (39 İlçe)")
print("   python ai_transportation_recommendations.py")
print("=" * 70)