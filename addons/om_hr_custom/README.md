# Module Quản lý Nhân sự - Odoo 17

Module quản lý nhân sự tùy chỉnh cho Odoo 17.

## Tính năng

- Quản lý thông tin nhân viên với các trường tùy chỉnh:
  - Mã nhân viên (tự động tạo)
  - Ngày vào làm
  - Loại hợp đồng (Toàn thời gian, Bán thời gian, Hợp đồng, Thực tập sinh)
  - Lương cơ bản
  - Kỹ năng
  - Ghi chú

- Views:
  - Tree view: Hiển thị danh sách nhân viên với mã NV, phòng ban, loại hợp đồng
  - Form view: Form chi tiết với tab thông tin bổ sung
  - Search view: Tìm kiếm theo mã NV và loại hợp đồng

- Menu:
  - Menu "Nhân sự" với các submenu:
    - Nhân viên
    - Phòng ban

## Cài đặt

1. Đảm bảo module `hr` đã được cài đặt
2. Copy module vào thư mục `addons`
3. Restart Odoo server
4. Vào Apps → Update Apps List
5. Tìm "Odoo 17 HR Management" và cài đặt

## Sử dụng

Sau khi cài đặt, bạn sẽ thấy menu "Nhân sự" trong Odoo. Click vào "Nhân viên" để xem danh sách và quản lý nhân viên.

## Cấu trúc module

```
om_hr_custom/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── hr_employee.py
├── views/
│   ├── hr_employee_views.xml
│   └── hr_menu_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── ir_sequence_data.xml
└── static/
    └── description/
```

## Tác giả

Your Company

## License

LGPL-3

