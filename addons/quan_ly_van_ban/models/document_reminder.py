# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError


class DocumentReminder(models.Model):
    _name = 'om.document.reminder'
    _description = 'Nhắc hạn văn bản'
    _order = 'reminder_date desc, document_id'

    name = fields.Char(
        string='Tên nhắc hạn',
        compute='_compute_name',
        store=True,
        help='Tên nhắc hạn'
    )
    
    document_id = fields.Many2one(
        'om.document.outgoing',
        string='Văn bản',
        required=True,
        ondelete='cascade',
        help='Văn bản cần nhắc hạn'
    )
    
    reminder_type = fields.Selection([
        ('30_days', 'Cảnh báo sớm (30 ngày)'),
        ('7_days', 'Khẩn cấp (7 ngày)'),
        ('1_day', 'Rất gấp (1 ngày)'),
    ], string='Loại nhắc hạn',
        required=True,
        help='Loại nhắc hạn dựa trên số ngày còn lại'
    )
    
    days_remaining = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_days_remaining',
        store=True,
        help='Số ngày còn lại đến ngày hết hạn'
    )
    
    reminder_date = fields.Datetime(
        string='Ngày nhắc hạn',
        required=True,
        default=fields.Datetime.now,
        help='Thời gian gửi nhắc hạn'
    )
    
    notification_sent = fields.Boolean(
        string='Đã gửi thông báo',
        default=False,
        help='Đã gửi thông báo nội bộ chưa'
    )
    
    email_sent = fields.Boolean(
        string='Đã gửi email',
        default=False,
        help='Đã gửi email nhắc nhở chưa'
    )
    
    activity_created = fields.Boolean(
        string='Đã tạo activity',
        default=False,
        help='Đã tạo activity chưa'
    )
    
    recipient_creator = fields.Boolean(
        string='Gửi người tạo',
        default=True,
        help='Gửi thông báo cho người tạo văn bản'
    )
    
    recipient_manager = fields.Boolean(
        string='Gửi trưởng phòng',
        default=True,
        help='Gửi thông báo cho trưởng phòng'
    )
    
    recipient_customer = fields.Boolean(
        string='Gửi khách hàng',
        default=True,
        help='Gửi thông báo cho khách hàng'
    )

    @api.depends('document_id', 'reminder_type', 'reminder_date')
    def _compute_name(self):
        """Tự động tạo tên nhắc hạn"""
        for record in self:
            if record.document_id:
                doc_name = record.document_id.name or record.document_id.number
                type_name = dict(record._fields['reminder_type'].selection).get(record.reminder_type, '')
                record.name = f"{doc_name} - {type_name}"
            else:
                record.name = 'Nhắc hạn văn bản'

    @api.depends('document_id', 'document_id.expiry_date')
    def _compute_days_remaining(self):
        """Tính toán số ngày còn lại"""
        today = date.today()
        for record in self:
            if record.document_id and record.document_id.expiry_date:
                delta = record.document_id.expiry_date - today
                record.days_remaining = delta.days
            else:
                record.days_remaining = 0

    def action_send_notifications(self):
        """Gửi tất cả các thông báo"""
        self.ensure_one()
        
        # Gửi thông báo nội bộ
        if not self.notification_sent:
            self._send_internal_notification()
        
        # Gửi email
        if not self.email_sent:
            self._send_email_reminder()
        
        # Tạo activity
        if not self.activity_created:
            self._create_activity()
        
        return True

    def _send_internal_notification(self):
        """Gửi thông báo nội bộ"""
        self.ensure_one()
        
        # Tạo thông báo cho người tạo văn bản
        if self.recipient_creator and self.document_id.create_uid:
            self.env['mail.message'].create({
                'model': 'om.document.outgoing',
                'res_id': self.document_id.id,
                'message_type': 'notification',
                'body': f'<p>Văn bản <strong>{self.document_id.name}</strong> sẽ hết hiệu lực trong <strong>{self.days_remaining} ngày</strong> (Ngày hết hạn: {self.document_id.expiry_date.strftime("%d/%m/%Y") if self.document_id.expiry_date else ""})</p>',
                'author_id': self.env.user.partner_id.id,
                'partner_ids': [(6, 0, [self.document_id.create_uid.partner_id.id])],
            })
        
        # Tạo thông báo cho trưởng phòng (nếu có)
        if self.recipient_manager and self.document_id.assigned_employee_id:
            manager = self.document_id.assigned_employee_id
            # Tìm user theo email của employee
            if manager.email:
                user = self.env['res.users'].search([('email', '=', manager.email)], limit=1)
                if user:
                    self.env['mail.message'].create({
                        'model': 'om.document.outgoing',
                        'res_id': self.document_id.id,
                        'message_type': 'notification',
                        'body': f'<p>Văn bản <strong>{self.document_id.name}</strong> sẽ hết hiệu lực trong <strong>{self.days_remaining} ngày</strong> (Ngày hết hạn: {self.document_id.expiry_date.strftime("%d/%m/%Y") if self.document_id.expiry_date else ""})</p>',
                        'author_id': self.env.user.partner_id.id,
                        'partner_ids': [(6, 0, [user.partner_id.id])],
                    })
        
        self.notification_sent = True

    def _send_email_reminder(self):
        """Gửi email nhắc nhở"""
        self.ensure_one()
        
        # Lấy email template
        template = self.env.ref('quan_ly_van_ban.email_template_document_expiry_reminder', raise_if_not_found=False)
        if not template:
            # Nếu không có template, tạo email thủ công
            self._send_email_manual()
            return
        
        # Gửi email cho người tạo
        if self.recipient_creator and self.document_id.create_uid and self.document_id.create_uid.email:
            template.send_mail(self.document_id.id, force_send=True, email_values={
                'email_to': self.document_id.create_uid.email,
            })
        
        # Gửi email cho trưởng phòng
        if self.recipient_manager and self.document_id.assigned_employee_id:
            manager = self.document_id.assigned_employee_id
            if manager.email:
                template.send_mail(self.document_id.id, force_send=True, email_values={
                    'email_to': manager.email,
                })
        
        # Gửi email cho khách hàng
        if self.recipient_customer and self.document_id.customer_id:
            customer = self.document_id.customer_id
            if customer.email:
                template.send_mail(self.document_id.id, force_send=True, email_values={
                    'email_to': customer.email,
                })
        
        self.email_sent = True

    def _send_email_manual(self):
        """Gửi email thủ công nếu không có template"""
        self.ensure_one()
        
        subject = f"[Nhắc hạn] {self.document_id.name} sắp hết hiệu lực"
        body = f"""
        <p>Xin chào,</p>
        <p>Văn bản sau đây sẽ hết hiệu lực trong <strong>{self.days_remaining} ngày</strong>:</p>
        <ul>
            <li><strong>Tên văn bản:</strong> {self.document_id.name}</li>
            <li><strong>Số hiệu:</strong> {self.document_id.number}</li>
            <li><strong>Ngày hết hạn:</strong> {self.document_id.expiry_date.strftime('%d/%m/%Y') if self.document_id.expiry_date else 'N/A'}</li>
            <li><strong>Khách hàng:</strong> {self.document_id.customer_id.name if self.document_id.customer_id else 'N/A'}</li>
        </ul>
        <p>Vui lòng kiểm tra và thực hiện gia hạn nếu cần thiết.</p>
        <p>Trân trọng,<br/>Hệ thống quản lý văn bản</p>
        """
        
        # Gửi email cho người tạo
        if self.recipient_creator and self.document_id.create_uid and self.document_id.create_uid.email:
            self.env['mail.mail'].create({
                'subject': subject,
                'body_html': body,
                'email_to': self.document_id.create_uid.email,
                'email_from': self.env.user.email or self.env['ir.config_parameter'].sudo().get_param('mail.catchall.alias', 'noreply@odoo.com'),
            }).send()
        
        # Gửi email cho trưởng phòng
        if self.recipient_manager and self.document_id.assigned_employee_id:
            manager = self.document_id.assigned_employee_id
            if manager.email:
                self.env['mail.mail'].create({
                    'subject': subject,
                    'body_html': body,
                    'email_to': manager.email,
                    'email_from': self.env.user.email or self.env['ir.config_parameter'].sudo().get_param('mail.catchall.alias', 'noreply@odoo.com'),
                }).send()
        
        # Gửi email cho khách hàng
        if self.recipient_customer and self.document_id.customer_id:
            customer = self.document_id.customer_id
            if customer.email:
                self.env['mail.mail'].create({
                    'subject': subject,
                    'body_html': body,
                    'email_to': customer.email,
                    'email_from': self.env.user.email or self.env['ir.config_parameter'].sudo().get_param('mail.catchall.alias', 'noreply@odoo.com'),
                }).send()
        
        self.email_sent = True

    def _create_activity(self):
        """Tạo activity nhắc nhở"""
        self.ensure_one()
        
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
        
        # Tạo activity cho người tạo
        if self.recipient_creator and self.document_id.create_uid:
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get_id('om.document.outgoing'),
                'res_id': self.document_id.id,
                'activity_type_id': activity_type.id,
                'summary': f'Văn bản sắp hết hiệu lực ({self.days_remaining} ngày)',
                'note': f'Văn bản {self.document_id.name} sẽ hết hiệu lực vào ngày {self.document_id.expiry_date.strftime("%d/%m/%Y") if self.document_id.expiry_date else "N/A"}. Vui lòng kiểm tra và gia hạn nếu cần.',
                'user_id': self.document_id.create_uid.id,
                'date_deadline': self.document_id.expiry_date or fields.Date.today(),
            })
        
        # Tạo activity cho trưởng phòng
        if self.recipient_manager and self.document_id.assigned_employee_id:
            manager = self.document_id.assigned_employee_id
            # Tìm user theo email của employee
            if manager.email:
                user = self.env['res.users'].search([('email', '=', manager.email)], limit=1)
                if user:
                    self.env['mail.activity'].create({
                        'res_model_id': self.env['ir.model']._get_id('om.document.outgoing'),
                        'res_id': self.document_id.id,
                        'activity_type_id': activity_type.id,
                        'summary': f'Văn bản sắp hết hiệu lực ({self.days_remaining} ngày)',
                        'note': f'Văn bản {self.document_id.name} sẽ hết hiệu lực vào ngày {self.document_id.expiry_date.strftime("%d/%m/%Y") if self.document_id.expiry_date else "N/A"}. Vui lòng kiểm tra và gia hạn nếu cần.',
                        'user_id': user.id,
                        'date_deadline': self.document_id.expiry_date or fields.Date.today(),
                    })
        
        self.activity_created = True


