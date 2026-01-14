# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class DocumentOutgoing(models.Model):
    _name = 'om.document.outgoing'
    _description = 'Văn bản đi'
    _order = 'date_sent desc, number'

    name = fields.Char(
        string='Số văn bản',
        required=True,
        help='Số hiệu văn bản đi'
    )
    
    number = fields.Char(
        string='Số đi',
        required=True,
        default=lambda self: self._generate_number(),
        help='Số đi của văn bản'
    )
    
    document_type_id = fields.Many2one(
        'om.document.type',
        string='Loại văn bản',
        required=True,
        help='Loại văn bản'
    )
    
    date_sent = fields.Date(
        string='Ngày gửi',
        required=True,
        default=fields.Date.today,
        help='Ngày gửi văn bản'
    )
    
    date_document = fields.Date(
        string='Ngày văn bản',
        help='Ngày trên văn bản'
    )
    
    sender = fields.Char(
        string='Nơi gửi',
        help='Cơ quan/đơn vị gửi văn bản'
    )
    
    recipient = fields.Char(
        string='Nơi nhận',
        required=True,
        help='Cơ quan/đơn vị nhận văn bản'
    )
    
    subject = fields.Text(
        string='Trích yếu',
        required=True,
        help='Nội dung trích yếu của văn bản'
    )
    
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('pending_approval', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('pending_sign', 'Chờ ký'),
        ('signed', 'Đã ký'),
        ('sent', 'Đã gửi'),
        ('received', 'Đã nhận'),
        ('expired', 'Hết hiệu lực'),
        ('archived', 'Lưu trữ'),
    ], string='Trạng thái', default='draft', required=True)
    
    priority = fields.Selection([
        ('low', 'Thấp'),
        ('normal', 'Bình thường'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp'),
    ], string='Độ ưu tiên', default='normal')
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Tệp đính kèm',
        help='Các tệp đính kèm của văn bản'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về văn bản'
    )
    
    # MỨC 1: Liên kết với HR Employee (dữ liệu gốc)
    assigned_employee_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên được gán',
        tracking=True,
        help='Nhân viên được gán xử lý văn bản này'
    )
    
    # Liên kết với khách hàng (nếu văn bản liên quan đến khách hàng)
    customer_id = fields.Many2one(
        'qlkh.customer',
        string='Khách hàng liên quan',
        help='Khách hàng liên quan đến văn bản (nếu có)'
    )
    
    # Liên kết với đơn hàng (nếu văn bản là hợp đồng, hóa đơn...)
    order_id = fields.Many2one(
        'qlkh.order',
        string='Đơn hàng liên quan',
        help='Đơn hàng liên quan đến văn bản (nếu có)'
    )
    
    # Liên kết với hợp đồng làm việc (nếu văn bản liên quan đến hợp đồng)
    contract_id = fields.Many2one(
        'om.hr.contract',
        string='Hợp đồng liên quan',
        help='Hợp đồng làm việc liên quan đến văn bản (nếu có)'
    )
    
    active = fields.Boolean(
        string='Hoạt động',
        default=True
    )
    
    # Chữ ký số
    effective_date = fields.Date(
        string='Ngày hiệu lực',
        help='Ngày văn bản có hiệu lực'
    )
    
    expiry_date = fields.Date(
        string='Ngày hết hạn',
        help='Ngày văn bản hết hiệu lực'
    )
    
    signature_ids = fields.One2many(
        'om.document.signature',
        'document_id',
        string='Chữ ký số',
        help='Danh sách chữ ký số của văn bản'
    )
    
    approval_ids = fields.One2many(
        'om.document.approval',
        'document_id',
        string='Quy trình duyệt',
        help='Quy trình duyệt văn bản'
    )
    
    history_ids = fields.One2many(
        'om.document.history',
        'document_id',
        string='Lịch sử',
        help='Lịch sử thay đổi văn bản'
    )
    
    signature_count = fields.Integer(
        string='Số chữ ký',
        compute='_compute_signature_count',
        store=False,
        help='Tổng số chữ ký'
    )
    
    signed_count = fields.Integer(
        string='Số chữ ký đã ký',
        compute='_compute_signature_count',
        store=False,
        help='Số chữ ký đã được ký'
    )
    
    approval_count = fields.Integer(
        string='Số bước duyệt',
        compute='_compute_approval_count',
        store=False,
        help='Tổng số bước duyệt'
    )
    
    approved_count = fields.Integer(
        string='Số bước đã duyệt',
        compute='_compute_approval_count',
        store=False,
        help='Số bước đã được duyệt'
    )
    
    is_signed = fields.Boolean(
        string='Đã ký',
        compute='_compute_is_signed',
        store=False,
        help='Văn bản đã được ký chưa'
    )
    
    is_approved = fields.Boolean(
        string='Đã duyệt',
        compute='_compute_is_approved',
        store=False,
        help='Văn bản đã được duyệt chưa'
    )
    
    is_expired = fields.Boolean(
        string='Hết hiệu lực',
        compute='_compute_is_expired',
        store=False,
        help='Văn bản đã hết hiệu lực chưa'
    )

    @api.depends('signature_ids', 'signature_ids.state')
    def _compute_signature_count(self):
        """Tính toán số chữ ký"""
        for record in self:
            record.signature_count = len(record.signature_ids)
            record.signed_count = len(record.signature_ids.filtered(lambda s: s.state == 'signed'))

    @api.depends('approval_ids', 'approval_ids.state')
    def _compute_approval_count(self):
        """Tính toán số bước duyệt"""
        for record in self:
            record.approval_count = len(record.approval_ids)
            record.approved_count = len(record.approval_ids.filtered(lambda a: a.state == 'approved'))

    @api.depends('signature_ids', 'signature_ids.state')
    def _compute_is_signed(self):
        """Kiểm tra văn bản đã được ký chưa"""
        for record in self:
            record.is_signed = bool(record.signature_ids.filtered(lambda s: s.state == 'signed'))

    @api.depends('approval_ids', 'approval_ids.state')
    def _compute_is_approved(self):
        """Kiểm tra văn bản đã được duyệt chưa"""
        for record in self:
            if record.approval_ids:
                record.is_approved = all(a.state == 'approved' for a in record.approval_ids)
            else:
                record.is_approved = False

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        """Kiểm tra văn bản đã hết hiệu lực chưa"""
        today = fields.Date.today()
        for record in self:
            if record.expiry_date:
                record.is_expired = record.expiry_date < today
            else:
                record.is_expired = False

    @api.model
    def _generate_number(self):
        """Tự động tạo số đi"""
        sequence = self.env['ir.sequence'].next_by_code('document.outgoing.number') or 'VBĐI001'
        return sequence

    @api.model
    def create(self, vals):
        """Override create để tự động tạo số đi nếu chưa có và ghi lịch sử"""
        if not vals.get('number'):
            vals['number'] = self._generate_number()
        record = super(DocumentOutgoing, self).create(vals)
        
        # Ghi lịch sử tạo mới (dùng sudo để bypass security)
        self.env['om.document.history'].sudo().create_history(
            document_id=record.id,
            action='create',
            notes='Tạo văn bản mới'
        )
        
        return record

    def write(self, vals):
        """Override write để ghi lịch sử thay đổi"""
        # Lưu giá trị cũ trước khi thay đổi
        old_values = {}
        for field_name in vals:
            if field_name in self._fields:
                for record in self:
                    old_value = getattr(record, field_name, False)
                    if old_value:
                        old_values[field_name] = str(old_value)
        
        result = super(DocumentOutgoing, self).write(vals)
        
        # Ghi lịch sử thay đổi
        for record in self:
            for field_name, new_value in vals.items():
                if field_name in self._fields and field_name not in ['write_date', 'write_uid', '__last_update']:
                    old_value = old_values.get(field_name, '')
                    self.env['om.document.history'].sudo().create_history(
                        document_id=record.id,
                        action='update',
                        field_name=field_name,
                        old_value=old_value,
                        new_value=str(new_value) if new_value else '',
                    )
        
        return result

    def action_submit_approval(self):
        """Gửi duyệt văn bản"""
        # Kiểm tra quyền soạn thảo của nhân viên được gán
        if self.assigned_employee_id:
            if not self.assigned_employee_id.check_permission('draft'):
                raise UserError(
                    f'Nhân viên {self.assigned_employee_id.name} không có quyền soạn thảo văn bản!\n'
                    f'Vui lòng kiểm tra phân quyền trong Quản lý nhân sự → Nhân viên.'
                )
            # Kiểm tra trạng thái nhân viên
            if self.assigned_employee_id.employee_status != 'working':
                raise UserError(
                    f'Nhân viên {self.assigned_employee_id.name} không đang làm việc, không thể gửi duyệt!'
                )
        else:
            # Nếu chưa gán nhân viên, tìm nhân viên theo email user hiện tại
            current_user_email = self.env.user.email
            if current_user_email:
                employee = self.env['om.hr.employee'].get_employee_by_email(current_user_email)
                if employee and not employee.check_permission('draft'):
                    raise UserError(
                        f'Bạn không có quyền soạn thảo văn bản!\n'
                        f'Vui lòng liên hệ quản trị viên để cấp quyền.'
                    )
        
        self.write({'status': 'pending_approval'})
        
        # Ghi lịch sử (dùng sudo để bypass security)
        self.env['om.document.history'].sudo().create_history(
            document_id=self.id,
            action='approve',
            notes='Gửi duyệt văn bản'
        )
        
        return True

    def action_approved(self):
        """Chuyển trạng thái sang Đã duyệt"""
        self.write({'status': 'approved'})
        
        # Ghi lịch sử
        self.env['om.document.history'].sudo().create_history(
            document_id=self.id,
            action='approve',
            notes='Văn bản đã được duyệt'
        )
        
        return True

    def action_sent(self):
        """Chuyển trạng thái sang Đã gửi"""
        self.write({'status': 'sent'})
        
        # Ghi lịch sử
        self.env['om.document.history'].sudo().create_history(
            document_id=self.id,
            action='send',
            notes='Văn bản đã được gửi'
        )
        
        return True

    def action_received(self):
        """Chuyển trạng thái sang Đã nhận"""
        self.write({'status': 'received'})
        
        # Ghi lịch sử
        self.env['om.document.history'].sudo().create_history(
            document_id=self.id,
            action='receive',
            notes='Văn bản đã được nhận'
        )
        
        return True

