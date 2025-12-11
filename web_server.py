"""
İstanbul Şehir Analizi - Web Sunucusu (Sağlık + Ulaşım + ÇED)
Flask ile kategori bazlı web server
"""

from flask import Flask, send_from_directory, jsonify, request
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = Flask(__name__)

# Klasör yolları
BASE_DIR = r"C:\ProgrammingFile\Python\IstanbulUlasimProjesi"
CIKTI_KLASORU = os.path.join(BASE_DIR, "outputs")
WEB_KLASORU = os.path.join(BASE_DIR, "web")
VERI_KLASORU = os.path.join(BASE_DIR, "data", "ham_veri", "saglik")  # ← saglik eklendi

# ÇED önbellek (rate limiting için)
CED_CACHE = {
    "data": None,
    "timestamp": None,
    "cache_duration": 3600  # 1 saat cache
}

print("=" * 70)
print("🌐 İSTANBUL ŞEHİR ANALİZİ - WEB SUNUCUSU")
print("   📂 Kategorili Sistem + ÇED Entegrasyonu + Sağlık Modülü")
print("=" * 70)
print()

# ============= ANA SAYFA (KATEGORİLER) =============
@app.route('/')
def index():
    try:
        return send_from_directory(WEB_KLASORU, 'index.html')
    except:
        return """
        <h1>❌ index.html bulunamadı!</h1>
        <p>Lütfen web/index.html dosyasını oluşturun.</p>
        """

# ============= ULAŞIM KATEGORİSİ =============
@app.route('/ulasim')
def ulasim():
    try:
        return send_from_directory(WEB_KLASORU, 'ulasim.html')
    except:
        return "<h1>❌ ulasim.html bulunamadı!</h1>"

@app.route('/ulasim/harita')
def ulasim_harita():
    try:
        return send_from_directory(WEB_KLASORU, 'harita.html')
    except:
        return "<h1>❌ harita.html bulunamadı!</h1>"

# ============= SAĞLIK KATEGORİSİ =============
@app.route('/saglik')
def saglik():
    """Sağlık analiz sayfası"""
    try:
        return send_from_directory(WEB_KLASORU, 'saglik.html')
    except:
        return """
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <title>Sağlık Analizi - Yakında</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                }
                .container {
                    background: white;
                    border-radius: 20px;
                    padding: 60px;
                    text-align: center;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 600px;
                }
                h1 { color: #667eea; font-size: 3em; margin-bottom: 20px; }
                p { color: #666; font-size: 1.2em; line-height: 1.8; }
                .icon { font-size: 5em; margin-bottom: 20px; }
                .back-btn {
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 15px 40px;
                    border-radius: 25px;
                    text-decoration: none;
                    margin-top: 30px;
                    font-weight: bold;
                    transition: all 0.3s;
                }
                .back-btn:hover {
                    background: #764ba2;
                    transform: translateY(-3px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🏥</div>
                <h1>Sağlık Analizi</h1>
                <p>saglik.html dosyası bulunamadı!</p>
                <p style="font-size: 0.9em; margin-top: 20px;">
                    Lütfen saglik.html dosyasını web/ klasörüne ekleyin.
                </p>
                <a href="/" class="back-btn">← Ana Sayfaya Dön</a>
            </div>
        </body>
        </html>
        """

# ============= JSON API ENDPOİNTLERİ =============

