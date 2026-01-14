# Hướng dẫn cài đặt AI Integration Module

## Cách 1: Sử dụng Dockerfile (Khuyến nghị)

Module đã được cấu hình để tự động cài đặt các thư viện Python khi build Docker image.

### Bước 1: Rebuild Docker image
```bash
cd /Users/nabi/Downloads/Odoo_17
docker-compose build web
```

### Bước 2: Restart container
```bash
docker-compose restart web
```

## Cách 2: Cài đặt thủ công vào container đang chạy

Nếu không muốn rebuild, bạn có thể cài đặt trực tiếp vào container:

```bash
# Vào container
docker exec -it -u root odoo_17 bash

# Cài đặt dependencies hệ thống
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-vie libtesseract-dev python3-pip

# Cài đặt thư viện Python
pip3 install openai google-generativeai requests pytesseract Pillow

# Thoát container
exit

# Restart container
docker-compose restart web
```

## Cách 3: Sử dụng pip trên máy host (nếu có Python)

Nếu bạn có Python và pip trên máy Mac:

```bash
# Kiểm tra Python
python3 --version

# Cài đặt pip nếu chưa có
python3 -m ensurepip --upgrade

# Hoặc cài đặt pip qua Homebrew
brew install python3

# Sau đó cài đặt thư viện
pip3 install openai google-generativeai requests pytesseract Pillow
```

**Lưu ý**: Cách 3 chỉ cài đặt trên máy host, không ảnh hưởng đến Odoo trong Docker. Bạn vẫn cần cài đặt vào container.

## Kiểm tra cài đặt

Sau khi cài đặt, vào Odoo và kiểm tra:
1. Apps → Tìm "AI Integration & External API" → Install
2. Vào menu **AI & API → Cấu hình AI**
3. Nhập API keys và test các tính năng

## Lưu ý

- **Tesseract OCR**: Cần cài đặt trên hệ thống (đã có trong Dockerfile)
- **API Keys**: Cần lấy từ các nhà cung cấp:
  - OpenAI: https://platform.openai.com/api-keys
  - Gemini: https://makersuite.google.com/app/apikey
  - Telegram: Tạo bot qua @BotFather
  - Zalo: Tạo Official Account

