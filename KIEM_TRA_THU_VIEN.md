# Kiểm tra và cài đặt thư viện Python trong Docker

## Kiểm tra thư viện đã được cài chưa

```bash
docker exec -it odoo_17 pip3 list | grep -E "openai|google|pytesseract|Pillow|requests"
```

## Nếu chưa có, cài đặt thủ công:

```bash
# Vào container với quyền root
docker exec -it -u root odoo_17 bash

# Cài đặt dependencies hệ thống cho OCR
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-vie libtesseract-dev python3-pip

# Cài đặt thư viện Python
pip3 install openai google-generativeai requests pytesseract Pillow

# Thoát container
exit

# Restart Odoo
docker-compose restart web
```

## Hoặc rebuild Docker image:

```bash
docker-compose build web
docker-compose restart web
```

## Kiểm tra sau khi cài:

```bash
docker exec -it odoo_17 python3 -c "import openai; print('OpenAI OK')"
docker exec -it odoo_17 python3 -c "import google.generativeai; print('Gemini OK')"
docker exec -it odoo_17 python3 -c "import pytesseract; print('Tesseract OK')"
```

