# Hướng dẫn cài đặt Module Nhân sự

## 📋 Module đã tạo

Module `om_hr_custom` đã được tạo trong thư mục `addons/om_hr_custom/`

## 🚀 Các bước cài đặt

### Bước 1: Kiểm tra Odoo đang chạy

```bash
docker-compose ps
```

Đảm bảo container `odoo_17` đang chạy.

### Bước 2: Truy cập Odoo

Mở trình duyệt và truy cập: `http://localhost:8069`

### Bước 3: Kích hoạt Developer Mode

1. Đăng nhập vào Odoo
2. Vào **Settings** (Cài đặt)
3. Scroll xuống dưới, tìm phần **Activate the developer mode**
4. Click để kích hoạt Developer Mode

### Bước 4: Cập nhật Apps List

1. Vào **Apps** menu
2. Click **Update Apps List** (nút ở trên cùng)
3. Chờ cập nhật xong

### Bước 5: Cài đặt module

1. Trong **Apps**, tìm kiếm: `HR Management` hoặc `Nhân sự`
2. Hoặc tìm theo tên: `om_hr_custom`
3. Click vào module **"Odoo 17 HR Management**
4. Click nút **Install**

### Bước 6: Kiểm tra

Sau khi cài đặt xong:

1. Bạn sẽ thấy menu **"Nhân sự"** trong menu chính
2. Click vào **Nhân sự** → **Nhân viên**
3. Bạn có thể tạo nhân viên mới với các trường tùy chỉnh:
   - Mã nhân viên (tự động)
   - Ngày vào làm
   - Loại hợp đồng
   - Lương cơ bản
   - Kỹ năng
   - Ghi chú

## ⚠️ Lưu ý

### Nếu không thấy module trong Apps:

1. **Kiểm tra module có trong thư mục addons:**

   ```bash
   ls -la addons/om_hr_custom
   ```

2. **Restart Odoo container:**

   ```bash
   docker-compose restart web
   ```

3. **Kiểm tra logs nếu có lỗi:**
   ```bash
   docker-compose logs web | tail -50
   ```

### Nếu module cần module `hr`:

Module này phụ thuộc vào module `hr` của Odoo. Nếu chưa có:

1. Vào **Apps**
2. Tìm và cài đặt module **"Employees"** hoặc **"hr"**
3. Sau đó mới cài module `om_hr_custom`

## 📁 Cấu trúc module

```
addons/om_hr_custom/
├── __init__.py                    # File init chính
├── __manifest__.py                # Manifest file
├── README.md                       # Hướng dẫn
├── models/
│   ├── __init__.py
│   └── hr_employee.py             # Model nhân viên
├── views/
│   ├── hr_employee_views.xml      # Views (tree, form, search)
│   └── hr_menu_views.xml          # Menu
├── security/
│   └── ir.model.access.csv        # Quyền truy cập
├── data/
│   └── ir_sequence_data.xml       # Sequence cho mã NV
└── static/
    └── description/
        └── icon.png
```

## 🎯 Tính năng module

- ✅ Quản lý nhân viên với các trường tùy chỉnh
- ✅ Mã nhân viên tự động (NV0001, NV0002, ...)
- ✅ Tree view hiển thị mã NV, phòng ban, loại hợp đồng
- ✅ Form view với tab thông tin bổ sung
- ✅ Menu "Nhân sự" với submenu Nhân viên và Phòng ban
- ✅ Tìm kiếm theo mã NV và loại hợp đồng

## 🔧 Tùy chỉnh

Bạn có thể chỉnh sửa các file để thêm tính năng:

- `models/hr_employee.py` - Thêm trường mới
- `views/hr_employee_views.xml` - Thay đổi giao diện
- `views/hr_menu_views.xml` - Thêm menu mới

## 📝 Sau khi cài đặt

1. Vào menu **Nhân sự** → **Nhân viên**
2. Click **Create** để tạo nhân viên mới
3. Điền thông tin:
   - Tên nhân viên
   - Mã nhân viên (tự động)
   - Phòng ban
   - Chức vụ
   - Ngày vào làm
   - Loại hợp đồng
   - Lương cơ bản
4. Lưu và kiểm tra

Chúc bạn thành công! 🎉
