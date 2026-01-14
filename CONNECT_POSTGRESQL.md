# Hướng dẫn kết nối PostgreSQL Container

## ⚠️ QUAN TRỌNG: Port phải là 5434, không phải 5432!

Container PostgreSQL của Odoo đang chạy trên **port 5434** (không phải 5432 mặc định).

## Thông tin kết nối

```
Host:     127.0.0.1 (hoặc localhost)
Port:     5434  ← QUAN TRỌNG!
User:     odoo
Password: odoo
Database: postgres (hoặc tên database cụ thể như nguyenhang.3010)
```

## Cách kết nối từ các ứng dụng

### 1. pgAdmin
1. Mở pgAdmin
2. Click chuột phải vào "Servers" → "Register" → "Server"
3. Tab **General**:
   - Name: `Odoo PostgreSQL`
4. Tab **Connection**:
   - Host name/address: `127.0.0.1`
   - Port: `5434` ⚠️
   - Maintenance database: `postgres`
   - Username: `odoo`
   - Password: `odoo`
5. Click "Save"

### 2. DBeaver
1. File → New → Database Connection
2. Chọn **PostgreSQL**
3. Điền thông tin:
   - Host: `127.0.0.1`
   - Port: `5434` ⚠️
   - Database: `postgres`
   - Username: `odoo`
   - Password: `odoo`
4. Click "Test Connection" → "Finish"

### 3. TablePlus / Postico
1. New Connection → PostgreSQL
2. Điền:
   - Host: `127.0.0.1`
   - Port: `5434` ⚠️
   - User: `odoo`
   - Password: `odoo`
   - Database: `postgres`

### 4. VS Code Extension (PostgreSQL Client)
1. Mở Database Explorer
2. Click "+" để thêm connection
3. Chọn PostgreSQL
4. Điền:
   - Host: `127.0.0.1`
   - Port: `5434` ⚠️
   - User: `odoo`
   - Password: `odoo`
   - Database: `postgres`

## Kiểm tra databases bằng lệnh

Chạy script:
```bash
./check_databases.sh
```

Hoặc chạy trực tiếp:
```bash
docker exec postgres_odoo psql -U odoo -d postgres -c "\l"
```

## Xem databases hiện có

Sau khi kết nối thành công, bạn sẽ thấy:
- `postgres` - Database mặc định
- `nguyenhang.3010` - Database Odoo của bạn
- Các database khác (nếu có)

## Lưu ý

- Nếu app PostgreSQL của bạn đang kết nối port 5432, đó là PostgreSQL local trên máy (không phải container)
- Container Odoo PostgreSQL chạy trên port **5434**
- Đảm bảo container đang chạy: `docker-compose ps`
- Nếu container không chạy: `docker-compose up -d`

