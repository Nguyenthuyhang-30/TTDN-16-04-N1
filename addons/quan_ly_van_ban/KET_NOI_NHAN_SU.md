# Kết nối giữa Module Nhân sự và Module Quản lý Văn bản

## 1. Dependency (Phụ thuộc)

Module `quan_ly_van_ban` phụ thuộc vào module `om_hr_custom` trong file `__manifest__.py`:

```python
'depends': [
    'base',
    'mail',
    'om_hr_custom',  # ← Module nhân sự
    'quan_ly_khach_hang',
],
```

## 2. Các Field Many2one kết nối với Nhân viên

### 2.1. Văn bản đi (Document Outgoing)
- **Field**: `assigned_employee_id`
- **Model**: `om.hr.employee`
- **Mục đích**: Nhân viên được gán để soạn thảo/xử lý văn bản đi
- **Vị trí**: `models/van_ban_di.py`

```python
assigned_employee_id = fields.Many2one(
    'om.hr.employee',
    string='Nhân viên được gán',
    tracking=True,
    help='Nhân viên được gán xử lý văn bản này'
)
```

### 2.2. Văn bản đến (Document Incoming)
- **Field**: `assigned_employee_id`
- **Model**: `om.hr.employee`
- **Mục đích**: Nhân viên được gán để xử lý văn bản đến
- **Vị trí**: `models/van_ban_den.py`

```python
assigned_employee_id = fields.Many2one(
    'om.hr.employee',
    string='Nhân viên được gán',
    tracking=True,
    help='Nhân viên được gán xử lý văn bản này'
)
```

### 2.3. Chữ ký số (Document Signature)
- **Field**: `signer_id`
- **Model**: `om.hr.employee`
- **Mục đích**: Nhân viên ký văn bản
- **Vị trí**: `models/chu_ky_so.py`

```python
signer_id = fields.Many2one(
    'om.hr.employee',
    string='Người ký',
    required=True,
    help='Nhân viên ký văn bản'
)
```

### 2.4. Quy trình duyệt (Document Approval)
- **Field**: `approver_id`
- **Model**: `om.hr.employee`
- **Mục đích**: Nhân viên duyệt văn bản
- **Vị trí**: `models/quy_trinh_duyet.py`

```python
approver_id = fields.Many2one(
    'om.hr.employee',
    string='Người duyệt',
    required=True,
    help='Nhân viên duyệt văn bản'
)
```

### 2.5. Chứng thư số (Digital Certificate)
- **Field**: `employee_id`
- **Model**: `om.hr.employee`
- **Mục đích**: Nhân viên sở hữu chứng thư số
- **Vị trí**: `models/chung_thu_so.py`

```python
employee_id = fields.Many2one(
    'om.hr.employee',
    string='Nhân viên',
    required=True,
    help='Nhân viên sở hữu chứng thư số'
)
```

### 2.6. Lịch sử văn bản (Document History)
- **Field**: `employee_id`
- **Model**: `om.hr.employee`
- **Mục đích**: Nhân viên thực hiện hành động (tự động tìm theo email)
- **Vị trí**: `models/lich_su_van_ban.py`

```python
employee_id = fields.Many2one(
    'om.hr.employee',
    string='Nhân viên',
    help='Nhân viên thực hiện hành động'
)
```

## 3. Logic tự động kết nối

### 3.1. Tự động gán nhân viên cho văn bản ưu tiên cao
**File**: `models/van_ban_den.py`

Khi tạo văn bản đến với độ ưu tiên cao hoặc khẩn cấp, hệ thống tự động gán nhân viên đầu tiên:

```python
@api.model
def create(self, vals):
    record = super(DocumentIncoming, self).create(vals)
    
    # Tự động gán nhân viên nếu văn bản có độ ưu tiên cao/khẩn cấp
    if not record.assigned_employee_id and record.priority in ['high', 'urgent']:
        # Tìm nhân viên đang hoạt động
        employees = self.env['om.hr.employee'].search([('active', '=', True)])
        if employees:
            record.assigned_employee_id = employees[0]
    
    return record
```

