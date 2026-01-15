# RPi-Cam: Inteligentní kamerový systém

## Přehled projektu
Kamerový systém pro Raspberry Pi 4 s AI detekcí objektů, WebSocket streamingem a webovým rozhraním.

**Cílová složka:** `/Users/martinkoudela/Desktop/developing/rpi-cam`

## Technologický stack
- **Backend:** Python 3.11+ / FastAPI / WebSocket
- **AI:** YOLOv8 Nano (Ultralytics) + fallback na MobileNet SSD
- **Kamera:** Picamera2 (oficiální knihovna pro Camera Module 3)
- **GPIO:** gpiozero (pro PIR senzor)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Notifikace:** python-telegram-bot

## Struktura projektu

```
rpi-cam/
├── backend/
│   ├── main.py                 # FastAPI aplikace, WebSocket server
│   ├── camera.py               # Picamera2 wrapper, frame capture
│   ├── detector.py             # AI detekce (YOLO/MobileNet)
│   ├── gpio_handler.py         # PIR senzor, GPIO eventy
│   ├── notifications.py        # Telegram notifikace
│   ├── config.py               # Konfigurace (env variables)
│   ├── models/                 # AI modely (YOLOv8n, MobileNet)
│   └── recordings/             # Uložené snímky a videa
├── frontend/
│   ├── index.html              # Hlavní stránka
│   ├── css/
│   │   └── style.css           # Styly
│   └── js/
│       ├── app.js              # Hlavní logika
│       ├── websocket.js        # WebSocket klient
│       └── ui.js               # UI komponenty
├── requirements.txt            # Python závislosti
├── .env.example                # Vzorová konfigurace
└── README.md                   # Dokumentace (pouze na vyžádání)
```

## Implementační fáze

### Fáze 1: Základní struktura a WebSocket stream
**Soubory:** `main.py`, `camera.py`, `config.py`, `frontend/*`

1. Vytvořit strukturu složek
2. FastAPI aplikace s WebSocket endpointem
3. Simulovaný kamerový stream (pro vývoj na macOS)
4. Frontend s live preview
5. Základní UI (start/stop stream tlačítka)

**Testování:** Spustit server, otevřít browser, ověřit WebSocket spojení

### Fáze 2: AI detekce objektů
**Soubory:** `detector.py`

1. Integrace YOLOv8 Nano (ultralytics)
2. Detekce: osoby, zvířata, vozidla, objekty
3. Bounding boxy s labely ve streamu
4. Konfigurovatelná confidence threshold
5. FPS optimalizace (skip frames pro detekci)

**Testování:** Stream s overlays detekcí, ověřit FPS

### Fáze 3: PIR senzor integrace
**Soubory:** `gpio_handler.py`

1. PIR senzor monitoring (gpiozero)
2. Event-driven aktivace kamery
3. Cooldown mezi detekcemi
4. Mock mód pro vývoj bez GPIO

**Testování:** Simulovat GPIO eventy, ověřit aktivaci streamu

### Fáze 4: Nahrávání a ukládání
**Soubory:** `main.py`, `camera.py`

1. Ukládání snímků při detekci
2. Nahrávání video clipů (pre-buffer + post-buffer)
3. Automatické mazání starých záznamů
4. API endpoint pro stahování záznamů

**Testování:** Trigger detekce, ověřit uložené soubory

### Fáze 5: Telegram notifikace
**Soubory:** `notifications.py`

1. Telegram Bot integrace
2. Notifikace při detekci pohybu/osoby
3. Odesílání snímků do chatu
4. Konfigurovatelné typy notifikací

**Testování:** Trigger detekce, ověřit Telegram zprávu

### Fáze 6 (budoucí): Rozšíření
- Digitální zoom na detekovaný objekt
- Web Push notifikace (PWA)
- Více kamer
- Tailscale remote access optimalizace

## Klíčové závislosti (requirements.txt)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0
opencv-python-headless>=4.8.0
ultralytics>=8.0.0      # YOLOv8
numpy>=1.24.0
python-dotenv>=1.0.0
python-telegram-bot>=20.0
Pillow>=10.0.0

# Pouze pro Raspberry Pi:
# picamera2>=0.3.12
# gpiozero>=2.0
# RPi.GPIO>=0.7.1
```

## Konfigurace (.env)

```env
# Server
HOST=0.0.0.0
PORT=8000

# Camera
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=30

# AI Detection
DETECTION_ENABLED=true
DETECTION_MODEL=yolov8n
DETECTION_CONFIDENCE=0.5
DETECTION_INTERVAL=3  # Detekce každý N-tý frame

# PIR Sensor
PIR_PIN=17
PIR_COOLDOWN=10

# Telegram
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id

# Recordings
RECORDINGS_PATH=./recordings
MAX_RECORDINGS_GB=10
```

## Poznámky pro vývoj

### Vývoj na macOS (bez RPi)
- Kamera: Použít OpenCV s webkamerou nebo test video
- GPIO: Mock mód s klávesovými zkratkami
- AI: Funguje normálně

### Nasazení na Raspberry Pi
1. Zkopírovat projekt na RPi
2. Nainstalovat závislosti: `pip install -r requirements.txt`
3. Nainstalovat RPi specifické: `pip install picamera2 gpiozero`
4. Nastavit `.env`
5. Spustit: `python backend/main.py`

## Verifikace
1. **Stream:** Otevřít `http://localhost:8000` → živý obraz
2. **Detekce:** Viditelné bounding boxy kolem objektů
3. **PIR:** Stisknout mock tlačítko → stream se aktivuje
4. **Nahrávání:** Detekce → soubor v `recordings/`
5. **Telegram:** Detekce → zpráva v Telegram chatu
