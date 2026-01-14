# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import hashlib


class DocumentSignature(models.Model):
    _name = 'om.document.signature'
    _description = 'Chữ ký số'
    _order = 'signed_date desc'

    name = fields.Char(
        string='Tên chữ ký',
        compute='_compute_name',
        store=True,
        help='Tên chữ ký số'
    )
    
    document_id = fields.Many2one(
        'om.document.outgoing',
        string='Văn bản',
        required=True,
        ondelete='cascade',
        help='Văn bản được ký'
    )
    
    document_incoming_id = fields.Many2one(
        'om.document.incoming',
        string='Văn bản đến',
        ondelete='cascade',
        help='Văn bản đến được ký (nếu có)'
    )
    
    signer_id = fields.Many2one(
        'om.hr.employee',
        string='Người ký',
        required=True,
        help='Nhân viên ký văn bản'
    )
    
    certificate_id = fields.Many2one(
        'om.digital.certificate',
        string='Chứng thư số',
        help='Chứng thư số sử dụng để ký'
    )
    
    signature_type = fields.Selection([
        ('internal', 'Ký nội bộ'),
        ('customer', 'Ký khách hàng'),
    ], string='Loại chữ ký',
        required=True,
        default='internal',
        help='Loại chữ ký: nội bộ hoặc khách hàng'
    )
    
    signature_method = fields.Selection([
        ('usb_token', 'USB Token'),
        ('remote', 'Ký số từ xa'),
        ('image_otp', 'Ký hình ảnh + OTP'),
    ], string='Hình thức ký',
        help='Hình thức ký số'
    )
    
    signature_image = fields.Binary(
        string='Hình ảnh chữ ký',
        help='Hình ảnh chữ ký (nếu ký bằng hình ảnh)'
    )
    
    signature_hash = fields.Char(
        string='Hash chữ ký',
        help='Mã hash của chữ ký để xác thực'
    )
    
    signed_date = fields.Datetime(
        string='Thời gian ký',
        default=fields.Datetime.now,
        help='Thời gian ký văn bản'
    )
    
    ip_address = fields.Char(
        string='IP thiết bị',
        help='Địa chỉ IP của thiết bị ký'
    )
    
    state = fields.Selection([
        ('pending', 'Chờ ký'),
        ('signed', 'Đã ký'),
        ('rejected', 'Từ chối'),
        ('expired', 'Hết hạn'),
    ], string='Trạng thái',
        default='pending',
        required=True,
        help='Trạng thái chữ ký'
    )
    
    position_x = fields.Float(
        string='Vị trí X',
        help='Vị trí X của chữ ký trên tài liệu (mm)'
    )
    
    position_y = fields.Float(
        string='Vị trí Y',
        help='Vị trí Y của chữ ký trên tài liệu (mm)'
    )
    
    page_number = fields.Integer(
        string='Số trang',
        default=1,
        help='Số trang đặt chữ ký'
    )
    
    otp_code = fields.Char(
        string='Mã OTP',
        help='Mã OTP sử dụng để xác thực (nếu có)'
    )
    
    signed_file = fields.Binary(
        string='File đã ký',
        help='File PDF đã được đóng dấu chữ ký'
    )
    
    signed_filename = fields.Char(
        string='Tên file đã ký',
        help='Tên file PDF đã ký'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về chữ ký'
    )
    
    # Thông tin khách hàng (nếu ký khách hàng)
    customer_id = fields.Many2one(
        'qlkh.customer',
        string='Khách hàng',
        help='Chọn khách hàng từ danh sách (nếu ký khách hàng)'
    )
    
    customer_email = fields.Char(
        string='Email khách hàng',
        help='Email khách hàng (tự động điền khi chọn khách hàng)'
    )
    
    customer_name = fields.Char(
        string='Tên khách hàng',
        help='Tên khách hàng (tự động điền khi chọn khách hàng)'
    )
    
    sign_link = fields.Char(
        string='Link ký',
        help='Link để khách hàng ký (nếu ký khách hàng)'
    )
    
    sign_link_expiry = fields.Datetime(
        string='Link hết hạn',
        help='Thời gian hết hạn của link ký'
    )

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        """Tự động điền thông tin khách hàng khi chọn"""
        if self.customer_id:
            self.customer_name = self.customer_id.name
            self.customer_email = self.customer_id.email or ''

    @api.depends('document_id', 'signer_id', 'signed_date', 'signature_type', 'customer_id', 'customer_name')
    def _compute_name(self):
        """Tự động tạo tên chữ ký"""
        for record in self:
            if record.document_id:
                doc_name = record.document_id.name or record.document_id.number
                # Nếu là ký khách hàng, ưu tiên hiển thị tên khách hàng
                if record.signature_type == 'customer':
                    if record.customer_id:
                        signer_name = record.customer_id.name
                    elif record.customer_name:
                        signer_name = record.customer_name
                    elif record.signer_id:
                        signer_name = record.signer_id.name
                    else:
                        signer_name = 'Khách hàng'
                else:
                    signer_name = record.signer_id.name if record.signer_id else 'Chưa chọn'
                
                date_str = record.signed_date.strftime('%d/%m/%Y %H:%M') if record.signed_date else ''
                record.name = f"{doc_name} - {signer_name} - {date_str}"
            else:
                record.name = 'Chữ ký số'

    def action_sign(self):
        """Thực hiện ký số"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError('Chỉ có thể ký các chữ ký đang chờ ký!')
        
        # Tạo hash cho chữ ký
        content = f"{self.document_id.id}_{self.signer_id.id}_{fields.Datetime.now()}"
        self.signature_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Cập nhật trạng thái
        self.write({
            'state': 'signed',
            'signed_date': fields.Datetime.now(),
            'ip_address': self.env['ir.http']._get_request_ip() if hasattr(self.env['ir.http'], '_get_request_ip') else '',
        })
        
        # Cập nhật trạng thái văn bản
        if self.document_id:
            if self.document_id.status == 'approved':
                self.document_id.write({'status': 'signed'})
        
        return True

    def action_reject(self):
        """Từ chối ký"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError('Chỉ có thể từ chối các chữ ký đang chờ ký!')
        
        self.write({
            'state': 'rejected',
        })
        
        return True

    def action_send_sign_request(self):
        """Gửi yêu cầu ký cho khách hàng"""
        self.ensure_one()
        # Ưu tiên lấy email từ customer_id, nếu không có thì lấy từ customer_email
        if self.customer_id and self.customer_id.email:
            self.customer_email = self.customer_id.email
            if not self.customer_name:
                self.customer_name = self.customer_id.name
        
        if not self.customer_email:
            raise UserError('Vui lòng chọn khách hàng hoặc nhập email khách hàng!')
        
        if self.state != 'pending':
            raise UserError('Chỉ có thể gửi yêu cầu ký cho chữ ký đang chờ ký!')
        
        # Tạo link ký với token bảo mật
        import secrets
        token = secrets.token_urlsafe(32)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.sign_link = f"{base_url}/document/sign/{token}"
        self.sign_link_expiry = fields.Datetime.add(fields.Datetime.now(), days=7)
        
        # Lưu token vào notes hoặc tạo model riêng để lưu token
        # (Trong thực tế nên tạo model om.document.sign.token để lưu token và map với signature)
        if not self.notes:
            self.notes = f"Token: {token}\n"
        else:
            self.notes += f"\nToken: {token}"
        
        # Gửi email sử dụng template
        template = self.env.ref('quan_ly_van_ban.email_template_customer_sign_request', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True, email_values={
                'email_to': self.customer_email,
            })
        else:
            # Gửi email thủ công nếu không có template
            subject = f"Yêu cầu ký văn bản: {self.document_id.name}"
            body = f"""
            <p>Xin chào {self.customer_name or 'Quý khách'},</p>
            <p>Chúng tôi cần bạn ký số văn bản: <strong>{self.document_id.name}</strong></p>
            <p>Vui lòng click vào link bên dưới để ký:</p>
            <p><a href="{self.sign_link}">Ký số văn bản</a></p>
            <p>Link này sẽ hết hạn vào: {self.sign_link_expiry.strftime('%d/%m/%Y %H:%M') if self.sign_link_expiry else 'N/A'}</p>
            <p>Trân trọng,<br/>Hệ thống quản lý văn bản</p>
            """
            self.env['mail.mail'].create({
                'subject': subject,
                'body_html': body,
                'email_to': self.customer_email,
                'email_from': self.env.user.email or self.env['ir.config_parameter'].sudo().get_param('mail.catchall.alias', 'noreply@odoo.com'),
            }).send()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã gửi yêu cầu ký đến {self.customer_email}',
                'type': 'success',
            }
        }