### 3.2. Kiểm tra quyền nhân viên khi soạn thảo/duyệt
**File**: `models/van_ban_di.py`

Hệ thống kiểm tra quyền của nhân viên trước khi cho phép soạn thảo hoặc gửi duyệt:

```python
def action_submit_approval(self):
    for record in self:
        # Kiểm tra quyền nhân viên
        if self.assigned_employee_id:
            if not self.assigned_employee_id.check_permission('draft'):
                raise UserError(
                    f'Nhân viên {self.assigned_employee_id.name} không có quyền soạn thảo văn bản!\n'
                    f'Vui lòng kiểm tra quyền trong thông tin nhân viên.'
                )
            
            # Kiểm tra trạng thái nhân viên
            if self.assigned_employee_id.employee_status != 'working':
                raise UserError(
                    f'Nhân viên {self.assigned_employee_id.name} không đang làm việc, không thể gửi duyệt!'
                )
```

### 3.3. Tự động tìm nhân viên theo email để ghi lịch sử
**File**: `models/lich_su_van_ban.py`

Khi ghi lịch sử văn bản, hệ thống tự động tìm nhân viên theo email của user hiện tại:

```python
@api.model
def create_history(self, ...):
    employee_id = None
    # Tìm employee theo email (vì model om.hr.employee không có field user_id)
    try:
        if self.env.user.email:
            employee = self.env['om.hr.employee'].search(
                [('email', '=', self.env.user.email)], 
                limit=1
            )
            if employee:
                employee_id = employee.id
    except Exception:
        pass
    
    return self.sudo().create({
        ...
        'employee_id': employee_id,
    })
```

### 3.4. Gửi thông báo đến Manager của nhân viên
**File**: `models/document_reminder.py`

Khi gửi nhắc hạn văn bản, hệ thống có thể gửi thông báo đến manager của nhân viên được gán:

```python
if self.recipient_manager and self.document_id.assigned_employee_id:
    manager = self.document_id.assigned_employee_id
    # Logic gửi thông báo đến manager
```

## 4. Các View hiển thị kết nối

### 4.1. Form Văn bản đi
- Hiển thị field `assigned_employee_id` để chọn nhân viên
- Hiển thị danh sách quy trình duyệt với `approver_id`
- Hiển thị danh sách chữ ký số với `signer_id`

### 4.2. Form Văn bản đến
- Hiển thị field `assigned_employee_id` để chọn nhân viên

### 4.3. Form Quy trình duyệt
- Hiển thị field `approver_id` để chọn người duyệt
- Domain filter: chỉ hiển thị nhân viên đang hoạt động và có trạng thái "working"

### 4.4. Form Chữ ký số
- Hiển thị field `signer_id` để chọn người ký
- Domain filter: chỉ hiển thị nhân viên đang hoạt động và có trạng thái "working"

### 4.5. Form Chứng thư số
- Hiển thị field `employee_id` để chọn nhân viên sở hữu

## 5. Quyền và Phân quyền

Module văn bản sử dụng các quyền từ module nhân sự:

- **can_draft**: Quyền soạn thảo văn bản
- **can_approve**: Quyền duyệt văn bản
- **can_final_approve**: Quyền phê duyệt cuối cùng

Các quyền này được kiểm tra trong các method:
- `action_submit_approval()`: Kiểm tra quyền soạn thảo
- `action_approved()`: Kiểm tra quyền duyệt

## 6. Tóm tắt

Module **quan_ly_van_ban** kết nối với module **om_hr_custom** thông qua:

1. **Dependency**: Phụ thuộc trực tiếp trong `__manifest__.py`
2. **6 Field Many2one**: Kết nối các model văn bản với model nhân viên
3. **Logic tự động**: 
   - Tự động gán nhân viên
   - Kiểm tra quyền
   - Tìm nhân viên theo email
   - Gửi thông báo đến manager
4. **Phân quyền**: Sử dụng hệ thống quyền từ module nhân sự

Tất cả các kết nối này đảm bảo module văn bản có thể quản lý và theo dõi văn bản theo nhân viên một cách hiệu quả.

