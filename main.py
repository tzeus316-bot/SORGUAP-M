from flask import Flask, request, jsonify, render_template_string
import os
import re
from datetime import datetime
import logging

# Flask uygulamasını oluştur
app = Flask(__name__)

# Port ayarı - Render otomatik atar
port = int(os.environ.get('PORT', 10000))

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ===================================== #
#         DOSYA YOLLARI (Render)        #
# ===================================== #

# Ana dizindeki dosyalar (Render'da repository'nin ana dizininde olacak)
PLAKA_DOSYA = 'data.txt'      # Plaka verileri
SICIL_DOSYA = 'sicil.txt'     # Sicil verileri

# ===================================== #
#         RENDER UYUMLU HTML            #
# ===================================== #

RENDER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔌 Çift API | Render</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #141e30 0%, #243b55 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 40px 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            color: white;
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header h1 span {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            padding: 5px 15px;
            border-radius: 30px;
            font-size: 0.4em;
            margin-left: 15px;
            color: white;
        }
        
        .header p {
            color: rgba(255,255,255,0.9);
            font-size: 1.2em;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }
        
        .stat-item {
            background: rgba(255,255,255,0.15);
            padding: 10px 25px;
            border-radius: 30px;
            color: white;
            font-size: 1.1em;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* API Grid */
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        /* API Kartları */
        .api-card {
            background: white;
            border-radius: 30px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .api-card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .card-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            color: white;
        }
        
        .card-title {
            flex: 1;
        }
        
        .card-title h2 {
            color: #333;
            margin-bottom: 5px;
            font-size: 1.8em;
        }
        
        .card-title p {
            color: #666;
            font-size: 0.9em;
        }
        
        .status-badge {
            background: #28a745;
            color: white;
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        /* Bilgi Kutuları */
        .info-box {
            background: #f8f9fa;
            border-radius: 20px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #667eea;
        }
        
        .info-box h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .info-box code {
            background: #e9ecef;
            padding: 8px 12px;
            border-radius: 10px;
            color: #d63384;
            font-size: 1.1em;
            display: inline-block;
            margin: 5px 0;
        }
        
        .info-item {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 10px;
            font-size: 0.95em;
        }
        
        /* Input Grubu */
        .input-group {
            margin: 25px 0;
        }
        
        .input-wrapper {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .input-wrapper input {
            flex: 1;
            padding: 15px 20px;
            font-size: 1.1em;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            transition: all 0.3s;
            background: #f8f9fa;
        }
        
        .input-wrapper input:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 4px rgba(102,126,234,0.1);
        }
        
        .input-wrapper button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .input-wrapper button:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(102,126,234,0.3);
        }
        
        /* Sonuç Kutusu */
        .result-box {
            background: #1e1e2f;
            color: #fff;
            border-radius: 15px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            font-size: 14px;
            line-height: 1.6;
            border: 1px solid #333;
            display: none;
        }
        
        .result-box.success {
            border-left: 5px solid #28a745;
        }
        
        .result-box.error {
            border-left: 5px solid #dc3545;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            color: white;
        }
        
        .footer a {
            color: #4ecdc4;
            text-decoration: none;
            font-weight: bold;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        /* Loading Animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .api-grid {
                grid-template-columns: 1fr;
            }
            
            .input-wrapper {
                flex-direction: column;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>
                🚀 ÇİFT API
                <span>RENDER</span>
            </h1>
            <p>data.txt (Plaka) & sicil.txt (TC) ile çalışan çift fonksiyonlu API</p>
            <div class="stats">
                <div class="stat-item">📁 data.txt aktif</div>
                <div class="stat-item">📋 sicil.txt aktif</div>
                <div class="stat-item">⚡ 2 endpoint</div>
            </div>
        </div>
        
        <!-- API Grid -->
        <div class="api-grid">
            <!-- PLAKA API KARTI -->
            <div class="api-card">
                <div class="card-header">
                    <div class="card-icon">🚗</div>
                    <div class="card-title">
                        <h2>Plaka Sorgulama</h2>
                        <p>data.txt dosyasından plaka sorgulama</p>
                    </div>
                    <div class="status-badge">AKTİF</div>
                </div>
                
                <div class="info-box">
                    <h3>📌 Kullanım</h3>
                    <div class="info-item">
                        <strong>GET:</strong> <code>/api/plaka?plaka=34KG4978</code>
                    </div>
                    <div class="info-item">
                        <strong>POST:</strong> <code>/api/plaka</code> 
                        <br>JSON: <code>{"plaka": "34KG4978"}</code>
                    </div>
                    <div class="info-item">
                        <strong>Veri dosyası:</strong> <code>data.txt</code>
                    </div>
                </div>
                
                <div class="input-group">
                    <div class="input-wrapper">
                        <input type="text" id="plaka-input" placeholder="Örnek: 34KG4978" maxlength="10">
                        <button onclick="sorgulaPlaka()">🔍 Sorgula</button>
                    </div>
                </div>
                
                <div id="plaka-sonuc" class="result-box"></div>
            </div>
            
            <!-- SİCİL API KARTI -->
            <div class="api-card">
                <div class="card-header">
                    <div class="card-icon">📋</div>
                    <div class="card-title">
                        <h2>Sicil Sorgulama</h2>
                        <p>sicil.txt dosyasından TC sorgulama</p>
                    </div>
                    <div class="status-badge">AKTİF</div>
                </div>
                
                <div class="info-box">
                    <h3>📌 Kullanım</h3>
                    <div class="info-item">
                        <strong>GET:</strong> <code>/api/sicil?tc=12345678901</code>
                    </div>
                    <div class="info-item">
                        <strong>POST:</strong> <code>/api/sicil</code>
                        <br>JSON: <code>{"tc": "12345678901"}</code>
                    </div>
                    <div class="info-item">
                        <strong>Veri dosyası:</strong> <code>sicil.txt</code>
                    </div>
                </div>
                
                <div class="input-group">
                    <div class="input-wrapper">
                        <input type="text" id="tc-input" placeholder="11 haneli TC girin" maxlength="11">
                        <button onclick="sorgulaSicil()">📋 Sorgula</button>
                    </div>
                </div>
                
                <div id="sicil-sonuc" class="result-box"></div>
            </div>
        </div>
        
        <!-- API Dokümantasyon -->
        <div class="footer">
            <p>🔗 <a href="/api/dokuman" target="_blank">API Dokümantasyonu</a> | 
            📁 <a href="#" onclick="testDosyalari()">Veri Dosyalarını Kontrol Et</a></p>
            <p style="margin-top: 15px; font-size: 0.9em;">
                data.txt: Plaka verileri | sicil.txt: TC sicil verileri
            </p>
        </div>
    </div>
    
    <script>
    async function sorgulaPlaka() {
        const plaka = document.getElementById('plaka-input').value.trim().toUpperCase();
        const sonucDiv = document.getElementById('plaka-sonuc');
        
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
                sonucDiv.className = 'result-box success';
            } else {
                sonucDiv.className = 'result-box error';
            }
            
            sonucDiv.innerHTML = JSON.stringify(data, null, 2);
        } catch(error) {
            sonucDiv.className = 'result-box error';
            sonucDiv.innerHTML = JSON.stringify({
                hata: 'Bağlantı hatası',
                detay: error.toString(),
                zaman: new Date().toISOString()
            }, null, 2);
        }
    }
    
    async function sorgulaSicil() {
        const tc = document.getElementById('tc-input').value.trim();
        const sonucDiv = document.getElementById('sicil-sonuc');
        
        if(tc.length !== 11 || isNaN(tc)) {
            alert('Lütfen 11 haneli TC kimlik numarası girin!');
            return;
        }
        
        sonucDiv.style.display = 'block';
        sonucDiv.className = 'result-box';
        sonucDiv.innerHTML = '<div style="text-align: center"><span class="loading"></span> TC aranıyor...</div>';
        
        try {
            const response = await fetch(`/api/sicil?tc=${tc}`);
            const data = await response.json();
            
            if(response.ok) {
                sonucDiv.className = 'result-box success';
            } else {
                sonucDiv.className = 'result-box error';
            }
            
            sonucDiv.innerHTML = JSON.stringify(data, null, 2);
        } catch(error) {
            sonucDiv.className = 'result-box error';
            sonucDiv.innerHTML = JSON.stringify({
                hata: 'Bağlantı hatası',
                detay: error.toString(),
                zaman: new Date().toISOString()
            }, null, 2);
        }
    }
    
    async function testDosyalari() {
        alert('📁 data.txt ve sicil.txt dosyaları ana dizinde olmalı!');
    }
    </script>
</body>
</html>
'''

# ===================================== #
#              YARDIMCI FONKSİYONLAR    #
# ===================================== #

def plaka_kontrol(plaka):
    """Plaka formatını kontrol eder"""
    if not plaka or not isinstance(plaka, str):
        return False
    plaka = plaka.upper().strip()
    return len(plaka) >= 5

def tc_kontrol(tc):
    """TC Kimlik numarası formatını kontrol eder"""
    if not tc or not isinstance(tc, str):
        return False
    tc = tc.strip()
    return bool(re.match(r'^[1-9][0-9]{10}$', tc))

def dosya_kontrol(dosya_adi):
    """Dosyanın var olup olmadığını kontrol eder"""
    if not os.path.exists(dosya_adi):
        return False
    return True

def plaka_ara(plaka):
    """
    data.txt dosyasında plakayı arar
    """
    try:
        plaka = plaka.upper().strip()
        
        # Dosya kontrolü
        if not dosya_kontrol(PLAKA_DOSYA):
            return {
                "hata": f"{PLAKA_DOSYA} dosyası bulunamadı!",
                "cozum": "Lütfen data.txt dosyasını ana dizine yükleyin",
                "durum": "hata",
                "zaman": datetime.now().isoformat()
            }
        
        with open(PLAKA_DOSYA, 'r', encoding='utf-8') as dosya:
            for satir in dosya:
                satir = satir.strip()
                if not satir or satir.startswith('#'):
                    continue
                
                # Önce virgülle ayırmayı dene
                if ',' in satir:
                    parcalar = satir.split(',')
                    mevcut_plaka = parcalar[0].strip().upper()
                    
                    if mevcut_plaka == plaka:
                        # Tüm bilgileri topla
                        bilgiler = {
                            "plaka": mevcut_plaka,
                            "durum": "bulundu",
                            "zaman": datetime.now().isoformat(),
                            "api": "plaka-api-v1"
                        }
                        
                        # Eğer yeterli bilgi varsa anlamlı alanlara ayır
                        if len(parcalar) >= 2:
                            bilgiler["sahip"] = parcalar[1].strip()
                        if len(parcalar) >= 3:
                            bilgiler["yil"] = parcalar[2].strip()
                        if len(parcalar) >= 4:
                            bilgiler["marka"] = parcalar[3].strip()
                        if len(parcalar) >= 5:
                            bilgiler["renk"] = parcalar[4].strip()
                        if len(parcalar) >= 6:
                            bilgiler["sehir"] = parcalar[5].strip()
                        
                        return bilgiler
                
                # Boşlukla ayrılmış dene
                elif ' ' in satir:
                    parcalar = satir.split()
                    mevcut_plaka = parcalar[0].strip().upper()
                    
                    if mevcut_plaka == plaka:
                        return {
                            "plaka": mevcut_plaka,
                            "bilgi": ' '.join(parcalar[1:]),
                            "durum": "bulundu",
                            "zaman": datetime.now().isoformat(),
                            "api": "plaka-api-v1"
                        }
        
        # Plaka bulunamadı
        return {
            "plaka": plaka,
            "durum": "bulunamadi",
            "mesaj": f"{plaka} plakası kayıtlarda bulunamadı",
            "zaman": datetime.now().isoformat(),
            "api": "plaka-api-v1"
        }
        
    except Exception as e:
        return {
            "hata": f"Plaka sorgulama hatası: {str(e)}",
            "durum": "hata",
            "zaman": datetime.now().isoformat()
        }

def sicil_ara(tc):
    """
    sicil.txt dosyasında TC'yi arar
    """
    try:
        tc = tc.strip()
        
        # Dosya kontrolü
        if not dosya_kontrol(SICIL_DOSYA):
            return {
                "hata": f"{SICIL_DOSYA} dosyası bulunamadı!",
                "cozum": "Lütfen sicil.txt dosyasını ana dizine yükleyin",
                "durum": "hata",
                "zaman": datetime.now().isoformat()
            }
        
        with open(SICIL_DOSYA, 'r', encoding='utf-8') as dosya:
            for satir in dosya:
                satir = satir.strip()
                if not satir or satir.startswith('#'):
                    continue
                
                # Virgülle ayrılmış varsayalım
                if ',' in satir:
                    parcalar = satir.split(',')
                    mevcut_tc = parcalar[0].strip()
                    
                    if mevcut_tc == tc:
                        # Sicil bilgilerini düzenle
                        sicil_bilgi = {
                            "tc": mevcut_tc,
                            "durum": "bulundu",
                            "zaman": datetime.now().isoformat(),
                            "api": "sicil-api-v1"
                        }
                        
                        # Eğer yeterli parça varsa anlamlı alanlara ayır
                        if len(parcalar) >= 2:
                            sicil_bilgi["ad_soyad"] = parcalar[1].strip()
                        if len(parcalar) >= 3:
                            sicil_bilgi["il"] = parcalar[2].strip()
                        if len(parcalar) >= 4:
                            sicil_bilgi["sicil_durumu"] = parcalar[3].strip()
                        if len(parcalar) >= 5:
                            sicil_bilgi["dogum_tarihi"] = parcalar[4].strip()
                        if len(parcalar) >= 6:
                            sicil_bilgi["meslek"] = parcalar[5].strip()
                        
                        return sicil_bilgi
        
        # TC bulunamadı
        return {
            "tc": tc,
            "durum": "bulunamadi",
            "mesaj": f"{tc} TC kimlik numarası kayıtlarda bulunamadı",
            "zaman": datetime.now().isoformat(),
            "api": "sicil-api-v1"
        }
        
    except Exception as e:
        return {
            "hata": f"Sicil sorgulama hatası: {str(e)}",
            "durum": "hata",
            "zaman": datetime.now().isoformat()
        }

# ===================================== #
#              API ROUTES               #
# ===================================== #

@app.route('/')
def ana_sayfa():
    """Ana sayfa - Render uyumlu arayüz"""
    return render_template_string(RENDER_TEMPLATE)

@app.route('/api/plaka', methods=['GET', 'POST'])
def plaka_api():
    """Plaka sorgulama API'si"""
    
    # İstekten plakayı al
    if request.method == 'GET':
        plaka = request.args.get('plaka')
    else:  # POST
        data = request.get_json()
        plaka = data.get('plaka') if data else None
    
    # Plaka kontrolü
    if not plaka:
        return jsonify({
            "hata": "Plaka belirtilmedi",
            "kullanim": {
                "get": "/api/plaka?plaka=34KG4978",
                "post": '{"plaka": "34KG4978"}'
            },
            "durum": "hata",
            "zaman": datetime.now().isoformat()
        }), 400
    
    # Plaka formatı kontrolü
    if not plaka_kontrol(plaka):
        return jsonify({
            "hata": "Geçersiz plaka formatı",
            "mesaj": "Plaka en az 5 karakter olmalıdır",
            "durum": "hata",
            "zaman": datetime.now().isoformat()
        }), 400
    
    # Ara ve sonucu döndür
    sonuc = plaka_ara(plaka)
    
    # Log kaydı
    logging.info(f"Plaka sorgulama: {plaka} - {sonuc.get('durum')}")
    
    # HTTP status code belirle
    if sonuc.get('durum') == 'bulundu':
        return jsonify(sonuc), 200
    elif sonuc.get('durum') == 'bulunamadi':
        return jsonify(sonuc), 404
    else:
        return jsonify(sonuc), 500

@app.route('/api/sicil', methods=['GET', 'POST'])
def sicil_api():
    """Sicil sorgulama API'si"""
    
    # İstekten TC'yi al
    if request.method == 'GET':
        tc = request.args.get('tc')
    else:  # POST
        data = request.get_json()
        tc = data.get('tc') if data else None
    
    # TC kontrolü
    if not tc:
        return jsonify({
            "hata": "TC kimlik numarası belirtilmedi",
            "kullanim": {
                "get": "/api/sicil?tc=12345678901",
                "post": '{"tc": "12345678901"}'
            },
            "durum": "hata",
            "zaman": datetime.now().isoformat()
        }), 400
    
    # TC formatı kontrolü
    if not tc_kontrol(tc):
        return jsonify({
            "hata": "Geçersiz TC kimlik numarası",
            "mesaj": "TC kimlik numarası 11 haneli ve rakamlardan oluşmalıdır",
            "durum": "hata",
            "zaman": datetime.now().isoformat()
        }), 400
    
    # Ara ve sonucu döndür
    sonuc = sicil_ara(tc)
    
    # Log kaydı
    logging.info(f"TC sorgulama: {tc} - {sonuc.get('durum')}")
    
    # HTTP status code belirle
    if sonuc.get('durum') == 'bulundu':
        return jsonify(sonuc), 200
    elif sonuc.get('durum') == 'bulunamadi':
        return jsonify(sonuc), 404
    else:
        return jsonify(sonuc), 500

@app.route('/api/dokuman', methods=['GET'])
def api_dokuman():
    """API dokümantasyonu"""
    return jsonify({
        "api_adi": "Çift API - Render Edition",
        "versiyon": "2.0",
        "aciklama": "data.txt (plaka) ve sicil.txt (TC) ile çalışan çift fonksiyonlu API",
        "base_url": request.host_url.rstrip('/'),
        "endpoints": [
            {
                "path": "/api/plaka",
                "methods": ["GET", "POST"],
                "aciklama": "Plaka bilgisi sorgular (data.txt)",
                "parametreler": {
                    "get": "?plaka=34KG4978",
                    "post": '{"plaka": "34KG4978"}'
                },
                "dosya": "data.txt",
                "ornk_cevap": {
                    "plaka": "34KG4978",
                    "sahip": "Oğuzhan Uğur",
                    "yil": "2020",
                    "marka": "BMW",
                    "renk": "Siyah",
                    "sehir": "İstanbul",
                    "durum": "bulundu",
                    "zaman": "2024-01-01T12:00:00"
                }
            },
            {
                "path": "/api/sicil",
                "methods": ["GET", "POST"],
                "aciklama": "TC Kimlik ile sicil sorgular (sicil.txt)",
                "parametreler": {
                    "get": "?tc=12345678901",
                    "post": '{"tc": "12345678901"}'
                },
                "dosya": "sicil.txt",
                "ornk_cevap": {
                    "tc": "12345678901",
                    "ad_soyad": "Ahmet Yılmaz",
                    "il": "İstanbul",
                    "sicil_durumu": "Temiz sicil",
                    "dogum_tarihi": "15.03.1990",
                    "meslek": "İnşaat Mühendisi",
                    "durum": "bulundu",
                    "zaman": "2024-01-01T12:00:00"
                }
            }
        ],
        "durum_kodlari": {
            "200": "Başarılı - Veri bulundu",
            "404": "Veri bulunamadı",
            "400": "Hatalı istek - Parametre eksik/hatalı",
            "500": "Sunucu hatası"
        },
        "dosyalar": {
            "plaka": "data.txt (ana dizinde olmalı)",
            "sicil": "sicil.txt (ana dizinde olmalı)"
        }
    })

@app.route('/api/saglik', methods=['GET'])
def saglik_kontrol():
    """Sağlık kontrolü - Render için"""
    return jsonify({
        "durum": "sağlıklı",
        "zaman": datetime.now().isoformat(),
        "dosyalar": {
            "data.txt": os.path.exists(PLAKA_DOSYA),
            "sicil.txt": os.path.exists(SICIL_DOSYA)
        }
    })

# ===================================== #
#              ANA ÇALIŞTIRMA           #
# ===================================== #

if __name__ == '__main__':
    print("="*60)
    print("🚀 ÇİFT API - RENDER EDITION")
    print("="*60)
    print(f"\n📁 Ana dizindeki dosyalar:")
    print(f"   - data.txt  : {'✅ Var' if os.path.exists(PLAKA_DOSYA) else '❌ Yok'}")
    print(f"   - sicil.txt : {'✅ Var' if os.path.exists(SICIL_DOSYA) else '❌ Yok'}")
    print(f"\n🌐 API Adresleri:")
    print(f"   Ana Sayfa : http://localhost:{port}/")
    print(f"   Plaka API : http://localhost:{port}/api/plaka?plaka=34KG4978")
    print(f"   Sicil API : http://localhost:{port}/api/sicil?tc=12345678901")
    print(f"   Doküman   : http://localhost:{port}/api/dokuman")
    print(f"   Sağlık     : http://localhost:{port}/api/saglik")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port)
