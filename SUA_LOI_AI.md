# Hướng dẫn sửa lỗi Internal Server Error

## ✅ Đã sửa các vấn đề:

1. **Cập nhật OpenAI API** - Sử dụng client mới (v1.0+) thay vì API cũ
2. **Xử lý import errors** - Tất cả imports được đặt trong try-except
3. **Loại bỏ imports không cần thiết** - Xóa các import không dùng đến

## Bước tiếp theo:

### 1. Restart Odoo để load lại code mới

```bash
cd /Users/nabi/Downloads/Odoo_17
docker-compose restart web
```

### 2. Upgrade module trong Odoo

1. Vào **Apps**
2. Tìm **"AI Integration"**
3. Click **Upgrade** (nếu đã cài) hoặc **Install** (nếu chưa cài)

### 3. Kiểm tra logs nếu vẫn lỗi

```bash
docker logs odoo_17 --tail 100
```

Tìm dòng có chứa "Error", "Traceback", hoặc "Exception" để xem lỗi cụ thể.

## Các lỗi thường gặp và cách sửa:

### Lỗi: "Module not found: openai"
- **Nguyên nhân**: Thư viện chưa được cài trong container
- **Giải pháp**: Đã được cài trong Dockerfile, nhưng nếu vẫn lỗi:
  ```bash
  docker exec -it -u root odoo_17 pip3 install openai google-generativeai
  ```

### Lỗi: "AttributeError: module 'openai' has no attribute 'ChatCompletion'"
- **Nguyên nhân**: Đang dùng OpenAI API cũ
- **Giải pháp**: Đã sửa để dùng client mới (OpenAI v1.0+)

### Lỗi: "ImportError: No module named 'pytesseract'"
- **Nguyên nhân**: Thư viện OCR chưa được cài
- **Giải pháp**: 
  ```bash
  docker exec -it -u root odoo_17 pip3 install pytesseract Pillow
  docker exec -it -u root odoo_17 apt-get install -y tesseract-ocr tesseract-ocr-vie
  ```

## Nếu vẫn gặp lỗi:

1. Kiểm tra logs chi tiết:
   ```bash
   docker logs odoo_17 --tail 200 | grep -i error
   ```

2. Kiểm tra module có được load không:
   - Vào Odoo → Settings → Technical → Database Structure → Models
   - Tìm "ai.config" hoặc "ai.document.summary"

3. Thử uninstall và install lại module:
   - Apps → AI Integration → Uninstall
   - Sau đó Install lại

4. Kiểm tra dependencies:
   ```bash
   docker exec -it odoo_17 pip3 list | grep -E "openai|google|pytesseract|Pillow"
   ```

