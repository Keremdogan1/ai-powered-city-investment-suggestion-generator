"""
İstanbul Çevre Analiz Motoru
İlçe bazlı yeşil alan ve park altyapısı eksiklik analizi
"""

import pandas as pd
import json
import os
import numpy as np

BASE_DIR = r"C:\ProgrammingFile\Python\IstanbulUlasimProjesi"
VERI_KLASORU = os.path.join(BASE_DIR, "data", "ham_veri")
CIKTI_KLASORU = os.path.join(BASE_DIR, "outputs")

print("=" * 70)
print("🌳 İSTANBUL ÇEVRE ALTYAPISI ANALİZ MOTORU")
print("=" * 70)
print()

# ====== 1. VERİLERİ YÜKLE ======
print("📂 data yükleniyor...")

try:
    # Nüfus verisi
    nufus_df = pd.read_excel(f"{VERI_KLASORU}/ilce_nufus_temiz.xlsx")
    print(f"✅ Nüfus datai: {len(nufus_df)} ilçe")
    
    # İlçe adlarını standartlaştır
    nufus_df['Ilce_Upper'] = nufus_df['Ilce'].str.upper().str.strip()
    
except FileNotFoundError:
    print("❌ HATA: ilce_nufus_temiz.xlsx bulunamadı!")
    exit(1)

# GeoJSON dataini yükle (İlçe bazlı yeşil alan datai)
geojson_dosya = os.path.join(VERI_KLASORU, "yaysis_mahal_geo_data.geojson")
geojson_data = None

