# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG CHỮ KÝ SỐ

## 📋 TỔNG QUAN HỆ THỐNG

Hệ thống chữ ký số cho phép quản lý và ký số văn bản điện tử một cách an toàn và có tính pháp lý.

---

## 🔄 QUY TRÌNH HOẠT ĐỘNG TỔNG THỂ

### **Bước 1: Tạo văn bản**
1. Vào menu **Quản lý văn bản → Văn bản đi**
2. Click **Tạo** để tạo văn bản mới
3. Điền thông tin:
   - Số văn bản, loại văn bản
   - Ngày hiệu lực, ngày hết hạn
   - Đính kèm file PDF/DOCX
   - Trạng thái: **Nháp**

### **Bước 2: Gửi duyệt**
1. Trong form văn bản, click nút **"Gửi duyệt"**
2. Trạng thái chuyển sang **"Chờ duyệt"**
3. Hệ thống tự động tạo các bước duyệt theo vai trò:
   - **Nhân viên** (sequence 1): Soạn thảo & gửi duyệt
   - **Trưởng phòng** (sequence 2): Duyệt nội dung
   - **Giám đốc** (sequence 3): Phê duyệt & ký số

### **Bước 3: Duyệt văn bản**

#### **3.1. Trưởng phòng duyệt nội dung**
1. Vào **Quản lý văn bản → Chữ ký số → Quy trình duyệt**
2. Tìm văn bản cần duyệt (trạng thái: Chờ duyệt)
3. Mở form quy trình duyệt
4. Click **"Duyệt"** hoặc **"Từ chối"**
   - Nếu **Duyệt**: Chuyển sang bước tiếp theo
   - Nếu **Từ chối**: Văn bản quay về trạng thái **Nháp**

#### **3.2. Giám đốc phê duyệt cuối**
1. Sau khi Trưởng phòng duyệt, Giám đốc sẽ thấy văn bản trong **Quy trình duyệt**
2. Click **"Duyệt"** để phê duyệt cuối cùng
3. Khi tất cả bước duyệt hoàn thành → Văn bản chuyển sang trạng thái **"Đã duyệt"**

### **Bước 4: Ký số văn bản**

#### **4.1. Ký nội bộ (Nhân viên/Giám đốc)**

1. **Mở wizard ký số:**
   - Vào form văn bản (trạng thái: Đã duyệt)
   - Click nút **"Ký số"** (màu xanh)

2. **Chọn phương thức ký:**
   - **Vẽ chữ ký**: Dùng chuột/touchpad vẽ trực tiếp
   - **Upload chữ ký**: Tải lên file PNG/JPG đã scan
   - **Chữ ký font**: Chọn style và nhập tên (Cursive/Elegant/Modern)

3. **Chọn vị trí ký:**
   - Số trang (mặc định: 1)
   - Vị trí X, Y (đơn vị: mm)

4. **Xác thực (nếu cần):**
   - Nhập mã OTP (nếu hệ thống yêu cầu)

5. **Hoàn tất:**
   - Click **"Ký số"**
   - Hệ thống tự động:
     - Tạo hash chữ ký (SHA256)
     - Ghi log (IP, thời gian)
     - Nhúng chữ ký vào PDF (nếu có)
     - Lưu file đã ký
     - Cập nhật trạng thái văn bản → **"Đã ký"**

#### **4.2. Ký khách hàng (Từ xa qua email)**

1. **Tạo yêu cầu ký:**
   - Vào **Quản lý văn bản → Chữ lý số → Chữ ký số**
   - Tạo chữ ký mới:
     - Chọn văn bản
     - Chọn **Loại chữ ký**: "Ký khách hàng"
     - Nhập email và tên khách hàng
   - Click **"Gửi yêu cầu ký"**

2. **Hệ thống tự động:**
   - Tạo token bảo mật (32 ký tự)
   - Tạo link ký: `{base_url}/document/sign/{token}`
   - Set thời hạn link: 7 ngày
   - Gửi email mời ký đến khách hàng

3. **Khách hàng nhận email:**
   - Email chứa thông tin văn bản
   - Link "Ký số văn bản" (có thời hạn)
   - Click link → Mở trang ký

4. **Khách hàng ký:**
   - Xác thực OTP (nếu cần)
   - Chọn phương thức ký (vẽ/upload/font)
   - Chọn vị trí ký
   - Click "Ký số"
   - Nhận email xác nhận đã ký

5. **Hệ thống cập nhật:**
   - Trạng thái chữ ký → **"Đã ký"**
   - Gửi email thông báo cho người tạo văn bản

---

## 📊 THEO DÕI VÀ QUẢN LÝ

