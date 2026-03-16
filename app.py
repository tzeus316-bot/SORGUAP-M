# ============================================= #
#     RENDER.COM İÇİN PLAKA API (Python)       #
#     SQL Formatındaki Verileri Okur           #
# ============================================= #

from flask import Flask, request, jsonify, render_template_string
import os
import re
import logging
from datetime import datetime
import socket

# Flask uygulamasını oluştur
app = Flask(__name__)

# Port ayarı - Render otomatik atar
port = int(os.environ.get('PORT', 10000))

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================= #
#              VERİ YÜKLEME                    #
# ============================================= #

VERI_DOSYASI = 'veri.txt'

def sql_verisini_parse_et(satir):
    """
    SQL INSERT satırından plaka ve ismi çıkar
    Örnek: INSERT INTO `77k_plaka` VALUES (1, '34KG4978', 'Oğuzhan Uğur', '-', '-');
    """
    satir = satir.strip()
    if not satir or 'INSERT INTO' not in satir:
        return None
    
    # VALUES kısmını bul
    match = re.search(r'VALUES\s*\((.*?)\)', satir, re.IGNORECASE)
    if not match:
        return None
    
    values = match.group(1)
    
    # Tırnak içindeki değerleri bul
    tirnak_icindekiler = re.findall(r"'([^']*)'", values)
    
    if len(tirnak_icindekiler) >= 3:  # En az id, plaka, isim olmalı
        plaka = tirnak_icindekiler[1].strip().upper()
        plaka = re.sub(r'\s+', '', plaka)  # Boşlukları temizle
        isim = tirnak_icindekiler[2].strip()
        
        return {
            'plaka': plaka,
            'isim': isim
        }
    
    return None

def verileri_yukle():
    """Tüm verileri dosyadan yükle"""
    veriler = {}
    
    if not os.path.exists(VERI_DOSYASI):
        app.logger.error(f"{VERI_DOSYASI} dosyası bulunamadı!")
        return veriler
    
    try:
        with open(VERI_DOSYASI, 'r', encoding='utf-8') as f:
            for satir in f:
                veri = sql_verisini_parse_et(satir)
                if veri:
                    veriler[veri['plaka']] = veri['isim']
        
        app.logger.info(f"{len(veriler)} plaka kaydı yüklendi")
    except Exception as e:
        app.logger.error(f"Veri yüklenirken hata: {e}")
    
    return veriler

# Uygulama başlarken verileri yükle
PLAKA_VERILERI = verileri_yukle()

# ============================================= #
#              YARDIMCI FONKSİYONLAR           #
# ============================================= #

def get_client_ip():
    """İstemci IP adresini al (Cloudflare uyumlu)"""
    if request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    elif request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        return request.remote_addr or '0.0.0.0'

def log_kaydet(plaka, bulundu_mu, ip):
    """Log kaydet"""
    log_dosyasi = 'plaka_log.txt'
    tarih = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    durum = 'BULUNDU' if bulundu_mu else 'BULUNAMADI'
    
    try:
        with open(log_dosyasi, 'a', encoding='utf-8') as f:
            f.write(f"[{tarih}] {durum} - Plaka: {plaka} - IP: {ip}\n")
    except:
        pass  # Log hatası önemli değil

# ============================================= #
#              API ROUTES                       #
# ============================================= #

