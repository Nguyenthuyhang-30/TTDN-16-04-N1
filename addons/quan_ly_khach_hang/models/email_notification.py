# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class EmailNotification(models.Model):
    _name = 'qlkh.email.notification'
    _description = 'Email và thông báo'
    _order = 'sent_date desc, create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    subject = fields.Char(
        string='Chủ đề',
        required=True,
        tracking=True,
        help='Chủ đề email'
    )
    
    recipient_ids = fields.Many2many(
        'qlkh.customer',
        string='Người nhận',
        required=True,
        help='Danh sách khách hàng nhận email'
    )
    
    recipient_emails = fields.Char(
        string='Email người nhận',
        compute='_compute_recipient_emails',
        store=False,
        help='Danh sách email người nhận (hiển thị)'
    )
    
    body = fields.Html(
        string='Nội dung',
        help='Nội dung email'
    )
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('sent', 'Đã gửi'),
        ('failed', 'Gửi thất bại'),
    ], string='Trạng thái',
        default='draft',
        tracking=True,
        help='Trạng thái email'
    )
    
    sent_date = fields.Datetime(
        string='Ngày gửi',
        readonly=True,
        help='Ngày và giờ gửi email'
    )
    
    mail_ids = fields.One2many(
        'mail.mail',
        'res_id',
        string='Email đã gửi',
        domain=[('model', '=', 'qlkh.email.notification')],
        help='Danh sách email đã gửi'
    )

    @api.depends('recipient_ids', 'recipient_ids.email')
    def _compute_recipient_emails(self):
        """Tính danh sách email người nhận"""
        for record in self:
            emails = record.recipient_ids.mapped('email')
            emails = [e for e in emails if e]  # Loại bỏ email rỗng
            record.recipient_emails = ', '.join(emails) if emails else ''

    def action_send(self):
        """Gửi email"""
        for record in self:
            if not record.recipient_ids:
                raise UserError('Vui lòng chọn ít nhất một người nhận!')
            
            if not record.body:
                raise UserError('Vui lòng nhập nội dung email!')
            
            # Lấy danh sách email hợp lệ
            valid_recipients = record.recipient_ids.filtered(lambda r: r.email)
            if not valid_recipients:
                raise UserError('Không có người nhận nào có email hợp lệ!')
            
            # Gửi email cho từng người nhận
            try:
                for recipient in valid_recipients:
                    mail_values = {
                        'subject': record.subject,
                        'body_html': record.body,
                        'email_to': recipient.email,
                        'email_from': self.env.user.email or self.env.company.email,
                        'model': 'qlkh.email.notification',
                        'res_id': record.id,
                    }
                    mail = self.env['mail.mail'].create(mail_values)
                    mail.send()
                
                record.state = 'sent'
                record.sent_date = fields.Datetime.now()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Thành công',
                        'message': f'Đã gửi email đến {len(valid_recipients)} người nhận!',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            except Exception as e:
                record.state = 'failed'
                raise UserError(f'Lỗi khi gửi email: {str(e)}')
        
        return True

    def action_reset_to_draft(self):
        """Quay lại trạng thái nháp"""
        for record in self:
            record.state = 'draft'
            record.sent_date = False
        
        return True

