# Hướng dẫn sử dụng PostgreSQL với Odoo

## 🔌 Kết nối nhanh

### Cách 1: Dùng script
```bash
./connect_db.sh
```

### Cách 2: Lệnh trực tiếp
```bash
psql -h localhost -p 5434 -U odoo -d postgres
```
Password: `odoo`

### Cách 3: Tạo alias (thêm vào ~/.zshrc hoặc ~/.bashrc)
```bash
alias odoo-db='psql -h localhost -p 5434 -U odoo -d postgres'
```
Sau đó chỉ cần gõ: `odoo-db`

## 📋 Các lệnh psql cơ bản

### Quản lý Databases
```sql
\l          -- Xem danh sách databases
\l+         -- Xem chi tiết databases
\c dbname   -- Kết nối vào database
\conninfo   -- Xem thông tin kết nối hiện tại
```

### Quản lý Tables
```sql
\dt         -- Xem danh sách tables
\dt+        -- Xem chi tiết tables
\d table    -- Xem cấu trúc table
\d+ table   -- Xem chi tiết cấu trúc table
```

### Quản lý Schemas
```sql
\dn         -- Xem danh sách schemas
\dn+        -- Xem chi tiết schemas
```

### Quản lý Functions
```sql
\df         -- Xem danh sách functions
\df+        -- Xem chi tiết functions
```

### SQL Queries
```sql
SELECT * FROM table_name LIMIT 10;
SELECT COUNT(*) FROM table_name;
```

### Hỗ trợ
```sql
\?          -- Xem tất cả lệnh psql
\h          -- Xem help cho SQL commands
\h SELECT   -- Xem help cho lệnh SELECT
\q          -- Thoát khỏi psql
```

## 🎯 Workflow thường dùng

### 1. Xem tất cả databases
```sql
postgres=# \l
```

### 2. Kết nối vào database Odoo
```sql
postgres=# \c nguyenhang.3010
```

### 3. Xem danh sách tables
```sql
nguyenhang.3010=# \dt
```

### 4. Xem cấu trúc table quan trọng
```sql
nguyenhang.3010=# \d res_users
nguyenhang.3010=# \d account_move
nguyenhang.3010=# \d product_product
```

### 5. Query dữ liệu
```sql
nguyenhang.3010=# SELECT id, name FROM res_users LIMIT 5;
nguyenhang.3010=# SELECT COUNT(*) FROM account_move;
```

## 📊 Các tables quan trọng trong Odoo

### Users & Companies
- `res_users` - Người dùng
- `res_partner` - Đối tác/Khách hàng
- `res_company` - Công ty

### Accounting
- `account_move` - Phiếu kế toán
- `account_move_line` - Dòng kế toán
- `account_account` - Tài khoản
- `account_journal` - Sổ nhật ký

### Products
- `product_product` - Sản phẩm
- `product_template` - Mẫu sản phẩm

### Sales
- `sale_order` - Đơn bán hàng
- `sale_order_line` - Dòng đơn bán hàng

## 🔍 Các query hữu ích

### Đếm số lượng records trong các tables chính
```sql
SELECT 
    'res_users' as table_name, 
    COUNT(*) as count 
FROM res_users
UNION ALL
SELECT 'res_partner', COUNT(*) FROM res_partner
UNION ALL
SELECT 'account_move', COUNT(*) FROM account_move
UNION ALL
SELECT 'product_product', COUNT(*) FROM product_product;
```

### Xem users và email
```sql
SELECT id, login, name, email FROM res_users WHERE active = true;
```

### Xem đối tác
```sql
SELECT id, name, email, phone FROM res_partner LIMIT 10;
```

## ⚠️ Lưu ý

1. **Không xóa dữ liệu trực tiếp** từ database mà không backup
2. **Luôn test queries** trên môi trường dev trước
3. **Sử dụng transactions** khi cần:
   ```sql
   BEGIN;
   -- Your queries here
   COMMIT;  -- hoặc ROLLBACK; nếu muốn hủy
   ```
4. **Backup trước khi thay đổi lớn**:
   ```bash
   docker exec postgres_odoo pg_dump -U odoo nguyenhang.3010 > backup.sql
   ```

## 🛠️ Scripts tiện ích

### Xem databases
```bash
./check_databases.sh
```

### Xem tables trong database
```bash
python3 view_tables.py nguyenhang.3010
```

### Kết nối nhanh
```bash
./connect_db.sh
```

## 📝 Tips

- Dùng `\x` để hiển thị kết quả dạng cột (toggle)
- Dùng `\timing` để hiển thị thời gian thực thi query
- Dùng `\copy` để export/import CSV
- Dùng `\e` để mở editor để viết query dài

