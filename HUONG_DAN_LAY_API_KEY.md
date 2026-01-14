# Hướng dẫn lấy API Key cho AI Integration

## 🔑 Lấy Google Gemini API Key

### Bước 1: Truy cập Google AI Studio
1. Vào: https://aistudio.google.com/app/apikey
2. Đăng nhập bằng tài khoản Google

### Bước 2: Tạo API Key
1. Click **"Create API Key"** hoặc **"Get API Key"**
2. Chọn project (hoặc tạo project mới)
3. Copy API key được tạo (dạng: `AIza...`)

### Bước 3: Cấu hình trong Odoo
1. Vào Odoo → **AI & API → Cấu hình AI**
2. Chọn **AI Provider**: Google Gemini
3. Dán API key vào **Gemini API Key**
4. Chọn Model: **Gemini Pro**
5. Click **Save**

### ⚠️ Lưu ý:
- API key bắt đầu bằng `AIza...`
- Không có khoảng trắng ở đầu/cuối
- Copy đầy đủ toàn bộ key
- Giữ bí mật API key, không chia sẻ công khai

## 🔑 Lấy OpenAI API Key (nếu dùng OpenAI)

### Bước 1: Truy cập OpenAI Platform
1. Vào: https://platform.openai.com/api-keys
2. Đăng nhập/Đăng ký tài khoản

### Bước 2: Tạo API Key
1. Click **"Create new secret key"**
2. Đặt tên cho key (ví dụ: "Odoo AI Integration")
3. Copy API key (dạng: `sk-...`)

### Bước 3: Cấu hình trong Odoo
1. Vào Odoo → **AI & API → Cấu hình AI**
2. Chọn **AI Provider**: OpenAI
3. Dán API key vào **OpenAI API Key**
4. Chọn Model: **GPT-3.5 Turbo** (rẻ) hoặc **GPT-4** (mạnh hơn)
5. Click **Save**

### ⚠️ Lưu ý:
- API key bắt đầu bằng `sk-...`
- OpenAI tính phí theo usage (có free tier)
- Kiểm tra billing/credit trước khi sử dụng

## 🧪 Test API Key

Sau khi cấu hình:
1. Vào **AI & API → Trợ lý ảo**
2. Nhập câu hỏi: "Giờ làm việc là mấy giờ?"
3. Click **Hỏi AI**
4. Nếu thành công → API key hợp lệ ✅
5. Nếu lỗi → Kiểm tra lại API key

## ❌ Các lỗi thường gặp

### "API key not valid"
- **Nguyên nhân**: API key sai hoặc đã hết hạn
- **Giải pháp**: Lấy API key mới và cập nhật lại

### "Quota exceeded"
- **Nguyên nhân**: Đã vượt quá giới hạn sử dụng
- **Giải pháp**: Đợi reset quota hoặc nâng cấp plan

### "Invalid API key format"
- **Nguyên nhân**: Copy thiếu hoặc có khoảng trắng thừa
- **Giải pháp**: Copy lại API key, đảm bảo không có khoảng trắng

## 💡 Tips

1. **Gemini (Miễn phí)**: 
   - Free tier: 60 requests/phút
   - Phù hợp cho testing và sử dụng nhỏ

2. **OpenAI (Có phí)**:
   - GPT-3.5 Turbo: Rẻ, nhanh
   - GPT-4: Đắt hơn, mạnh hơn
   - Có free credit $5 khi đăng ký mới

3. **Bảo mật**:
   - Không commit API key vào git
   - Chỉ nhập trong Odoo, không lưu trong code
   - Rotate API key định kỳ

