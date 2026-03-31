# FileForge

A production-ready Django REST API for converting documents and images between formats.

## Features

- **Documents**: PDF ↔ DOCX, DOC/DOCX/PPTX/XLSX → PDF
- **Images**: Convert between JPG, PNG, WebP, BMP, TIFF, GIF; image ↔ PDF
- Multi-page PDF → ZIP of images
- 50 MB upload limit, automatic file cleanup, security headers

---

## Deploy to Render

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/you/fileforge.git
git push -u origin main
```

### 2. Create a new Web Service on Render
- Connect your GitHub repo
- **Runtime**: Python
- **Build Command**:
  ```
  chmod +x build.sh && ./build.sh
  ```
- **Start Command**:
  ```
  gunicorn fileforge.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  ```
- **Health Check Path**: `/health/`

### 3. Set Environment Variables on Render

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | Generate (Render can auto-generate) |
| `DJANGO_DEBUG` | `False` |
| `CORS_ALLOWED_ORIGINS` | `https://yourfrontend.com` |

Render automatically sets `RENDER_EXTERNAL_HOSTNAME` — no need to set `ALLOWED_HOSTS` manually.

---

## Local Development

```bash
# 1. Clone and install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Install system deps (Ubuntu/Debian)
sudo apt install libreoffice poppler-utils

# 3. Set env
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY

# 4. Run
python manage.py migrate
python manage.py runserver
```

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/docs/convert/` | Convert any document format |
| POST | `/api/docs/to-pdf/` | DOC/DOCX → PDF shortcut |
| POST | `/api/images/convert/` | Convert image formats |
| POST | `/api/images/to-pdf/` | Image → PDF |
| POST | `/api/images/pdf-to-image/` | PDF → image (ZIP if multi-page) |
| GET | `/health/` | Health check |

See `api_docs.html` for full API documentation.

---

## Dependencies

- **Django 5** + Django REST Framework
- **pdf2docx** — PDF to DOCX conversion
- **Pillow** — Image processing
- **pdf2image** + **poppler** — PDF rasterization
- **LibreOffice** — Office format conversions
- **Gunicorn** + **WhiteNoise** — Production server