if os.path.exists(geojson_dosya):
    try:
        with open(geojson_dosya, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        features = geojson_data.get('features', [])
        print(f"✅ GeoJSON datai yüklendi: {len(features)} feature")
    except Exception as e:
        print(f"⚠️  GeoJSON dosyası okunamadı: {e}")
        geojson_data = None

# Excel dosyası - TÜM SEKMELERİ KULLAN
yesil_alan_dosya = os.path.join(VERI_KLASORU, "_yesil_alanlar_datai.xlsx")
excel_sheets_data = {}

if os.path.exists(yesil_alan_dosya):
    try:
        xls = pd.ExcelFile(yesil_alan_dosya)
        print(f"✅ Excel dosyası açıldı: {len(xls.sheet_names)} sekme bulundu")
        
        # Tüm sekmeleri yükle
        for sheet_name in xls.sheet_names:
            try:
                df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
                excel_sheets_data[sheet_name] = df_sheet
                print(f"   ✓ Sekme '{sheet_name}': {len(df_sheet)} satır")
            except Exception as e:
                print(f"   ⚠️  Sekme '{sheet_name}' okunamadı: {e}")
        
        # Ana sekme (ilk sekme) referans için
        yesil_alan_df = excel_sheets_data.get(xls.sheet_names[0])
        
    except Exception as e:
        print(f"⚠️  Excel dosyası okunamadı: {e}")
        yesil_alan_df = None
        excel_sheets_data = {}
else:
    yesil_alan_df = None
    excel_sheets_data = {}

# Park ve yeşil alan verisi - district_green_space_summary.csv'den oku
green_space_csv = None
green_space_dosya = os.path.join(VERI_KLASORU, "district_green_space_summary.csv")

if os.path.exists(green_space_dosya):
    try:
        green_space_csv = pd.read_csv(green_space_dosya, encoding='utf-8')
        print(f"✅ Yeşil alan özet datai: {len(green_space_csv)} ilçe")
        print(f"   Sütunlar: {list(green_space_csv.columns)}")
    except Exception as e:
        print(f"⚠️  Yeşil alan datai okunamadı: {e}")

# CSV dosyalarını kontrol et (cevre klasöründe - yedek)
cevre_klasoru = os.path.join(VERI_KLASORU, "cevre")
park_csv = None
yesil_alan_csv = None

if os.path.exists(cevre_klasoru):
    park_csv_dosya = os.path.join(cevre_klasoru, "park_bahce_yesil_alanlar.csv")
    yesil_alan_csv_dosya = os.path.join(cevre_klasoru, "parklar_yesil_alanlar.csv")
    
    if os.path.exists(park_csv_dosya):
        try:
            park_csv = pd.read_csv(park_csv_dosya, encoding='utf-8')
            print(f"✅ Park CSV datai: {len(park_csv)} kayıt")
            print(f"   Sütunlar: {list(park_csv.columns)}")
        except Exception as e:
            print(f"⚠️  Park CSV okunamadı: {e}")
    
    if os.path.exists(yesil_alan_csv_dosya):
        try:
            yesil_alan_csv = pd.read_csv(yesil_alan_csv_dosya, encoding='utf-8')
            print(f"✅ Yeşil alan CSV datai: {len(yesil_alan_csv)} kayıt")
            print(f"   Sütunlar: {list(yesil_alan_csv.columns)}")
        except Exception as e:
            print(f"⚠️  Yeşil alan CSV okunamadı: {e}")

print()

# ====== 2. VERİYİ İŞLE VE BİRLEŞTİR ======
print("=" * 70)
print("🔗 VERİLERİ İŞLEME VE BİRLEŞTİRME")
print("=" * 70)
print()

# Ana dataframe'i oluştur
cevre_df = nufus_df[['Ilce', 'Nufus', 'Ilce_Upper']].copy()

# İlçe bazlı park ve yeşil alan dataini topla
# CSV'den veri varsa kullan, yoksa tahmin yap

# Park sayısı için ilçe eşleştirmesi
ilce_park_sayisi = {}
ilce_yesil_alan_m2 = {}
ilce_yesil_alan_feature_count = {}

# GeoJSON'dan ilçe bazlı datai çıkar
if geojson_data is not None:
    print("📊 GeoJSON'dan ilçe bazlı data işleniyor...")
    features = geojson_data.get('features', [])
    
    for feat in features:
        props = feat.get('properties', {})
        district = props.get('ILCE', '')
        feature_type = props.get('TUR', '')
        
        if district:
            district_upper = district.upper().strip()
            
            # Toplam feature sayısı
            if district_upper not in ilce_yesil_alan_feature_count:
                ilce_yesil_alan_feature_count[district_upper] = 0
            ilce_yesil_alan_feature_count[district_upper] += 1
            
            # Park sayısı (sadece "Park" türündeki feature'lar)
            if 'park' in feature_type.lower():
                if district_upper not in ilce_park_sayisi:
                    ilce_park_sayisi[district_upper] = 0
                ilce_park_sayisi[district_upper] += 1
    
    print(f"✅ {len(ilce_yesil_alan_feature_count)} ilçe için GeoJSON verisi işlendi")
    print(f"✅ {len(ilce_park_sayisi)} ilçe için park verisi bulundu")

# CSV datainden park sayısını çıkar (GeoJSON'dan daha detaylıysa kullan)
if green_space_csv is not None:
    print("📊 District green space CSV'den park datai işleniyor...")
    # Sütunları kontrol et
    if 'District' in green_space_csv.columns and 'Total_Features' in green_space_csv.columns:
        for _, row in green_space_csv.iterrows():
            district = str(row['District']).upper().strip()
            total_features = int(row['Total_Features'])
            ilce_park_sayisi[district] = total_features
        print(f"✅ {len(ilce_park_sayisi)} ilçe için park verisi bulundu (district_green_space_summary.csv)")
    else:
        print(f"⚠️  CSV formatı beklenmediği gibi. Sütunlar: {green_space_csv.columns.tolist()}")

if park_csv is not None:
    print("📊 CSV'den park datai işleniyor...")
    # İlçe sütununu bul
    ilce_sutunlari = [col for col in park_csv.columns if 'ilce' in col.lower() or 'ilçe' in col.lower()]
    
    if ilce_sutunlari:
        ilce_sutun = ilce_sutunlari[0]
        park_csv['Ilce_Upper'] = park_csv[ilce_sutun].str.upper().str.strip()
        park_ilce = park_csv.groupby('Ilce_Upper').size().reset_index(name='Park_Sayisi')
        
        for _, row in park_ilce.iterrows():
            ilce_park_sayisi[row['Ilce_Upper']] = int(row['Park_Sayisi'])
        
        print(f"✅ {len(ilce_park_sayisi)} ilçe için park verisi bulundu")

# Yeşil alan CSV'den veri çıkar
if yesil_alan_csv is not None:
    print("📊 CSV'den yeşil alan datai işleniyor...")
    ilce_sutunlari = [col for col in yesil_alan_csv.columns if 'ilce' in col.lower() or 'ilçe' in col.lower()]
    
    if ilce_sutunlari:
        ilce_sutun = ilce_sutunlari[0]
        # Alan sütununu bul (m2, alan, metrekare vb.)
        alan_sutunlari = [col for col in yesil_alan_csv.columns if 'alan' in col.lower() or 'm2' in col.lower() or 'metrekare' in col.lower()]
        
        if alan_sutunlari:
            alan_sutun = alan_sutunlari[0]
            yesil_alan_csv['Ilce_Upper'] = yesil_alan_csv[ilce_sutun].str.upper().str.strip()
            yesil_ilce = yesil_alan_csv.groupby('Ilce_Upper')[alan_sutun].sum().reset_index(name='Yesil_Alan_M2')
            
            for _, row in yesil_ilce.iterrows():
                ilce_yesil_alan_m2[row['Ilce_Upper']] = float(row['Yesil_Alan_M2'])
            
            print(f"✅ {len(ilce_yesil_alan_m2)} ilçe için yeşil alan verisi bulundu")

# Eksik data için tahmin yap
print("📊 Eksik data için tahmin yapılıyor...")

# Excel sekmelerinden veri çıkar
ortalama_m2_per_kisi = 7.78  # Varsayılan değer
toplam_yesil_alan_m2_referans = None
park_sayisi_excel = None
agac_sayisi_2022 = None

# Ana sekmeden genel datai çıkar
if yesil_alan_df is not None and len(yesil_alan_df) > 0:
    for col in yesil_alan_df.columns:
        col_str = str(col).lower()
        if 'kişi başına' in col_str or 'kisi basina' in col_str:
            try:
                numeric_values = pd.to_numeric(yesil_alan_df[col], errors='coerce').dropna()
                if len(numeric_values) > 0:
                    ortalama_m2_per_kisi = float(numeric_values.iloc[-1])
                    print(f"   Excel'den kişi başına yeşil alan: {ortalama_m2_per_kisi} m²")
            except:
                pass
        if 'bakım' in col_str or 'bakim' in col_str:
            try:
                numeric_values = pd.to_numeric(yesil_alan_df[col], errors='coerce').dropna()
                if len(numeric_values) > 0:
                    toplam_yesil_alan_m2_referans = float(numeric_values.iloc[-1])
                    print(f"   Excel'den toplam yeşil alan: {toplam_yesil_alan_m2_referans:,.0f} m²")
            except:
                pass

# "Yeşil Alanlar Sayısı" sekmesinden park sayısını çıkar
if 'Yeşil Alanlar Sayısı' in excel_sheets_data or 'Yesil Alanlar Sayisi' in excel_sheets_data:
    sheet_name = 'Yeşil Alanlar Sayısı' if 'Yeşil Alanlar Sayısı' in excel_sheets_data else 'Yesil Alanlar Sayisi'
    park_df = excel_sheets_data[sheet_name]
    if 'Park' in park_df.values or 'park' in str(park_df.values).lower():
        try:
            # Park satırını bul
            park_row = park_df[park_df.iloc[:, 0].astype(str).str.contains('Park', case=False, na=False)]
            if len(park_row) > 0:
                park_sayisi_excel = int(park_row.iloc[0, 1])
                print(f"   Excel'den toplam park sayısı: {park_sayisi_excel}")
        except:
            pass

# "2022 Yılı Dikilen Ağaç Sayısı" sekmesinden ağaç sayısını çıkar
for sheet_name in excel_sheets_data.keys():
    if 'ağaç' in sheet_name.lower() or 'agac' in sheet_name.lower() or 'dikilen' in sheet_name.lower():
        agac_df = excel_sheets_data[sheet_name]
        try:
            # Sayısal değerleri bul
            numeric_cols = agac_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                agac_sayisi_2022 = int(agac_df[numeric_cols[0]].sum())
                print(f"   Excel'den 2022 dikilen ağaç sayısı: {agac_sayisi_2022:,}")
                break
        except:
            pass

# GeoJSON feature sayısına göre yeşil alan tahmini
if geojson_data:
    total_features = len(geojson_data.get('features', []))
    
    # Feature başına ortalama alan (tahmin)
    if toplam_yesil_alan_m2_referans and total_features > 0:
        ortalama_feature_alan_m2 = toplam_yesil_alan_m2_referans / total_features
        print(f"   Feature başına ortalama alan (tahmin): {ortalama_feature_alan_m2:,.0f} m²")
    else:
        # Varsayılan: Her feature için ortalama 5000 m² (tahmin)
        ortalama_feature_alan_m2 = 5000
        print(f"   Varsayılan feature alanı kullanılıyor: {ortalama_feature_alan_m2:,.0f} m²")

# Her ilçe için park ve yeşil alan hesaplama/tahmin
for idx, row in cevre_df.iterrows():
    ilce_upper = row['Ilce_Upper']
    nufus = row['Nufus']
    
    # Park sayısı (GeoJSON'dan veya tahmin)
    if ilce_upper not in ilce_park_sayisi:
        # GeoJSON feature sayısına göre tahmin
        if ilce_upper in ilce_yesil_alan_feature_count:
            # Feature sayısının %30'u park olarak tahmin edilir
            tahmini_park = max(1, int(ilce_yesil_alan_feature_count[ilce_upper] * 0.3))
        else:
            # 1000 kişiye 0.5 park standardı
            tahmini_park = max(1, int((nufus / 1000) * 0.5))
        ilce_park_sayisi[ilce_upper] = tahmini_park
    
    # Yeşil alan m² (GeoJSON feature sayısına göre veya tahmin)
    if ilce_upper not in ilce_yesil_alan_m2:
        if ilce_upper in ilce_yesil_alan_feature_count and 'ortalama_feature_alan_m2' in locals():
            # GeoJSON feature sayısı * ortalama feature alanı
            tahmini_yesil_alan = ilce_yesil_alan_feature_count[ilce_upper] * ortalama_feature_alan_m2
        else:
            # Ortalama m²/kişi ile tahmin
            tahmini_yesil_alan = nufus * ortalama_m2_per_kisi
        ilce_yesil_alan_m2[ilce_upper] = tahmini_yesil_alan

# DataFrame'e ekle
cevre_df['Park_Sayisi'] = cevre_df['Ilce_Upper'].map(ilce_park_sayisi).fillna(1)
cevre_df['Yesil_Alan_M2'] = cevre_df['Ilce_Upper'].map(ilce_yesil_alan_m2).fillna(cevre_df['Nufus'] * ortalama_m2_per_kisi)

# Kişi başına yeşil alan
cevre_df['Kisi_Basina_Yesil_M2'] = cevre_df['Yesil_Alan_M2'] / cevre_df['Nufus']

# Hektar cinsinden yeşil alan
cevre_df['Yesil_Alan_Hektar'] = cevre_df['Yesil_Alan_M2'] / 10000

print(f"✅ Veri işleme tamamlandı: {len(cevre_df)} ilçe")
print()

# ====== 3. STANDARTLAR VE HEDEFLER ======
print("=" * 70)
print("🎯 ÇEVRE STANDARTLARI (DSÖ ve İBB)")
print("=" * 70)

STANDARTLAR = {
    'yesil_alan_min_m2_per_kisi': 10.0,      # DSÖ minimum: 10 m²/kişi
    'yesil_alan_ideal_m2_per_kisi': 15.0,   # İdeal: 15 m²/kişi
    'park_1000_kisi': 0.5,                   # 1000 kişiye 0.5 park
    'park_min_alan_m2': 5000,                # Minimum park alanı: 5000 m²
    'yesil_alan_min_hektar_per_100k': 100    # 100,000 kişiye 100 hektar
}

for key, value in STANDARTLAR.items():
    print(f"  {key}: {value}")
print()

# ====== 4. EKSİKLİK SKORLARI HESAPLA ======
print("=" * 70)
print("📊 EKSİKLİK SKORU HESAPLAMALARI")
print("=" * 70)
print()

# 4.1 Yeşil Alan Eksikliği
print("🌳 Yeşil Alan Eksiklik Skoru...")
cevre_df['Gerekli_Yesil_Alan_M2'] = cevre_df['Nufus'] * STANDARTLAR['yesil_alan_min_m2_per_kisi']
cevre_df['Yesil_Alan_Eksigi_M2'] = cevre_df['Gerekli_Yesil_Alan_M2'] - cevre_df['Yesil_Alan_M2']
cevre_df['Yesil_Alan_Eksigi_M2'] = cevre_df['Yesil_Alan_Eksigi_M2'].clip(lower=0)
cevre_df['Yesil_Alan_Eksiklik_Skoru'] = (
    cevre_df['Yesil_Alan_Eksigi_M2'] / cevre_df['Gerekli_Yesil_Alan_M2'] * 100
).fillna(0).clip(0, 100)

print(f"  ✅ Ortalama yeşil alan eksikliği: {cevre_df['Yesil_Alan_Eksiklik_Skoru'].mean():.1f}/100")

# 4.2 Park Eksikliği
print("🏞️ Park Eksiklik Skoru...")
cevre_df['Gerekli_Park_Sayisi'] = (cevre_df['Nufus'] / 1000) * STANDARTLAR['park_1000_kisi']
cevre_df['Park_Eksigi'] = cevre_df['Gerekli_Park_Sayisi'] - cevre_df['Park_Sayisi']
cevre_df['Park_Eksigi'] = cevre_df['Park_Eksigi'].clip(lower=0)
cevre_df['Park_Eksiklik_Skoru'] = (
    cevre_df['Park_Eksigi'] / cevre_df['Gerekli_Park_Sayisi'] * 100
).fillna(0).clip(0, 100)

print(f"  ✅ Ortalama park eksikliği: {cevre_df['Park_Eksiklik_Skoru'].mean():.1f}/100")

# 4.3 Kişi Başına Yeşil Alan Skoru
print("📏 Kişi Başına Yeşil Alan Skoru...")
cevre_df['Kisi_Basina_Eksiklik_Skoru'] = (
    (STANDARTLAR['yesil_alan_min_m2_per_kisi'] - cevre_df['Kisi_Basina_Yesil_M2']) / 
    STANDARTLAR['yesil_alan_min_m2_per_kisi'] * 100
).clip(0, 100)

print(f"  ✅ Ortalama kişi başına eksiklik: {cevre_df['Kisi_Basina_Eksiklik_Skoru'].mean():.1f}/100")

# 4.4 Genel Çevre Eksiklik Skoru
print("⚖️ Genel Çevre Eksiklik Skoru...")
cevre_df['Genel_Cevre_Skoru'] = (
    cevre_df['Yesil_Alan_Eksiklik_Skoru'] * 0.50 +
    cevre_df['Park_Eksiklik_Skoru'] * 0.30 +
    cevre_df['Kisi_Basina_Eksiklik_Skoru'] * 0.20
)

print(f"  ✅ Ortalama genel eksiklik: {cevre_df['Genel_Cevre_Skoru'].mean():.1f}/100")
print()

# ====== 5. EN SORUNLU İLÇELER ======
print("=" * 70)
print("🚨 EN SORUNLU 15 İLÇE (Önizleme)")
print("=" * 70)
print()

en_sorunlu = cevre_df.nlargest(15, 'Genel_Cevre_Skoru')

for idx, row in en_sorunlu.iterrows():
    print(f"{row['Ilce']:20} | Nüfus: {int(row['Nufus']):>8,} | "
          f"Park: {int(row['Park_Sayisi']):>3} | "
          f"m²/kişi: {row['Kisi_Basina_Yesil_M2']:>5.2f} | "
          f"Skor: {row['Genel_Cevre_Skoru']:>5.1f}/100")

print()

# ====== 6. ÖNCELİK GRUPLARI ======
yuksek_oncelik = cevre_df[cevre_df['Genel_Cevre_Skoru'] >= 60]
orta_oncelik = cevre_df[(cevre_df['Genel_Cevre_Skoru'] >= 30) & 
                        (cevre_df['Genel_Cevre_Skoru'] < 60)]
dusuk_oncelik = cevre_df[cevre_df['Genel_Cevre_Skoru'] < 30]

print(f"📊 Öncelik Dağılımı:")
print(f"  🔴 Yüksek: {len(yuksek_oncelik)} ilçe")
print(f"  🟡 Orta: {len(orta_oncelik)} ilçe")
print(f"  🟢 Düşük: {len(dusuk_oncelik)} ilçe")
print()

# ====== 7. AI İÇİN VERİ HAZIRLA ======
print("=" * 70)
print("🤖 YAPAY ZEKA İÇİN VERİ HAZIRLANIYOR - TÜM 39 İLÇE")
print("=" * 70)
print()

# Öncelik sırasına göre tüm 39 ilçe
tum_ilceler = cevre_df.sort_values('Genel_Cevre_Skoru', ascending=False)

# Genel durum hesapla
toplam_nufus = int(cevre_df['Nufus'].sum())
toplam_park = int(cevre_df['Park_Sayisi'].sum())
toplam_yesil_alan_m2 = float(cevre_df['Yesil_Alan_M2'].sum())
toplam_yesil_alan_hektar = float(cevre_df['Yesil_Alan_Hektar'].sum())
ortalama_m2_per_kisi = float(cevre_df['Kisi_Basina_Yesil_M2'].mean())

ai_data = {
    "genel_durum": {
        "toplam_nufus": toplam_nufus,
        "toplam_park": toplam_park,
        "toplam_yesil_alan_m2": toplam_yesil_alan_m2,
        "toplam_yesil_alan_hektar": toplam_yesil_alan_hektar,
        "ortalama_m2_per_kisi": ortalama_m2_per_kisi,
        "ortalama_eksiklik": float(cevre_df['Genel_Cevre_Skoru'].mean()),
        "analiz_edilen_ilce_sayisi": 39,
        "standartlar": STANDARTLAR,
        "veri_durumu": "kısmi_tahmin" if len(ilce_park_sayisi) < 20 else "gerçek_veri",
        "uyari": "Bazı ilçeler için park ve yeşil alan datai tahmin edilmiştir"
    },
    "en_sorunlu_ilceler": []
}

# TÜM 39 İLÇEYİ EKLE
for idx, row in tum_ilceler.iterrows():
    sorunlar = []
    
    if row['Yesil_Alan_Eksiklik_Skoru'] > 50:
        sorunlar.append(f"Yeşil alan {int(row['Yesil_Alan_Eksigi_M2']/10000):.1f} hektar eksik")
    
    if row['Park_Eksiklik_Skoru'] > 50:
        sorunlar.append(f"Park sayısı {int(row['Park_Eksigi'])} eksik")
    
    if row['Kisi_Basina_Yesil_M2'] < STANDARTLAR['yesil_alan_min_m2_per_kisi']:
        sorunlar.append(f"Kişi başına yeşil alan {row['Kisi_Basina_Yesil_M2']:.2f} m² (min: {STANDARTLAR['yesil_alan_min_m2_per_kisi']} m²)")
    
    ilce_dict = {
        "ilce": row['Ilce'],
        "nufus": int(row['Nufus']),
        "park_sayisi": int(row['Park_Sayisi']),
        "yesil_alan_m2": float(row['Yesil_Alan_M2']),
        "yesil_alan_hektar": float(row['Yesil_Alan_Hektar']),
        "kisi_basina_yesil_m2": float(row['Kisi_Basina_Yesil_M2']),
        "yesil_alan_eksigi_m2": float(row['Yesil_Alan_Eksigi_M2']),
        "park_eksigi": float(row['Park_Eksigi']),
        "genel_cevre_skoru": float(row['Genel_Cevre_Skoru']),
        "sorunlar": sorunlar
    }
    
    ai_data["en_sorunlu_ilceler"].append(ilce_dict)

# JSON kaydet
os.makedirs(CIKTI_KLASORU, exist_ok=True)
with open(f"{CIKTI_KLASORU}/ai_analiz_cevre_39ilce.json", 'w', encoding='utf-8') as f:
    json.dump(ai_data, f, ensure_ascii=False, indent=2)

print(f"✅ AI verisi (39 ilçe): ai_analiz_cevre_39ilce.json")
print(f"📋 Hazırlanan ilçe sayısı: {len(ai_data['en_sorunlu_ilceler'])}")
print()

# CSV rapor kaydet
rapor = cevre_df.sort_values('Genel_Cevre_Skoru', ascending=False)
rapor_cols = [
    'Ilce', 'Nufus', 'Park_Sayisi', 'Yesil_Alan_Hektar', 
    'Kisi_Basina_Yesil_M2', 'Genel_Cevre_Skoru'
]
rapor_ozet = rapor[rapor_cols]
rapor_ozet.to_csv(f"{CIKTI_KLASORU}/ilce_cevre_raporu_39ilce.csv", 
                  index=False, encoding='utf-8-sig')

print("✅ CSV rapor kaydedildi: ilce_cevre_raporu_39ilce.csv")
print()

print("=" * 70)
print("✅ ANALİZ TAMAMLANDI - 39 İLÇE HAZIR!")
print("=" * 70)
print()
print("📌 Sonraki Adım: AI Öneri Sistemi (39 İlçe)")
print("   python ai_environment_recommendations.py")
print("=" * 70)

