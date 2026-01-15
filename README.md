# RPi-Cam

AI-powered security camera system for Raspberry Pi 4 with real-time object detection and web streaming.

## Features

- Live video streaming via WebSocket
- AI object detection (YOLOv8) - people, animals, vehicles
- PIR motion sensor integration
- Telegram notifications with snapshots
- Web-based control panel
- Recording on motion detection

## Hardware

- Raspberry Pi 4 (4GB RAM)
- Raspberry Pi Camera Module 3 NoIR
- PIR motion sensor

## Tech Stack

- **Backend:** Python, FastAPI, WebSocket
- **AI:** YOLOv8 (Ultralytics)
- **Camera:** Picamera2
- **Frontend:** HTML/CSS/JavaScript

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/rpi-cam.git
cd rpi-cam

# Create virtual environment
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
python backend/main.py
```

## Configuration

Copy `.env.example` to `.env` and configure:

- `TELEGRAM_BOT_TOKEN` - Telegram bot token for notifications
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID
- `DETECTION_CONFIDENCE` - AI detection threshold (0.0-1.0)

## License

MIT
