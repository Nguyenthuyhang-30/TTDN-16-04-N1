# HƯỚNG DẪN CÀI ĐẶT MODULE MAIL

## Vấn đề
Lỗi: `KeyError: 'mail.template'` xảy ra vì module `mail` chưa được cài đặt trong database.

## Giải pháp

### Cách 1: Cài đặt module Mail qua giao diện
1. Vào **Apps** (Ứng dụng)
2. Bỏ filter "Apps" (nếu có)
3. Tìm kiếm "Mail" hoặc "Discuss"
4. Click **Install** để cài đặt module Mail
5. Sau đó upgrade lại module "Quản lý văn bản"

### Cách 2: Cài đặt qua command line
```bash
# Vào container Odoo
docker exec -it odoo_17 bash

# Cài đặt module mail
odoo-bin -c /etc/odoo/odoo.conf -d <database_name> -u mail --stop-after-init

# Hoặc upgrade module quan_ly_van_ban
odoo-bin -c /etc/odoo/odoo.conf -d <database_name> -u quan_ly_van_ban --stop-after-init
```

### Cách 3: Tạm thời bỏ qua email templates
Nếu không cần email templates ngay, có thể comment file email_template_data.xml trong __manifest__.py:

```python
'data': [
    'data/ir_sequence_data.xml',
    'security/ir.model.access.csv',
    'security/ir.model.access.digital_signature.xml',
    'data/ir_cron_data.xml',
    # 'data/email_template_data.xml',  # Tạm thời comment
    ...
],
```

Sau khi cài đặt module Mail, uncomment lại dòng này.

## Lưu ý
- Module `mail` là module cơ bản của Odoo, thường được cài đặt mặc định
- Nếu database mới tạo, có thể module Mail chưa được cài
- Sau khi cài Mail, các tính năng email sẽ hoạt động bình thường

