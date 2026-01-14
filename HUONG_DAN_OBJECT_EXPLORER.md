# Hướng dẫn xem Databases và Tables trong Object Explorer

## 🎯 Mục tiêu
Hiển thị databases và tables trong Object Explorer của VS Code PostgreSQL extension giống như trong PostgreSQL Server.

## 📋 Các databases hiện có
- `postgres` - Database mặc định
- `nguyenhang.3010` - Database Odoo của bạn

## 🔍 Cách 1: Xem database postgres (đang kết nối)

### Bước 1: Mở rộng cây trong Object Explorer
1. Tìm "postgres" trong Object Explorer
2. Click vào mũi tên `>` để mở rộng
3. Tìm "Schemas (1)" → click mở rộng
4. Tìm "public" → click mở rộng
5. Bạn sẽ thấy các loại objects:
   - **Tables** - Các bảng dữ liệu
   - **Views** - Các view
   - **Functions** - Các hàm
   - **Procedures** - Các thủ tục
   - Và nhiều loại khác

### Bước 2: Xem Tables
1. Mở rộng "Tables" (nếu có)
2. Bạn sẽ thấy danh sách tất cả tables trong database postgres

## 🔍 Cách 2: Kết nối vào database nguyenhang.3010

### Tạo kết nối mới:
1. Click icon "+" hoặc chuột phải trong Object Explorer → "New Connection"
2. Điền thông tin:
   ```
   Server Name: Odoo Database
   Host: localhost
   Port: 5434
   Database: nguyenhang.3010  ← QUAN TRỌNG!
   User: odoo
   Password: odoo
   ```
3. Click "Connect"
4. Sau khi kết nối, bạn sẽ thấy "nguyenhang.3010" trong Object Explorer
5. Mở rộng: `nguyenhang.3010` → `Schemas` → `public` → `Tables`
6. Bạn sẽ thấy TẤT CẢ tables của Odoo!

## 🔍 Cách 3: Dùng SQL Query

### Xem danh sách databases:
```sql
SELECT 
    datname as "Database Name",
    pg_size_pretty(pg_database_size(datname)) as "Size"
FROM pg_database 
WHERE datistemplate = false
ORDER BY datname;
```

### Xem tables trong database nguyenhang.3010:
```sql
SELECT 
    table_schema,
    table_name
FROM information_schema.tables 
WHERE table_catalog = 'nguyenhang.3010'
    AND table_schema = 'public'
ORDER BY table_name;
```

### Hoặc dùng lệnh psql trong PSQL tab:
```
\c nguyenhang.3010
\dt
```

## 📊 Các tables quan trọng trong Odoo database

Sau khi kết nối vào `nguyenhang.3010`, bạn sẽ thấy hàng trăm tables, ví dụ:

### Users & Companies
- `res_users` - Người dùng hệ thống
- `res_partner` - Đối tác/Khách hàng/Nhà cung cấp
- `res_company` - Công ty
- `res_groups` - Nhóm người dùng

### Accounting
- `account_move` - Phiếu kế toán
- `account_move_line` - Dòng kế toán
- `account_account` - Tài khoản kế toán
- `account_journal` - Sổ nhật ký
- `account_payment` - Thanh toán

### Products
- `product_product` - Sản phẩm
- `product_template` - Mẫu sản phẩm
- `product_category` - Danh mục sản phẩm

### Sales
- `sale_order` - Đơn bán hàng
- `sale_order_line` - Dòng đơn bán hàng

### Inventory
- `stock_picking` - Phiếu xuất/nhập kho
- `stock_move` - Di chuyển kho
- `stock_quant` - Tồn kho

## 🔄 Refresh Object Explorer

Nếu không thấy databases/tables mới:
1. Click chuột phải vào kết nối
2. Chọn "Refresh" hoặc "Reload"
3. Hoặc click icon refresh (🔄) ở trên Object Explorer

## 💡 Tips

1. **Double-click vào table** để xem dữ liệu
2. **Click chuột phải vào table** để:
   - View Data
   - Show Definition
   - Generate SQL
3. **Search trong Object Explorer**: Dùng `Cmd + F` để tìm table
4. **Filter**: Có thể filter để chỉ hiển thị tables, views, functions, etc.

## ⚠️ Lưu ý

- Database `postgres` chỉ chứa dữ liệu hệ thống
- Database `nguyenhang.3010` mới chứa dữ liệu Odoo thực tế
- Để xem tables Odoo, bạn PHẢI kết nối vào `nguyenhang.3010`


