# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class HrContract(models.Model):
    _name = 'om.hr.contract'
    _description = 'Hợp đồng làm việc'
    _order = 'start_date desc, employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Số hợp đồng',
        required=True,
        default=lambda self: self._generate_contract_number(),
        tracking=True,
        help='Số hợp đồng làm việc'
    )
    
    employee_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên',
        required=True,
        tracking=True,
        ondelete='cascade',
        help='Nhân viên ký hợp đồng'
    )
    
    contract_type = fields.Selection([
        ('fulltime', 'Toàn thời gian'),
        ('parttime', 'Bán thời gian'),
        ('contract', 'Hợp đồng'),
        ('intern', 'Thực tập sinh'),
    ], string='Loại hợp đồng',
        required=True,
        default='fulltime',
        tracking=True,
        help='Loại hợp đồng làm việc'
    )
    
    start_date = fields.Date(
        string='Ngày bắt đầu',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Ngày hợp đồng có hiệu lực'
    )
    
    end_date = fields.Date(
        string='Ngày kết thúc',
        tracking=True,
        help='Ngày hợp đồng hết hiệu lực (để trống nếu không xác định)'
    )
    
    salary = fields.Monetary(
        string='Mức lương',
        currency_field='currency_id',
        required=True,
        tracking=True,
        help='Mức lương theo hợp đồng'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    job_title = fields.Char(
        string='Chức vụ',
        tracking=True,
        help='Chức vụ của nhân viên theo hợp đồng'
    )
    
    department_id = fields.Many2one(
        'om.hr.department',
        string='Phòng ban',
        tracking=True,
        help='Phòng ban của nhân viên theo hợp đồng'
    )
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('active', 'Đang hiệu lực'),
        ('expired', 'Hết hạn'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái',
        default='draft',
        required=True,
        tracking=True,
        help='Trạng thái hợp đồng'
    )
    
    is_active = fields.Boolean(
        string='Đang hiệu lực',
        compute='_compute_is_active',
        store=True,
        help='Hợp đồng đang có hiệu lực'
    )
    
    days_remaining = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_days_remaining',
        help='Số ngày còn lại trước khi hết hạn'
    )
    
    contract_file = fields.Binary(
        string='File hợp đồng',
        help='File hợp đồng đã ký (PDF, Word, ...)'
    )
    
    contract_filename = fields.Char(
        string='Tên file',
        help='Tên file hợp đồng'
    )
    
    signed_date = fields.Date(
        string='Ngày ký',
        tracking=True,
        help='Ngày ký hợp đồng'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về hợp đồng'
    )
    
    # Liên kết với văn bản (nếu module quan_ly_van_ban được cài đặt)
    document_ids = fields.One2many(
        'om.document.outgoing',
        'contract_id',
        string='Văn bản liên quan',
        help='Danh sách văn bản liên quan đến hợp đồng này (ký, duyệt)'
    )
    
    document_count = fields.Integer(
        string='Số văn bản',
        compute='_compute_document_count',
        help='Tổng số văn bản liên quan đến hợp đồng'
    )
    
    active = fields.Boolean(
        string='Hoạt động',
        default=True,
        help='Nếu bỏ chọn, hợp đồng này sẽ bị ẩn'
    )

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Tự động điền thông tin khi chọn nhân viên"""
        result = {}
        if self.employee_id:
            # Tự động điền loại hợp đồng từ nhân viên (nếu có)
            if self.employee_id.contract_type:
                self.contract_type = self.employee_id.contract_type
            
            # Tự động điền chức vụ
            self.job_title = self.employee_id.job_title or ''
            
            # Tự động điền phòng ban
            self.department_id = self.employee_id.department_id
            
            # Tự động điền mức lương (nếu có, nếu không thì giữ nguyên giá trị hiện tại)
            if self.employee_id.salary:
                self.salary = self.employee_id.salary
            
            # Tự động điền ngày bắt đầu từ ngày vào làm (nếu chưa có)
            if not self.start_date and self.employee_id.join_date:
                self.start_date = self.employee_id.join_date
        else:
            # Nếu bỏ chọn nhân viên, xóa các thông tin liên quan
            self.job_title = False
            self.department_id = False
        
        return result

    @api.model
    def _generate_contract_number(self):
        """Tự động tạo số hợp đồng"""
        sequence = self.env['ir.sequence'].next_by_code('hr.contract.number') or 'HD0001'
        return sequence

    @api.model
    def _update_contract_states(self):
        """Cập nhật trạng thái hợp đồng dựa trên ngày (gọi từ cron)"""
        today = fields.Date.today()
        contracts = self.search([
            ('state', 'in', ['draft', 'active']),
            ('active', '=', True)
        ])
        for contract in contracts:
            if contract.end_date and contract.end_date < today:
                contract.state = 'expired'
            elif contract.start_date and contract.start_date <= today:
                if not contract.end_date or contract.end_date >= today:
                    if contract.state == 'draft':
                        contract.state = 'active'
    
    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        """Tính toán hợp đồng có đang hiệu lực không"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'cancelled':
                record.is_active = False
            elif record.state == 'active':
                if record.start_date and record.start_date <= today:
                    if not record.end_date or record.end_date >= today:
                        record.is_active = True
                    else:
                        record.is_active = False
                else:
                    record.is_active = False
            else:
                record.is_active = False

    @api.depends('end_date')
    def _compute_days_remaining(self):
        """Tính số ngày còn lại trước khi hết hạn"""
        today = fields.Date.today()
        for record in self:
            if record.end_date and record.end_date > today:
                record.days_remaining = (record.end_date - today).days
            else:
                record.days_remaining = 0
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        """Tính số văn bản liên quan đến hợp đồng"""
        for record in self:
            try:
                # Kiểm tra xem model om.document.outgoing có tồn tại không
                if 'om.document.outgoing' in self.env:
                    record.document_count = len(record.document_ids)
                else:
                    record.document_count = 0
            except Exception:
                record.document_count = 0

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Kiểm tra ngày bắt đầu và kết thúc"""
        for record in self:
            if record.end_date and record.start_date:
                if record.end_date < record.start_date:
                    raise ValidationError(
                        'Ngày kết thúc không thể nhỏ hơn ngày bắt đầu!'
                    )

    @api.model
    def create(self, vals):
        """Override create để tự động cập nhật thông tin nhân viên"""
        record = super(HrContract, self).create(vals)
        
        # Tự động cập nhật thông tin nhân viên nếu hợp đồng đang hiệu lực
        if record.state == 'active' and record.employee_id:
            employee = record.employee_id
            # Cập nhật loại hợp đồng
            employee.contract_type = record.contract_type
            # Cập nhật mức lương
            employee.salary = record.salary
            # Cập nhật chức vụ nếu có
            if record.job_title:
                employee.job_title = record.job_title
            # Cập nhật phòng ban nếu có
            if record.department_id:
                employee.department_id = record.department_id
            # Cập nhật ngày vào làm nếu chưa có
            if not employee.join_date:
                employee.join_date = record.start_date
        
        return record

    def write(self, vals):
        """Override write để tự động cập nhật thông tin nhân viên"""
        result = super(HrContract, self).write(vals)
        
        # Nếu hợp đồng chuyển sang trạng thái active, cập nhật thông tin nhân viên
        if 'state' in vals and vals['state'] == 'active':
            for record in self:
                if record.employee_id:
                    employee = record.employee_id
                    employee.contract_type = record.contract_type
                    employee.salary = record.salary
                    if record.job_title:
                        employee.job_title = record.job_title
                    if record.department_id:
                        employee.department_id = record.department_id
        
        return result

    def action_activate(self):
        """Kích hoạt hợp đồng"""
        for record in self:
            if record.state != 'draft':
                raise UserError('Chỉ có thể kích hoạt hợp đồng ở trạng thái Nháp!')
            record.state = 'active'
            # Tự động cập nhật thông tin nhân viên
            if record.employee_id:
                employee = record.employee_id
                employee.contract_type = record.contract_type
                employee.salary = record.salary
                if record.job_title:
                    employee.job_title = record.job_title
                if record.department_id:
                    employee.department_id = record.department_id

    def action_cancel(self):
        """Hủy hợp đồng"""
        for record in self:
            record.state = 'cancelled'

    def action_renew(self):
        """Gia hạn hợp đồng"""
        for record in self:
            if not record.end_date:
                raise UserError('Hợp đồng không có ngày kết thúc, không thể gia hạn!')
            # Tạo hợp đồng mới dựa trên hợp đồng hiện tại
            new_contract = self.env['om.hr.contract'].create({
                'employee_id': record.employee_id.id,
                'contract_type': record.contract_type,
                'start_date': record.end_date + timedelta(days=1),
                'salary': record.salary,
                'job_title': record.job_title,
                'department_id': record.department_id.id,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Hợp đồng mới',
                'res_model': 'om.hr.contract',
                'res_id': new_contract.id,
                'view_mode': 'form',
                'target': 'current',
            }
    
    def action_create_document(self):
        """Tạo văn bản mới liên kết với hợp đồng này"""
        for record in self:
            # Kiểm tra xem module quan_ly_van_ban có được cài đặt không
            try:
                document_model = self.env['om.document.outgoing']
                document_type_model = self.env['om.document.type']
            except KeyError:
                raise UserError('Module Quản lý Văn bản chưa được cài đặt!')
            
            # Tìm hoặc tạo loại văn bản "Hợp đồng"
            document_type = document_type_model.search([('name', '=', 'Hợp đồng')], limit=1)
            if not document_type:
                # Tạo loại văn bản "Hợp đồng" nếu chưa có
                document_type = document_type_model.create({
                    'name': 'Hợp đồng',
                    'code': 'HOP_DONG',
                    'description': 'Hợp đồng làm việc',
                })
            
            # Tạo văn bản mới
            document = document_model.create({
                'name': f'Hợp đồng {record.name}',
                'subject': f'Hợp đồng làm việc số {record.name} - {record.employee_id.name if record.employee_id else ""}',
                'document_type_id': document_type.id,
                'contract_id': record.id,
                'assigned_employee_id': record.employee_id.id if record.employee_id else False,
                'date_sent': fields.Date.today(),
                'date_document': record.start_date if record.start_date else fields.Date.today(),
                'recipient': record.employee_id.name if record.employee_id else '',
                'status': 'draft',
            })
            
            return {
                'type': 'ir.actions.act_window',
                'name': 'Văn bản mới',
                'res_model': 'om.document.outgoing',
                'res_id': document.id,
                'view_mode': 'form',
                'target': 'current',
            }

