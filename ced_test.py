"""
ÇED Entegrasyonu Test Script (Geliştirilmiş)
Sayfa yapısını detaylı analiz eder ve HTML'i kaydeder
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import urllib3

# SSL uyarısını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_ced_connection():
    """ÇED sitesine bağlantıyı test et"""
    print("=" * 70)
    print("🌐 ÇED DUYURU SİSTEMİ DETAYLI ANALİZ")
    print("=" * 70)
    print()
    
    print("1️⃣ ÇED sitesine bağlanılıyor...")
    
    base_url = "https://eced-duyuru.csb.gov.tr/eced-prod/duyurular.xhtml"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        print(f"✅ Bağlantı başarılı! (Status: {response.status_code})")
        print(f"   Sayfa boyutu: {len(response.content)} bytes")
        print()
        
        # HTML'i kaydet
        with open('ced_page_source.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 HTML kaydedildi: ced_page_source.html")
        print()
        
        return response
        
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return None

def deep_analyze_structure(response):
    """Sayfa yapısını derinlemesine analiz et"""
    print("2️⃣ Detaylı sayfa analizi...")
    print()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # TÜM metin içeriği
    all_text = soup.get_text(separator='\n', strip=True)
    
    # "Duyuru" kelimesini içeren satırları bul
    print("📋 'Duyuru' İçeren Satırlar:")
    duyuru_lines = [line for line in all_text.split('\n') if 'duyuru' in line.lower() and len(line) > 10]
    for i, line in enumerate(duyuru_lines[:10], 1):
        print(f"   {i}. {line[:80]}")
    print()
    
    # Tablo içeriğini detaylı incele
    print("📊 Tablo Detay Analizi:")
    tables = soup.find_all('table')
    for t_idx, table in enumerate(tables, 1):
        print(f"\n   Tablo {t_idx}:")
        rows = table.find_all('tr')
        print(f"   - Satır sayısı: {len(rows)}")
        
        # İlk birkaç satırı göster
        for r_idx, row in enumerate(rows[:5], 1):
            cells = row.find_all(['td', 'th'])
            if cells:
                cell_texts = [cell.get_text(strip=True)[:30] for cell in cells]
                print(f"     Satır {r_idx}: {' | '.join(cell_texts)}")
    
    print()
    
    # Link analizi
    print("🔗 Link Analizi:")
    links = soup.find_all('a', href=True)
    duyuru_links = [link for link in links if 'duyuru' in link.get('href', '').lower()]
    print(f"   Toplam link: {len(links)}")
    print(f"   Duyuru linkleri: {len(duyuru_links)}")
    if duyuru_links:
        print(f"   Örnek link: {duyuru_links[0].get_text(strip=True)[:50]}")
    print()
    
    # ID ve Class içeren div'leri bul
    print("🎯 Önemli Container'lar:")
    important_divs = soup.find_all('div', id=True)
    print(f"   ID'li div sayısı: {len(important_divs)}")
    for div in important_divs[:5]:
        print(f"   - ID: {div.get('id')} | Class: {div.get('class')}")
    
    print()
    
    # Form analizi
    print("📝 Form Detayları:")
    forms = soup.find_all('form')
    for f_idx, form in enumerate(forms, 1):
        print(f"\n   Form {f_idx}:")
        print(f"   - ID: {form.get('id')}")
        print(f"   - Action: {form.get('action')}")
        
        # Form içindeki input'ları bul
        inputs = form.find_all(['input', 'select'])
        print(f"   - Input sayısı: {len(inputs)}")
        for inp in inputs[:3]:
            print(f"     • {inp.get('name')} ({inp.get('type')})")
    
    print()
    return soup

def find_actual_project_data(soup):
    """Gerçek proje verilerini bul"""
    print("3️⃣ Proje verilerini arama...")
    print()
    
    # Ana tablo: form:duyurTable_data
    print("   📊 Strateji: Ana tablo (form:duyurTable_data)")
    main_table = soup.find('tbody', id='form:duyurTable_data')
    
    if not main_table:
        print("   ❌ Ana tablo bulunamadı")
        return []
    
    rows = main_table.find_all('tr', class_='ui-widget-content')
    print(f"   ✓ {len(rows)} proje satırı bulundu")
    
    # İlk 5 satırı detaylı analiz et
    projeler = []
    for idx, row in enumerate(rows[:5], 1):
        cells = row.find_all('td', role='gridcell')
        
        if len(cells) >= 9:
            print(f"\n   📄 Proje {idx}:")
            print(f"   - Hücre sayısı: {len(cells)}")
            
            # Tablo yapısı:
            # 0: İl, 1: İlçe, 2: Proje Adı, 3: Proje Sahibi
            # 4: Sektör, 5: Alt Sektör, 6: Karar Tipi, 7: Tarih, 8: Proje Türü
            
            il = cells[0].get_text(strip=True)
            ilce = cells[1].get_text(strip=True)
            proje_adi = cells[2].get_text(strip=True)
            firma = cells[3].get_text(strip=True)
            sektor = cells[4].get_text(strip=True)
            alt_sektor = cells[5].get_text(strip=True)
            
            print(f"     İl: {il}")
            print(f"     İlçe: {ilce}")
            print(f"     Proje: {proje_adi[:80]}...")
            print(f"     Firma: {firma[:50]}...")
            print(f"     Sektör: {sektor}")
            
            # Proje objesi oluştur
            proje = {
                "veri_kaynagi": "ana_tablo",
                "il": il,
                "ilce": ilce,
                "proje_adi": proje_adi,
                "firma": firma,
                "sektor": sektor,
                "alt_sektor": alt_sektor,
                "karar_tipi": cells[6].get_text(strip=True),
                "tarih": cells[7].get_text(strip=True),
                "proje_turu": cells[8].get_text(strip=True),
                "hucre_sayisi": len(cells)  # ← doğru ekleme
            }

            
            # İstanbul kontrolü
            proje["istanbul"] = il.upper() == 'İSTANBUL' or il.upper() == 'ISTANBUL'
            
            # Kategori tespiti
            full_text = (proje_adi + " " + sektor + " " + alt_sektor).lower()
            if any(k in full_text for k in ['metro', 'tramvay', 'yol', 'köprü', 'ulaşım', 'ulasim']):
                proje["olasi_kategori"] = "ulasim"
            elif any(k in full_text for k in ['hastane', 'sağlık', 'saglik', 'klinik']):
                proje["olasi_kategori"] = "saglik"
            elif any(k in full_text for k in ['atık', 'atik', 'çevre', 'cevre', 'arıtma', 'aritma']):
                proje["olasi_kategori"] = "cevre"
            else:
                proje["olasi_kategori"] = "diger"
            
            if proje["istanbul"]:
                print(f"     ✓ İSTANBUL PROJESİ!")
            
            if proje["olasi_kategori"] != "diger":
                print(f"     📂 Kategori: {proje['olasi_kategori']}")
            
            projeler.append(proje)
    
    return projeler

def generate_parsing_code(projeler):
    """Parse kodu önerisi oluştur"""
    print("\n4️⃣ Önerilen Parse Kodu:")
    print()
    
    if not projeler:
        print("   ⚠️ Proje bulunamadı, kod üretilemedi")
        return
    
    # İlk projeyi analiz et
    ornek = projeler[0]
    
    print("```python")
    print("def parse_ced_proje(row_element):")
    print('    """ÇED tablosundan proje bilgisi çıkar"""')
    print("    try:")
    print("        cells = row_element.find_all(['td', 'th'])")
    print(f"        ")
    print(f"        # Toplam {ornek['hucre_sayisi']} hücre var")
    
    if ornek['hucre_sayisi'] >= 3:
        print("        proje_adi = cells[0].get_text(strip=True) if len(cells) > 0 else ''")
        print("        firma = cells[1].get_text(strip=True) if len(cells) > 1 else ''")
        print("        il = cells[2].get_text(strip=True) if len(cells) > 2 else ''")
        
        if ornek['hucre_sayisi'] >= 4:
            print("        sektor = cells[3].get_text(strip=True) if len(cells) > 3 else ''")
        
        if ornek['hucre_sayisi'] >= 5:
            print("        tarih = cells[4].get_text(strip=True) if len(cells) > 4 else ''")
    
    print("        ")
    print("        return {")
    print("            'proje_adi': proje_adi,")
    print("            'firma': firma,")
    print("            'il': il,")
    if ornek['hucre_sayisi'] >= 4:
        print("            'sektor': sektor,")
    if ornek['hucre_sayisi'] >= 5:
        print("            'tarih': tarih,")
    print("            'kategori': categorize_project(proje_adi, sektor)")
    print("        }")
    print("    except Exception as e:")
    print("        return None")
    print("```")
    print()

def save_results(projeler):
    """Sonuçları kaydet"""
    print("5️⃣ Sonuçlar kaydediliyor...")
    
    if projeler:
        with open('ced_parsed_projects.json', 'w', encoding='utf-8') as f:
            json.dump(projeler, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(projeler)} proje kaydedildi: ced_parsed_projects.json")
        
        # İstanbul projeleri
        istanbul_projeler = [p for p in projeler if p.get('istanbul', False)]
        print(f"   📍 İstanbul projesi: {len(istanbul_projeler)}/{len(projeler)}")
        
        # Kategoriler
        kategoriler = {}
        for p in projeler:
            kat = p.get('olasi_kategori', 'bilinmiyor')
            kategoriler[kat] = kategoriler.get(kat, 0) + 1
        
        print(f"   📂 Kategoriler: {kategoriler}")
    else:
        print("   ⚠️ Kaydedilecek proje yok")
    
    print()

def main():
    response = test_ced_connection()
    
    if not response:
        print("⚠️ Bağlantı başarısız, test sonlandırılıyor.")
        return
    
    soup = deep_analyze_structure(response)
    projeler = find_actual_project_data(soup)
    
    print()
    print("=" * 70)
    print("📊 TEST SONUÇLARI")
    print("=" * 70)
    print()
    
    if projeler:
        print(f"✅ {len(projeler)} proje parse edildi")
        print()
        
        # Örnek göster
        print("📄 Örnek Proje Verisi:")
        print(json.dumps(projeler[0], indent=2, ensure_ascii=False))
        print()
        
        generate_parsing_code(projeler)
        save_results(projeler)
        
        print("🎯 SONRAKI ADIMLAR:")
        print("   1. ced_parsed_projects.json'ı incele")
        print("   2. Önerilen parse kodunu web_sunucu.py'ye ekle")
        print("   3. python web_sunucu.py ile test et")
        
    else:
        print("❌ Proje parse edilemedi")
        print()
        print("💡 ÖNERİLER:")
        print("   1. ced_page_source.html dosyasını tarayıcıda aç")
        print("   2. Developer Tools ile tablo yapısını incele")
        print("   3. Hangi hücrede hangi bilgi olduğunu belirle")
        print("   4. web_sunucu.py içindeki parse fonksiyonunu manuel güncelle")
    
    print()
    print("📁 Oluşturulan Dosyalar:")
    print("   - ced_page_source.html (Sayfa kaynağı)")
    if projeler:
        print("   - ced_parsed_projects.json (Parse edilmiş projeler)")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()