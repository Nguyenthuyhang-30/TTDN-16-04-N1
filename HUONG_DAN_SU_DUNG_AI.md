# Hướng dẫn sử dụng AI Integration Module

## ✅ Đã hoàn thành cài đặt

Docker image đã được build thành công với các thư viện:
- ✅ OpenAI
- ✅ Google Gemini
- ✅ Tesseract OCR
- ✅ Pillow
- ✅ Requests

## Bước tiếp theo: Cài đặt module trong Odoo

### 1. Vào Odoo và cài đặt module

1. Mở trình duyệt: http://localhost:8069
2. Đăng nhập vào Odoo
3. Vào **Apps** (Ứng dụng)
4. Bỏ filter "Apps" (nếu có)
5. Tìm kiếm: **"AI Integration"** hoặc **"AI & External API"**
6. Click **Install**

### 2. Cấu hình API Keys

Sau khi cài đặt, vào menu **AI & API → Cấu hình AI**

#### a) Cấu hình OpenAI (nếu dùng)
- Lấy API Key: https://platform.openai.com/api-keys
- Nhập vào: **OpenAI API Key**
- Chọn Model: GPT-3.5 Turbo (rẻ) hoặc GPT-4 (mạnh hơn)

#### b) Cấu hình Google Gemini (nếu dùng)
- Lấy API Key: https://makersuite.google.com/app/apikey
- Nhập vào: **Gemini API Key**
- Chọn Model: Gemini Pro

#### c) Chọn AI Provider
- Chọn **OpenAI** hoặc **Google Gemini** làm provider chính

### 3. Sử dụng các tính năng AI

#### 📝 AI Tóm tắt văn bản

1. Vào menu **AI & API** (sẽ có sau khi cài module)
2. Tạo bản ghi mới "AI Tóm tắt văn bản"
3. Nhập nội dung cần tóm tắt vào **Nội dung gốc**
4. Chọn độ dài tóm tắt (Ngắn/Trung bình/Dài)
5. Click **Tóm tắt** → AI sẽ tự động tóm tắt

#### 📷 OCR Bóc tách dữ liệu

1. Tạo bản ghi mới "OCR Bóc tách"
2. Chọn loại tài liệu: Hóa đơn, CV, Hợp đồng...
3. Upload hình ảnh hoặc file PDF
4. Click **Bóc tách** → Hệ thống sẽ:
   - OCR để lấy văn bản từ hình ảnh
   - AI xử lý và cấu trúc hóa dữ liệu

#### 🤖 Trợ lý ảo giải đáp nội quy

1. Vào menu **AI & API → Trợ lý ảo** (hoặc từ bất kỳ đâu)
2. Chọn chủ đề: Nhân sự, Chấm công, Lương thưởng...
3. Nhập câu hỏi
4. Click **Hỏi AI** → AI sẽ trả lời dựa trên nội quy công ty

### 4. External API (Tùy chọn)

#### 📱 Telegram Notifications

1. Tạo bot qua @BotFather trên Telegram
2. Lấy Bot Token
3. Lấy Chat ID (có thể dùng @userinfobot)
4. Nhập vào cấu hình AI
5. Sử dụng API: `/ai/send_telegram` để gửi thông báo

#### 📱 Zalo Notifications

1. Tạo Zalo Official Account
2. Lấy OA ID và Access Token
3. Nhập vào cấu hình AI
4. Sử dụng API: `/ai/send_zalo` để gửi thông báo

#### 📅 Google Calendar Sync

1. Tạo Google OAuth Client ID
2. Nhập Client ID và Client Secret
3. Tạo sự kiện và đồng bộ lên Google Calendar

## Lưu ý quan trọng

⚠️ **API Keys**: 
- Giữ bí mật API keys, không chia sẻ công khai
- OpenAI và Gemini có thể tính phí theo usage
- Nên test với lượng nhỏ trước

⚠️ **OCR**:
- Cần hình ảnh rõ ràng, chất lượng tốt
- Hỗ trợ tiếng Việt và tiếng Anh
- PDF cần được convert sang hình ảnh trước

⚠️ **Performance**:
- AI processing có thể mất vài giây
- Nên có kết nối internet ổn định
- Có thể bị rate limit từ API providers

## Troubleshooting

### Lỗi "Module not found"
- Kiểm tra module đã được install chưa
- Restart Odoo: `docker-compose restart web`
- Upgrade module trong Odoo

### Lỗi "API Key invalid"
- Kiểm tra lại API key đã nhập đúng chưa
- Kiểm tra API key còn hiệu lực không
- Kiểm tra có đủ credit/quota không

### Lỗi "Import error"
- Kiểm tra các thư viện đã được cài trong container:
  ```bash
  docker exec -it odoo_17 pip3 list | grep openai
  ```

## Test nhanh

Sau khi cấu hình xong, test nhanh:

1. **Test AI Tóm tắt**:
   - Tạo bản ghi mới
   - Nhập: "Công ty chúng tôi có giờ làm việc từ 8h30 đến 17h30, giờ nghỉ từ 12h30 đến 13h30"
   - Click "Tóm tắt" → Xem kết quả

2. **Test Trợ lý ảo**:
   - Mở wizard
   - Hỏi: "Giờ làm việc là mấy giờ?"
   - Xem AI trả lời

Chúc bạn sử dụng thành công! 🚀

