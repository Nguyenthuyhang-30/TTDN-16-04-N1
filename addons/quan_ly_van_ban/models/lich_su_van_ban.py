# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class DocumentHistory(models.Model):
    _name = 'om.document.history'
    _description = 'Lịch sử văn bản'
    _order = 'timestamp desc'

    name = fields.Char(
        string='Tên lịch sử',
        compute='_compute_name',
        store=True,
        help='Tên lịch sử'
    )
    
    document_id = fields.Many2one(
        'om.document.outgoing',
        string='Văn bản đi',
        ondelete='cascade',
        help='Văn bản đi'
    )
    
    document_incoming_id = fields.Many2one(
        'om.document.incoming',
        string='Văn bản đến',
        ondelete='cascade',
        help='Văn bản đến'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Người thực hiện',
        required=True,
        default=lambda self: self.env.user,
        help='Người dùng thực hiện hành động'
    )
    
    employee_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên',
        help='Nhân viên thực hiện hành động'
    )
    
    action = fields.Selection([
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('approve', 'Duyệt'),
        ('reject', 'Từ chối'),
        ('sign', 'Ký'),
        ('send', 'Gửi'),
        ('receive', 'Nhận'),
        ('archive', 'Lưu trữ'),
        ('restore', 'Khôi phục'),
    ], string='Hành động',
        required=True,
        help='Hành động được thực hiện'
    )
    
    old_value = fields.Text(
        string='Giá trị cũ',
        help='Giá trị trước khi thay đổi'
    )
    
    new_value = fields.Text(
        string='Giá trị mới',
        help='Giá trị sau khi thay đổi'
    )
    
    field_name = fields.Char(
        string='Trường thay đổi',
        help='Tên trường được thay đổi'
    )
    
    timestamp = fields.Datetime(
        string='Thời gian',
        required=True,
        default=fields.Datetime.now,
        help='Thời gian thực hiện hành động'
    )
    
    ip_address = fields.Char(
        string='Địa chỉ IP',
        help='Địa chỉ IP của thiết bị'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú bổ sung'
    )

    @api.depends('document_id', 'document_incoming_id', 'action', 'timestamp')
    def _compute_name(self):
        """Tự động tạo tên lịch sử"""
        for record in self:
            doc_name = ''
            if record.document_id:
                doc_name = record.document_id.name or record.document_id.number
            elif record.document_incoming_id:
                doc_name = record.document_incoming_id.name or record.document_incoming_id.number
            
            action_name = dict(record._fields['action'].selection).get(record.action, '')
            time_str = record.timestamp.strftime('%d/%m/%Y %H:%M:%S') if record.timestamp else ''
            record.name = f"{doc_name} - {action_name} - {time_str}"

    @api.model
    def create_history(self, document_id=None, document_incoming_id=None, action=None, 
                      field_name=None, old_value=None, new_value=None, notes=None):
        """Tạo bản ghi lịch sử"""
        ip_address = ''
        try:
            if hasattr(self.env['ir.http'], '_get_request_ip'):
                ip_address = self.env['ir.http']._get_request_ip()
        except:
            pass
        
        employee_id = None
        # Tìm employee theo email (vì model om.hr.employee không có field user_id)
        try:
            if self.env.user.email:
                employee = self.env['om.hr.employee'].search([('email', '=', self.env.user.email)], limit=1)
                if employee:
                    employee_id = employee.id
        except Exception:
            # Nếu không tìm thấy hoặc có lỗi, bỏ qua
            pass
        
        # Sử dụng sudo() để bypass security check khi tạo lịch sử
        # Vì lịch sử là hệ thống tự động tạo, không phải người dùng tạo
        return self.sudo().create({
            'document_id': document_id,
            'document_incoming_id': document_incoming_id,
            'action': action,
            'field_name': field_name,
            'old_value': old_value,
            'new_value': new_value,
            'notes': notes,
            'ip_address': ip_address,
            'employee_id': employee_id,
        })