@app.route('/')
def ana_sayfa():
    """Ana sayfa - API bilgileri"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Plaka API - Render</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #141e30, #243b55);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container { max-width: 800px; width: 100%; }
            .card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 30px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            h1 span {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 5px 15px;
                border-radius: 30px;
                font-size: 0.4em;
                margin-left: 10px;
            }
            .badge {
                text-align: center;
                margin-bottom: 30px;
            }
            .badge span {
                background: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 30px;
                font-size: 0.9em;
                display: inline-block;
                margin: 0 5px;
            }
            .badge .blue { background: #007bff; }
            .info-box {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 30px 0;
                border-left: 5px solid #667eea;
            }
            .info-box h3 {
                color: #333;
                margin-bottom: 15px;
            }
            .info-item {
                background: white;
                padding: 12px;
                border-radius: 10px;
                margin: 10px 0;
                font-family: monospace;
                font-size: 1.1em;
            }
            .input-group {
                display: flex;
                gap: 10px;
                margin: 30px 0;
            }
            .input-group input {
                flex: 1;
                padding: 15px 20px;
                font-size: 1.2em;
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                transition: all 0.3s;
            }
            .input-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102,126,234,0.1);
            }
            .input-group button {
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 1.2em;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.3s;
            }
            .input-group button:hover {
                transform: scale(1.05);
            }
            .result-box {
                background: #1e1e2f;
                color: white;
                border-radius: 15px;
                padding: 20px;
                font-family: 'Courier New', monospace;
                white-space: pre-wrap;
                max-height: 300px;
                overflow-y: auto;
                display: none;
                border-left: 5px solid #28a745;
            }
            .result-box.error {
                border-left-color: #dc3545;
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 15px;
            }
            .stat-item { text-align: center; }
            .stat-value {
                font-size: 1.5em;
                font-weight: bold;
                color: #667eea;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #666;
                font-size: 0.9em;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>
                    🚗 PLAKA API
                    <span>RENDER</span>
                </h1>
                
                <div class="badge">
                    <span class="blue">🛡️ CLOUDFLARE</span>
                    <span>📁 {{ veri_sayisi }} KAYIT</span>
                    <span>🐍 PYTHON</span>
                </div>
                
                <div class="info-box">
                    <h3>📌 API KULLANIMI</h3>
                    <div class="info-item">
                        <strong>GET:</strong> <code>/api/plaka?plaka=34KG4978</code>
                    </div>
                    <div class="info-item">
                        <strong>POST:</strong> <code>/api/plaka</code><br>
                        JSON: <code>{"plaka": "34KG4978"}</code>
                    </div>
                    <div class="info-item">
                        <strong>Dosya:</strong> <code>veri.txt</code> (SQL formatı)
                    </div>
                </div>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value">{{ veri_sayisi }}</div>
                        <div>Plaka Kaydı</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">✅ AKTİF</div>
                        <div>API Durumu</div>
                    </div>
                </div>
                
                <div class="input-group">
                    <input type="text" id="plaka" placeholder="Örnek: 34KG4978" maxlength="10" autofocus>
                    <button onclick="sorgula()">🔍 Sorgula</button>
                </div>
                
                <div id="sonuc" class="result-box"></div>
                
                <div class="footer">
                    🔒 Cloudflare uyumlu | Gerçek IP gizli | {{ zaman }}
                </div>
            </div>
        </div>
        
        <script>
        async function sorgula() {
            const plaka = document.getElementById('plaka').value.trim().toUpperCase();
            const sonucDiv = document.getElementById('sonuc');
            
            if(!plaka) {
                alert('Lütfen bir plaka girin!');
                return;
            }
            
            sonucDiv.style.display = 'block';
            sonucDiv.className = 'result-box';
            sonucDiv.innerHTML = '<div style="text-align: center"><span class="loading"></span> Plaka aranıyor...</div>';
            
            try {
                const response = await fetch(`/api/plaka?plaka=${encodeURIComponent(plaka)}`);
                const data = await response.json();
                
                if(response.ok) {
                    sonucDiv.className = 'result-box';
                } else {
                    sonucDiv.className = 'result-box error';
                }
                
                sonucDiv.innerHTML = JSON.stringify(data, null, 2);
            } catch(error) {
                sonucDiv.className = 'result-box error';
                sonucDiv.innerHTML = JSON.stringify({
                    hata: 'Bağlantı hatası',
                    detay: error.toString()
                }, null, 2);
            }
        }
        
        document.getElementById('plaka').addEventListener('keypress', function(e) {
            if(e.key === 'Enter') sorgula();
        });
        </script>
    </body>
    </html>
    ''', veri_sayisi=len(PLAKA_VERILERI), zaman=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/plaka', methods=['GET', 'POST'])
def plaka_api():
    """Plaka sorgulama API'si"""
    
    # Güvenlik başlıkları
    headers = {
        'Server': 'Cloudflare',
        'X-Powered-By': 'Cloudflare',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }
    
    # İstekten plakayı al
    if request.method == 'GET':
        plaka = request.args.get('plaka')
    else:  # POST
        data = request.get_json()
        plaka = data.get('plaka') if data else None
    
    # Plaka kontrolü
    if not plaka:
        return jsonify({
            'durum': 'hata',
            'kod': 400,
            'mesaj': 'Plaka belirtilmedi',
            'kullanim': '/api/plaka?plaka=34KG4978',
            'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 400, headers
    
    # Plakayı temizle
    plaka = re.sub(r'\s+', '', plaka.strip().upper())
    
    if not plaka:
        return jsonify({
            'durum': 'hata',
            'kod': 400,
            'mesaj': 'Geçersiz plaka formatı',
            'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 400, headers
    
    # Plakayı ara
    ip = get_client_ip()
    
    if plaka in PLAKA_VERILERI:
        # Log kaydet
        log_kaydet(plaka, True, ip)
        
        return jsonify({
            'durum': 'başarılı',
            'kod': 200,
            'plaka': plaka,
            'isim': PLAKA_VERILERI[plaka],
            'mesaj': 'Plaka bulundu',
            'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200, headers
    else:
        # Log kaydet
        log_kaydet(plaka, False, ip)
        
        return jsonify({
            'durum': 'hata',
            'kod': 404,
            'plaka': plaka,
            'mesaj': 'Plaka bulunamadı',
            'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 404, headers

@app.route('/api/veriler', methods=['GET'])
def veri_listesi():
    """Tüm plakaların listesi (sadece plaka ve isim)"""
    veriler = [{'plaka': p, 'isim': i} for p, i in PLAKA_VERILERI.items()]
    
    return jsonify({
        'durum': 'başarılı',
        'toplam': len(veriler),
        'veriler': veriler,
        'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@app.route('/api/saglik', methods=['GET'])
def saglik_kontrol():
    """Sağlık kontrolü"""
    return jsonify({
        'durum': 'sağlıklı',
        'veri_sayisi': len(PLAKA_VERILERI),
        'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@app.route('/api/ip', methods=['GET'])
def ip_goster():
    """İstemci IP'sini göster (test için)"""
    ip = get_client_ip()
    return jsonify({
        'ip': ip,
        'cloudflare': request.headers.get('CF-Connecting-IP') is not None,
        'headers': dict(request.headers)
    }), 200

# ============================================= #
#                  ANA ÇALIŞTIRMA               #
# ============================================= #

if __name__ == '__main__':
    print("="*60)
    print("🚗 PLAKA API - RENDER.COM")
    print("="*60)
    print(f"\n📁 Veri dosyası: {VERI_DOSYASI}")
    print(f"📊 Yüklenen kayıt: {len(PLAKA_VERILERI)} plaka")
    print(f"\n🌐 API Adresleri:")
    print(f"   Ana Sayfa : http://localhost:{port}/")
    print(f"   Plaka API : http://localhost:{port}/api/plaka?plaka=34KG4978")
    print(f"   Tüm Veriler: http://localhost:{port}/api/veriler")
    print(f"   Sağlık     : http://localhost:{port}/api/saglik")
    print(f"   IP Test    : http://localhost:{port}/api/ip")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
