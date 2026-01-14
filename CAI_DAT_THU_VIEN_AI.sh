#!/bin/bash
# Script cài đặt thư viện Python cho AI Integration vào Docker container

echo "Đang cài đặt thư viện Python cho AI Integration..."

# Cài đặt dependencies hệ thống
echo "1. Cài đặt Tesseract OCR..."
docker exec -it -u root odoo_17 bash -c "apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-vie libtesseract-dev python3-pip"

# Cài đặt thư viện Python
echo "2. Cài đặt thư viện Python..."
docker exec -it -u root odoo_17 bash -c "pip3 install --no-cache-dir openai google-generativeai requests pytesseract Pillow"

# Kiểm tra cài đặt
echo "3. Kiểm tra cài đặt..."
docker exec -it odoo_17 python3 -c "import openai; print('✓ OpenAI OK')" 2>/dev/null || echo "✗ OpenAI chưa cài"
docker exec -it odoo_17 python3 -c "import google.generativeai; print('✓ Gemini OK')" 2>/dev/null || echo "✗ Gemini chưa cài"
docker exec -it odoo_17 python3 -c "import pytesseract; print('✓ Tesseract OK')" 2>/dev/null || echo "✗ Tesseract chưa cài"
docker exec -it odoo_17 python3 -c "from PIL import Image; print('✓ Pillow OK')" 2>/dev/null || echo "✗ Pillow chưa cài"

echo ""
echo "Hoàn thành! Restart Odoo:"
echo "docker-compose restart web"