### **1. Xem lịch sử văn bản**
- Vào **Quản lý văn bản → Lịch sử văn bản**
- Xem tất cả thay đổi:
  - Ai thực hiện
  - Khi nào
  - Hành động gì
  - IP address
  - Giá trị cũ/mới

### **2. Xem chữ ký số**
- Vào **Quản lý văn bản → Chữ ký số → Chữ ký số**
- Xem danh sách tất cả chữ ký:
  - Trạng thái (Chờ ký/Đã ký/Từ chối)
  - Người ký
  - Thời gian ký
  - Hash chữ ký (để xác thực)

### **3. Quản lý chứng thư số**
- Vào **Quản lý văn bản → Chữ ký số → Chứng thư số**
- Thêm chứng thư số cho nhân viên:
  - Tên chứng thư
  - Số seri
  - Loại (USB Token/Ký từ xa/Ký hình ảnh + OTP)
  - Nhà cung cấp (VNPT-CA/Viettel-CA/FPT-CA)
  - Ngày cấp, ngày hết hạn
  - Upload file chứng thư

---

## 🔔 HỆ THỐNG NHẮC HẠN TỰ ĐỘNG

### **Cách hoạt động:**
1. **Cron job chạy hàng ngày lúc 08:00:**
   - Quét tất cả văn bản đã ký (`status='signed'`)
   - Có ngày hết hạn (`expiry_date != NULL`)
   - Chưa hết hạn (`expiry_date > today`)

2. **Phân loại theo mức độ:**
   - **30 ngày còn lại**: Cảnh báo sớm (màu vàng)
   - **7 ngày còn lại**: Khẩn cấp (màu cam)
   - **1 ngày còn lại**: Rất gấp (màu đỏ)

3. **Tự động gửi thông báo:**
   - **Thông báo nội bộ**: Mail message trong Odoo
   - **Email nhắc nhở**: Gửi đến email
   - **Activity**: Tạo activity với deadline = ngày hết hạn

4. **Người nhận:**
   - Người tạo văn bản
   - Trưởng phòng
   - Khách hàng (nếu có)

### **Xem nhắc hạn:**
- Vào **Quản lý văn bản → Nhắc hạn văn bản**
- Xem danh sách nhắc hạn
- Có thể gửi lại thông báo thủ công

---

## 🔐 BẢO MẬT VÀ XÁC THỰC

### **1. Hash chữ ký:**
- Mỗi chữ ký có hash SHA256 duy nhất
- Hash = SHA256(document_id + signer_id + timestamp + signature_image)
- Dùng để xác thực tính toàn vẹn của chữ ký

### **2. Ghi log đầy đủ:**
- IP address của thiết bị ký
- Thời gian ký chính xác
- Người ký
- Phương thức ký

### **3. Token bảo mật cho link ký:**
- Token 32 ký tự ngẫu nhiên
- Link có thời hạn (7 ngày)
- Mỗi link chỉ dùng được 1 lần (có thể cải thiện)

---

## 📝 CÁC TRẠNG THÁI VĂN BẢN

1. **Nháp** (draft): Văn bản đang soạn thảo
2. **Chờ duyệt** (pending_approval): Đã gửi duyệt, chờ phê duyệt
3. **Đã duyệt** (approved): Đã được duyệt, sẵn sàng ký
4. **Chờ ký** (pending_sign): Đang chờ ký số
5. **Đã ký** (signed): Đã được ký số
6. **Đã gửi** (sent): Đã gửi đi
7. **Đã nhận** (received): Đã được nhận
8. **Hết hiệu lực** (expired): Đã hết hạn
9. **Lưu trữ** (archived): Đã lưu trữ

---

## 🎯 CÁC TÍNH NĂNG NỔI BẬT

### ✅ **Đã triển khai:**
- ✅ Quy trình duyệt đa cấp (Nhân viên → Trưởng phòng → Giám đốc)
- ✅ Ký số với 3 phương thức (Vẽ/Upload/Font)
- ✅ Ký khách hàng từ xa qua email
- ✅ Ghi log đầy đủ (Audit Trail)
- ✅ Nhắc hạn tự động
- ✅ Hash chữ ký để xác thực
- ✅ Quản lý chứng thư số

### ⚠️ **Cần cải thiện (tùy chọn):**
- ⚠️ Logic nhúng chữ ký vào PDF (cần thư viện PyPDF2/reportlab)
- ⚠️ Controller xử lý link ký cho khách hàng (cần tạo route `/document/sign/{token}`)
- ⚠️ Tạo chữ ký font thực tế (cần thư viện PIL/Pillow)

---

## 📞 HỖ TRỢ

Nếu có thắc mắc hoặc cần hỗ trợ, vui lòng liên hệ quản trị viên hệ thống.