# ULAŞIM - Analiz Verisi
@app.route('/api/ulasim/analiz-verisi')
@app.route('/api/analiz-verisi')  # Geriye uyumluluk
def get_analiz_verisi():
    try:
        trafik_39_dosya = os.path.join(CIKTI_KLASORU, 'ai_analiz_verisi_39ilce_trafik.json')
        if os.path.exists(trafik_39_dosya):
            with open(trafik_39_dosya, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Ulaşım analiz verisi servis edildi: 39 ilçe + trafik")
            return jsonify(data)
        
        normal_39_dosya = os.path.join(CIKTI_KLASORU, 'ai_analiz_verisi_39ilce.json')
        if os.path.exists(normal_39_dosya):
            with open(normal_39_dosya, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Ulaşım analiz verisi servis edildi: 39 ilçe")
            return jsonify(data)
        
        trafik_dosya = os.path.join(CIKTI_KLASORU, 'ai_analiz_verisi_trafik.json')
        if os.path.exists(trafik_dosya):
            with open(trafik_dosya, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        
        with open(os.path.join(CIKTI_KLASORU, 'ai_analiz_verisi.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
        
    except FileNotFoundError:
        return jsonify({
            "error": "Ulaşım analiz verisi bulunamadı",
            "message": "Lütfen önce transportation_analysis_engine.py dosyasını çalıştırın"
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ULAŞIM - Yatırım Önerileri
@app.route('/api/ulasim/yatirim-onerileri')
@app.route('/api/yatirim-onerileri')  # Geriye uyumluluk
def get_yatirim_onerileri():
    try:
        # ÇED versiyonu
        ced_dosya = os.path.join(CIKTI_KLASORU, 'ai_yatirim_onerileri_v5_ced.json')
        if os.path.exists(ced_dosya):
            with open(ced_dosya, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Ulaşım önerileri (ÇED) servis edildi: {len(data)} ilçe")
            return jsonify(data)
        
        # Normal 39 ilçe
        dosya_39 = os.path.join(CIKTI_KLASORU, 'ai_yatirim_onerileri_39ilce.json')
        if os.path.exists(dosya_39):
            with open(dosya_39, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"⚠️  Normal öneriler servis edildi: 39 ilçe (ÇED verisi YOK)")
            return jsonify(data)
        
        # Eski versiyon
        with open(os.path.join(CIKTI_KLASORU, 'ai_yatirim_onerileri.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"⚠️  Eski versiyon servis edildi")
        return jsonify(data)
        
    except FileNotFoundError:
        return jsonify({
            "error": "Ulaşım yatırım önerileri bulunamadı",
            "message": "Lütfen önce ai_transportation_recommendations.py dosyasını çalıştırın"
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SAĞLIK - Analiz Verisi
@app.route('/api/saglik/analiz-verisi')
def get_saglik_analiz():
    """Sağlık analiz dataini döndür"""
    try:
        with open(os.path.join(CIKTI_KLASORU, 'ai_analiz_saglik_39ilce.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Sağlık analiz verisi servis edildi: 39 ilçe")
        return jsonify(data)
        
    except FileNotFoundError:
        return jsonify({
            "error": "Sağlık analiz verisi bulunamadı",
            "message": "Lütfen önce health_analysis_engine.py dosyasını çalıştırın"
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SAĞLIK - Yatırım Önerileri
@app.route('/api/saglik/yatirim-onerileri')
def get_saglik_onerileri():
    """Sağlık yatırım önerilerini döndür"""
    try:
        with open(os.path.join(CIKTI_KLASORU, 'ai_saglik_onerileri_39ilce.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Sağlık önerileri servis edildi: {len(data)} ilçe")
        return jsonify(data)
        
    except FileNotFoundError:
        return jsonify({
            "error": "Sağlık önerileri bulunamadı",
            "message": "Lütfen önce ai_health_recommendations.py dosyasını çalıştırın"
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SAĞLIK - Metadata
@app.route('/api/saglik/metadata')
def get_saglik_metadata():
    """Veri kaynaklarını ve metodolojisini döndür"""
    try:
        with open(os.path.join(VERI_KLASORU, 'veri_metadata.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({
            "error": "Metadata bulunamadı",
            "uyari": "Veri kaynakları bilgisi mevcut değil"
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= ÇEVRE KATEGORİSİ =============
@app.route('/cevre')
def cevre():
    """Çevre analiz sayfası"""
    try:
        return send_from_directory(WEB_KLASORU, 'cevre.html')
    except:
        return "<h1>❌ cevre.html bulunamadı!</h1>"

@app.route('/cevre/harita')
def cevre_harita():
    """Çevre interaktif haritası"""
    try:
        return send_from_directory(WEB_KLASORU, 'cevre_harita.html')
    except:
        return """
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <title>Çevre Analizi - Yakında</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                }
                .container {
                    background: white;
                    border-radius: 20px;
                    padding: 60px;
                    text-align: center;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 600px;
                }
                h1 { color: #667eea; font-size: 3em; margin-bottom: 20px; }
                p { color: #666; font-size: 1.2em; line-height: 1.8; }
                .icon { font-size: 5em; margin-bottom: 20px; }
                .back-btn {
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 15px 40px;
                    border-radius: 25px;
                    text-decoration: none;
                    margin-top: 30px;
                    font-weight: bold;
                    transition: all 0.3s;
                }
                .back-btn:hover {
                    background: #764ba2;
                    transform: translateY(-3px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🌳</div>
                <h1>Çevre Analizi</h1>
                <p>cevre.html dosyası bulunamadı!</p>
                <p style="font-size: 0.9em; margin-top: 20px;">
                    Lütfen cevre.html dosyasını web/ klasörüne ekleyin.
                </p>
                <a href="/" class="back-btn">← Ana Sayfaya Dön</a>
            </div>
        </body>
        </html>
        """

# ÇEVRE - Analiz Verisi
@app.route('/api/cevre/analiz-verisi')
def get_cevre_analiz():
    """Çevre analiz dataini döndür"""
    try:
        with open(os.path.join(CIKTI_KLASORU, 'ai_analiz_cevre_39ilce.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Çevre analiz verisi servis edildi: 39 ilçe")
        return jsonify(data)
        
    except FileNotFoundError:
        return jsonify({
            "error": "Çevre analiz verisi bulunamadı",
            "message": "Lütfen önce environment_analysis_engine.py dosyasını çalıştırın"
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ÇEVRE - Yatırım Önerileri
@app.route('/api/cevre/yatirim-onerileri')
def get_cevre_onerileri():
    """Çevre yatırım önerilerini döndür"""
    try:
        with open(os.path.join(CIKTI_KLASORU, 'ai_cevre_onerileri_39ilce.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Çevre önerileri servis edildi: {len(data)} ilçe")
        return jsonify(data)
        
    except FileNotFoundError:
        return jsonify({
            "error": "Çevre önerileri bulunamadı",
            "message": "Lütfen önce ai_environment_recommendations.py dosyasını çalıştırın"
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= ÇED ENTEGRASYONU (ULAŞIM İÇİN) =============

def scrape_ced_projeleri(kategori=None):
    """ÇED duyuru sisteminden projeleri çeker (placeholder)"""
    # Not: Gerçek ÇED scraping kodu burada olacak
    # Şimdilik basit fallback döndürüyoruz
    return create_fallback_ced_data(kategori)

def create_fallback_ced_data(kategori=None):
    """Bağlantı başarısız olursa örnek veri döndür"""
    print("⚠️  Fallback ÇED verisi kullanılıyor")
    
    ornek_projeler = [
        {
            "proje_adi": "Beylikdüzü-Avcılar Metro Hattı",
            "firma": "İBB - Metro İstanbul",
            "il": "İstanbul",
            "sektor": "Ulaşım",
            "tarih": "2024",
            "kategori": "ulasim",
            "durum": "Planlama Aşamasında"
        }
    ]
    
    if kategori:
        ornek_projeler = [p for p in ornek_projeler if p.get("kategori") == kategori]
    
    return {
        "projeler": ornek_projeler,
        "toplam": len(ornek_projeler),
        "kategori": kategori,
        "son_guncelleme": datetime.now().isoformat(),
        "kaynak": "Örnek Veri (ÇED bağlantısı başarısız)",
        "uyari": "Gerçek zamanlı veri alınamadı"
    }

@app.route('/api/ced-projeleri')
def get_ced_projeleri():
    """Tüm ÇED projelerini getir"""
    kategori = request.args.get('kategori')
    return jsonify(scrape_ced_projeleri(kategori))

# ============= RAPOR İNDİRME =============
@app.route('/api/rapor')
def get_rapor():
    try:
        rapor_39 = os.path.join(CIKTI_KLASORU, 'ilce_eksiklik_raporu_39ilce.csv')
        if os.path.exists(rapor_39):
            return send_from_directory(CIKTI_KLASORU, 'ilce_eksiklik_raporu_39ilce.csv', as_attachment=True)
        
        return send_from_directory(CIKTI_KLASORU, 'ilce_eksiklik_raporu.csv', as_attachment=True)
    except:
        return "Rapor bulunamadı", 404

# ============= DURUM KONTROLÜ =============
@app.route('/api/durum')
def durum():
    """Sistem durumu ve dosya kontrolü"""
    dosyalar = {
        "ulasim": {
            "analiz_39_trafik": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_analiz_verisi_39ilce_trafik.json')),
            "analiz_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_analiz_verisi_39ilce.json')),
            "oneriler_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_yatirim_onerileri_39ilce.json')),
            "oneriler_v5_ced": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_yatirim_onerileri_v5_ced.json')),
            "rapor_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ilce_eksiklik_raporu_39ilce.csv'))
        },
        "saglik": {
            "analiz_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_analiz_saglik_39ilce.json')),
            "oneriler_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_saglik_onerileri_39ilce.json')),
            "rapor_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ilce_saglik_raporu_39ilce.csv')),
            "metadata": os.path.exists(os.path.join(VERI_KLASORU, 'veri_metadata.json')),
            "veri_birlesik": os.path.exists(os.path.join(VERI_KLASORU, 'ilce_saglik_birlesik_tahmini.csv'))
        },
        "cevre": {
            "analiz_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_analiz_cevre_39ilce.json')),
            "oneriler_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ai_cevre_onerileri_39ilce.json')),
            "rapor_39": os.path.exists(os.path.join(CIKTI_KLASORU, 'ilce_cevre_raporu_39ilce.csv'))
        },
        "ced_entegrasyonu": {
            "aktif": True,
            "son_kontrol": CED_CACHE["timestamp"].isoformat() if CED_CACHE["timestamp"] else None,
            "cache_proje_sayisi": len(CED_CACHE["data"]["projeler"]) if CED_CACHE["data"] else 0
        }
    }
    
    # Ulaşım durumu
    aktif_ulasim = None
    if dosyalar["ulasim"]["oneriler_v5_ced"]:
        aktif_ulasim = "39 ilçe + ÇED entegrasyonu ✅"
    elif dosyalar["ulasim"]["analiz_39_trafik"] and dosyalar["ulasim"]["oneriler_39"]:
        aktif_ulasim = "39 ilçe + trafik (ÇED yok ⚠️)"
    elif dosyalar["ulasim"]["analiz_39"]:
        aktif_ulasim = "39 ilçe"
    
    # Sağlık durumu
    aktif_saglik = None
    if dosyalar["saglik"]["analiz_39"] and dosyalar["saglik"]["oneriler_39"]:
        aktif_saglik = "39 ilçe (Hibrit Model) ✅"
    elif dosyalar["saglik"]["veri_birlesik"]:
        aktif_saglik = "Veri hazır (AI bekliyor) ⏳"
    
    # Çevre durumu
    aktif_cevre = None
    if dosyalar["cevre"]["analiz_39"] and dosyalar["cevre"]["oneriler_39"]:
        aktif_cevre = "39 ilçe ✅"
    elif dosyalar["cevre"]["analiz_39"]:
        aktif_cevre = "Veri hazır (AI bekliyor) ⏳"
    
    return jsonify({
        "dosyalar": dosyalar,
        "aktif_veri": {
            "ulasim": aktif_ulasim,
            "saglik": aktif_saglik,
            "cevre": aktif_cevre
        },
        "mesaj": "Tüm modüller hazır! 🎉" if aktif_ulasim and aktif_saglik and aktif_cevre else "Bazı modüller eksik",
        "kategoriler": {
            "ulasim": "Aktif ✅" if aktif_ulasim else "Hazırlanıyor ⏳",
            "saglik": "Aktif ✅" if aktif_saglik else "Hazırlanıyor ⏳",
            "cevre": "Aktif ✅" if aktif_cevre else "Hazırlanıyor ⏳",
            "egitim": "Yakında 📅"
        },
        "ced_sistem": {
            "durum": "Aktif ✅",
            "api_endpoint": "/api/ced-projeleri",
            "karsilastirma": "/api/ulasim/ced-karsilastir"
        }
    })

if __name__ == '__main__':
    print("✅ Sunucu başlatılıyor...")
    print()
    print("🌐 Adresler:")
    print("   Ana Sayfa (Kategoriler): http://localhost:5000")
    print("   Ulaşım Analizi: http://localhost:5000/ulasim")
    print("   Sağlık Analizi: http://localhost:5000/saglik")
    print("   Çevre Analizi: http://localhost:5000/cevre")
    print("   Ulaşım Haritası: http://localhost:5000/ulasim/harita")
    print()
    print("📊 API Endpoint'leri:")
    print("   Durum Kontrolü: http://localhost:5000/api/durum")
    print("   Ulaşım Analiz: http://localhost:5000/api/ulasim/analiz-verisi")
    print("   Ulaşım Öneriler: http://localhost:5000/api/ulasim/yatirim-onerileri")
    print("   Sağlık Analiz: http://localhost:5000/api/saglik/analiz-verisi")
    print("   Sağlık Öneriler: http://localhost:5000/api/saglik/yatirim-onerileri")
    print("   Sağlık Metadata: http://localhost:5000/api/saglik/metadata")
    print("   Çevre Analiz: http://localhost:5000/api/cevre/analiz-verisi")
    print("   Çevre Öneriler: http://localhost:5000/api/cevre/yatirim-onerileri")
    print()
    print("🌐 ÇED Entegrasyonu:")
    print("   Tüm ÇED Projeleri: http://localhost:5000/api/ced-projeleri")
    print()
    print("🛑 Durdurmak için: CTRL+C")
    print("=" * 70)
    print()
    
    # Render deployment compatibility
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)