class DocumentOutgoing(models.Model):
    _inherit = 'om.document.outgoing'

    reminder_ids = fields.One2many(
        'om.document.reminder',
        'document_id',
        string='Nhắc hạn',
        help='Danh sách nhắc hạn văn bản'
    )

    @api.model
    def _cron_check_expiring_documents(self):
        """Cron job: Quét văn bản sắp hết hạn (chạy hàng ngày 08:00)"""
        today = date.today()
        
        # Tìm các văn bản đã ký và có ngày hết hạn
        documents = self.search([
            ('status', '=', 'signed'),
            ('expiry_date', '!=', False),
            ('expiry_date', '>', today),  # Chưa hết hạn
        ])
        
        for doc in documents:
            if not doc.expiry_date:
                continue
            
            days_remaining = (doc.expiry_date - today).days
            
            # Xác định loại nhắc hạn
            reminder_type = None
            if days_remaining <= 1:
                reminder_type = '1_day'
            elif days_remaining <= 7:
                reminder_type = '7_days'
            elif days_remaining <= 30:
                reminder_type = '30_days'
            
            # Chỉ tạo nhắc hạn nếu trong khoảng 30 ngày
            if reminder_type:
                # Kiểm tra xem đã có nhắc hạn cho loại này chưa
                # Kiểm tra xem đã có nhắc hạn cho loại này trong ngày hôm nay chưa
                today_start = fields.Datetime.start_of(fields.Datetime.today(), 'day')
                existing_reminder = self.env['om.document.reminder'].search([
                    ('document_id', '=', doc.id),
                    ('reminder_type', '=', reminder_type),
                    ('reminder_date', '>=', today_start),
                ], limit=1)
                
                if not existing_reminder:
                    # Tạo nhắc hạn mới
                    reminder = self.env['om.document.reminder'].create({
                        'document_id': doc.id,
                        'reminder_type': reminder_type,
                        'days_remaining': days_remaining,
                    })
                    
                    # Tự động gửi thông báo
                    reminder.action_send_notifications()

