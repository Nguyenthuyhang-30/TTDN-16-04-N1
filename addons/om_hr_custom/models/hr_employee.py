# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _name = 'om.hr.employee'
    _description = 'Nhân viên'
    _order = 'name'
    
    _sql_constraints = [
        ('employee_code_unique', 'UNIQUE(employee_code)', 'Mã nhân viên đã tồn tại! Vui lòng nhập mã khác.')
    ]

    name = fields.Char(
        string='Tên nhân viên',
        required=True,
        help='Họ và tên nhân viên'
    )
    
    employee_code = fields.Char(
        string='Mã nhân viên',
        required=True,
        default=lambda self: self._generate_employee_code(),
        help='Mã số nhân viên duy nhất'
    )
    
    email = fields.Char(
        string='Email',
        help='Email của nhân viên'
    )
    
    phone = fields.Char(
        string='Số điện thoại',
        help='Số điện thoại liên hệ'
    )
    
    department_id = fields.Many2one(
        'om.hr.department',
        string='Phòng ban',
        help='Phòng ban của nhân viên'
    )
    
    # Quan hệ với hợp đồng làm việc
    contract_ids = fields.One2many(
        'om.hr.contract',
        'employee_id',
        string='Hợp đồng làm việc',
        help='Danh sách hợp đồng làm việc của nhân viên'
    )
    
    active_contract_id = fields.Many2one(
        'om.hr.contract',
        string='Hợp đồng hiện tại',
        compute='_compute_active_contract',
        store=True,
        help='Hợp đồng đang có hiệu lực'
    )
    
    # MỨC 1: Quan hệ ngược với các module khác
    # Lưu ý: One2many fields sẽ tự động được tạo từ Many2one fields trong các module khác
    # Không cần định nghĩa ở đây để tránh lỗi khi module chưa được load
    # Các quan hệ sẽ hoạt động tự động khi:
    # - om.document.incoming có field assigned_employee_id
    # - om.document.outgoing có field assigned_employee_id  
    # - qlkh.order có field salesperson_id
    # - qlkh.customer.support có field assigned_employee_id
    
    job_title = fields.Char(
        string='Chức vụ',
        help='Chức vụ của nhân viên'
    )
    
    join_date = fields.Date(
        string='Ngày vào làm',
        default=fields.Date.today,
        help='Ngày nhân viên bắt đầu làm việc'
    )
    
    contract_type = fields.Selection([
        ('fulltime', 'Toàn thời gian'),
        ('parttime', 'Bán thời gian'),
        ('contract', 'Hợp đồng'),
        ('intern', 'Thực tập sinh'),
    ], string='Loại hợp đồng', default='fulltime')
    
    salary = fields.Monetary(
        string='Lương cơ bản',
        currency_field='currency_id',
        help='Mức lương cơ bản của nhân viên'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    active = fields.Boolean(
        string='Hoạt động',
        default=True,
        help='Nếu bỏ chọn, nhân viên này sẽ bị ẩn'
    )
    
    # Trạng thái nhân viên
    employee_status = fields.Selection([
        ('working', 'Đang làm việc'),
        ('resigned', 'Nghỉ việc'),
        ('suspended', 'Tạm nghỉ'),
    ], string='Trạng thái nhân viên',
        default='working',
        required=True,
        tracking=True,
        help='Trạng thái làm việc của nhân viên'
    )
    
    # Vai trò nhân sự
    role = fields.Selection([
        ('employee', 'Nhân viên'),
        ('manager', 'Trưởng phòng'),
        ('director', 'Giám đốc'),
    ], string='Vai trò',
        default='employee',
        required=True,
        tracking=True,
        help='Vai trò của nhân viên trong tổ chức'
    )
    
    # Phân quyền
    can_draft = fields.Boolean(
        string='Quyền soạn thảo',
        default=True,
        tracking=True,
        help='Nhân viên có quyền soạn thảo văn bản'
    )
    
    can_approve = fields.Boolean(
        string='Quyền duyệt',
        default=False,
        tracking=True,
        help='Nhân viên có quyền duyệt văn bản'
    )
    
    can_final_approve = fields.Boolean(
        string='Quyền phê duyệt',
        default=False,
        tracking=True,
        help='Nhân viên có quyền phê duyệt cuối cùng (Giám đốc)'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về nhân viên'
    )

    @api.model
    def _generate_employee_code(self):
        """Tự động tạo mã nhân viên"""
        sequence = self.env['ir.sequence'].next_by_code('hr.employee.code') or 'NV0001'
        return sequence

    @api.constrains('employee_code')
    def _check_employee_code_unique(self):
        """Kiểm tra mã nhân viên không được trùng"""
        for record in self:
            if record.employee_code:
                # Tìm các nhân viên khác có cùng mã (trừ chính bản thân record này)
                duplicate = self.search([
                    ('employee_code', '=', record.employee_code),
                    ('id', '!=', record.id)
                ])
                if duplicate:
                    raise ValidationError(
                        f'Mã nhân viên "{record.employee_code}" đã tồn tại!\n'
                        f'Nhân viên: {duplicate[0].name}\n'
                        f'Vui lòng nhập mã khác.'
                    )

    @api.model
    def create(self, vals):
        """Override create để tự động tạo mã nhân viên nếu chưa có và kiểm tra trùng"""
        if not vals.get('employee_code'):
            # Tạo mã mới và đảm bảo không trùng
            max_attempts = 100
            for attempt in range(max_attempts):
                new_code = self._generate_employee_code()
                existing = self.search([('employee_code', '=', new_code)], limit=1)
                if not existing:
                    vals['employee_code'] = new_code
                    break
            else:
                # Nếu sau 100 lần vẫn trùng, tạo mã thủ công
                raise ValidationError(
                    'Không thể tạo mã nhân viên tự động. Vui lòng nhập mã thủ công.'
                )
        else:
            # Kiểm tra mã nhập thủ công có trùng không
            existing = self.search([('employee_code', '=', vals['employee_code'])], limit=1)
            if existing:
                raise ValidationError(
                    f'Mã nhân viên "{vals["employee_code"]}" đã tồn tại!\n'
                    f'Nhân viên: {existing.name}\n'
                    f'Vui lòng nhập mã khác.'
                )
        
        return super(HrEmployee, self).create(vals)
    
    def write(self, vals):
        """MỨC 2: Tự động cập nhật khi nhân viên thay đổi phòng ban hoặc vai trò"""
        result = super(HrEmployee, self).write(vals)
        
        # Nếu phòng ban thay đổi, có thể cập nhật các bản ghi liên quan
        if 'department_id' in vals:
            # Có thể thêm logic tự động gán lại văn bản, đơn hàng... nếu cần
            pass
        
        # Tự động cập nhật quyền dựa trên vai trò
        if 'role' in vals:
            for record in self:
                role = vals.get('role', record.role)
                # Tự động set quyền dựa trên vai trò
                if role == 'director':
                    # Giám đốc có tất cả quyền
                    record.can_draft = True
                    record.can_approve = True
                    record.can_final_approve = True
                elif role == 'manager':
                    # Trưởng phòng có quyền soạn thảo và duyệt
                    record.can_draft = True
                    record.can_approve = True
                    record.can_final_approve = False
                elif role == 'employee':
                    # Nhân viên chỉ có quyền soạn thảo
                    record.can_draft = True
                    record.can_approve = False
                    record.can_final_approve = False
        
        return result
    
    def check_permission(self, permission_type):
        """
        Kiểm tra quyền của nhân viên
        
        :param permission_type: 'draft', 'approve', 'final_approve'
        :return: True nếu có quyền, False nếu không
        """
        self.ensure_one()
        
        # Kiểm tra trạng thái nhân viên
        if self.employee_status != 'working':
            return False
        
        # Kiểm tra quyền cụ thể
        if permission_type == 'draft':
            return self.can_draft
        elif permission_type == 'approve':
            return self.can_approve
        elif permission_type == 'final_approve':
            return self.can_final_approve
        
        return False
    
    def has_role(self, role_name):
        """
        Kiểm tra nhân viên có vai trò cụ thể không
        
        :param role_name: 'employee', 'manager', 'director'
        :return: True nếu có vai trò, False nếu không
        """
        self.ensure_one()
        return self.role == role_name
    
    @api.model
    def get_employee_by_email(self, email):
        """Tìm nhân viên theo email"""
        if not email:
            return self.browse()
        return self.search([('email', '=', email)], limit=1)
    
    @api.depends('contract_ids', 'contract_ids.state', 'contract_ids.start_date', 'contract_ids.end_date')
    def _compute_active_contract(self):
        """Tính toán hợp đồng đang hiệu lực"""
        today = fields.Date.today()
        for record in self:
            active_contract = self.env['om.hr.contract'].search([
                ('employee_id', '=', record.id),
                ('state', '=', 'active'),
                ('start_date', '<=', today),
                '|',
                ('end_date', '=', False),
                ('end_date', '>=', today),
            ], limit=1, order='start_date desc')
            record.active_contract_id = active_contract


class HrDepartment(models.Model):
    _name = 'om.hr.department'
    _description = 'Phòng ban'
    _order = 'name'

    name = fields.Char(
        string='Tên phòng ban',
        required=True,
        help='Tên phòng ban'
    )
    
    code = fields.Char(
        string='Mã phòng ban',
        help='Mã phòng ban'
    )
    
    manager_id = fields.Many2one(
        'om.hr.employee',
        string='Trưởng phòng',
        help='Trưởng phòng của phòng ban này'
    )
    
    employee_ids = fields.One2many(
        'om.hr.employee',
        'department_id',
        string='Nhân viên',
        help='Danh sách nhân viên trong phòng ban'
    )
    
    active = fields.Boolean(
        string='Hoạt động',
        default=True
    )
