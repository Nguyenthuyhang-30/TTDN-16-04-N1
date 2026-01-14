# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime


class DocumentIncoming(models.Model):
    _name = 'om.document.incoming'
    _description = 'Văn bản đến'
    _order = 'date_received desc, number'

    name = fields.Char(
        string='Số văn bản',
        required=True,
        help='Số hiệu văn bản đến'
    )
    
    number = fields.Char(
        string='Số đến',
        required=True,
        default=lambda self: self._generate_number(),
        help='Số đến của văn bản'
    )
    
    document_type_id = fields.Many2one(
        'om.document.type',
        string='Loại văn bản',
        required=True,
        help='Loại văn bản'
    )
    
    date_received = fields.Date(
        string='Ngày nhận',
        required=True,
        default=fields.Date.today,
        help='Ngày nhận văn bản'
    )
    
    date_document = fields.Date(
        string='Ngày văn bản',
        help='Ngày trên văn bản'
    )
    
    sender = fields.Char(
        string='Nơi gửi',
        required=True,
        help='Cơ quan/đơn vị gửi văn bản'
    )
    
    recipient = fields.Char(
        string='Nơi nhận',
        help='Cơ quan/đơn vị nhận văn bản'
    )
    
    subject = fields.Text(
        string='Trích yếu',
        required=True,
        help='Nội dung trích yếu của văn bản'
    )
    
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('received', 'Đã nhận'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
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
    
    active = fields.Boolean(
        string='Hoạt động',
        default=True
    )

    @api.model
    def _generate_number(self):
        """Tự động tạo số đến"""
        sequence = self.env['ir.sequence'].next_by_code('document.incoming.number') or 'VBĐ001'
        return sequence

    @api.model
    def create(self, vals):
        """MỨC 2: Tự động gán nhân viên xử lý văn bản theo độ ưu tiên"""
        if not vals.get('number'):
            vals['number'] = self._generate_number()
        
        record = super(DocumentIncoming, self).create(vals)
        
        # Nếu văn bản có độ ưu tiên cao hoặc khẩn cấp và chưa được gán
        if not record.assigned_employee_id and record.priority in ['high', 'urgent']:
            # Tự động gán cho nhân viên trong phòng ban phù hợp
            # Tìm nhân viên có ít văn bản đang xử lý nhất
            employees = self.env['om.hr.employee'].search([('active', '=', True)])
            if employees:
                # Gán cho nhân viên đầu tiên (có thể cải thiện logic sau)
                record.assigned_employee_id = employees[0]
        
        return record

    def action_received(self):
        """Chuyển trạng thái sang Đã nhận"""
        self.write({'status': 'received'})
        return True

    def action_processing(self):
        """Chuyển trạng thái sang Đang xử lý"""
        self.write({'status': 'processing'})
        return True

    def action_completed(self):
        """Chuyển trạng thái sang Hoàn thành"""
        self.write({'status': 'completed'})
        return True

