# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import hashlib


class SignDocumentWizard(models.TransientModel):
    _name = 'om.sign.document.wizard'
    _description = 'Wizard ký số văn bản'

    document_id = fields.Many2one(
        'om.document.outgoing',
        string='Văn bản',
        required=True,
        help='Văn bản cần ký'
    )
    
    signature_method = fields.Selection([
        ('draw', 'Vẽ chữ ký'),
        ('upload', 'Tải lên chữ ký'),
        ('font', 'Chữ ký font'),
    ], string='Phương thức ký',
        required=True,
        default='draw',
        help='Chọn phương thức tạo chữ ký'
    )
    
    # Vẽ chữ ký
    signature_draw = fields.Binary(
        string='Chữ ký vẽ',
        help='Chữ ký được vẽ bằng chuột/touchpad (PNG/SVG)'
    )
    
    # Upload chữ ký
    signature_upload = fields.Binary(
        string='Chữ ký upload',
        help='Upload hình ảnh chữ ký đã scan (PNG/JPG)'
    )
    
    signature_upload_filename = fields.Char(
        string='Tên file chữ ký'
    )
    
    # Chữ ký font
    signature_font_style = fields.Selection([
        ('cursive', 'Cursive'),
        ('elegant', 'Elegant'),
        ('modern', 'Modern'),
    ], string='Style chữ ký font',
        help='Style của chữ ký font'
    )
    
    signature_font_name = fields.Char(
        string='Tên để tạo chữ ký',
        help='Nhập tên để tự động tạo chữ ký'
    )
    
    # Vị trí ký
    page_number = fields.Integer(
        string='Số trang',
        default=1,
        required=True,
        help='Số trang đặt chữ ký'
    )
    
    position_x = fields.Float(
        string='Vị trí X (mm)',
        default=0.0,
        help='Vị trí X của chữ ký trên tài liệu (mm)'
    )
    
    position_y = fields.Float(
        string='Vị trí Y (mm)',
        default=0.0,
        help='Vị trí Y của chữ ký trên tài liệu (mm)'
    )
    
    # OTP (nếu cần)
    otp_code = fields.Char(
        string='Mã OTP',
        help='Mã OTP để xác thực (nếu cần)'
    )
    
    # Người ký
    signer_id = fields.Many2one(
        'om.hr.employee',
        string='Người ký',
        required=False,  # Tạm thời bỏ required để tránh lỗi với record cũ
        help='Nhân viên ký văn bản'
    )
    
    # Chứng thư số
    certificate_id = fields.Many2one(
        'om.digital.certificate',
        string='Chứng thư số',
        help='Chứng thư số sử dụng để ký (nếu có)'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về chữ ký'
    )

    @api.model
    def default_get(self, fields_list):
        """Lấy giá trị mặc định"""
        res = super(SignDocumentWizard, self).default_get(fields_list)
        
        if 'document_id' in fields_list and self._context.get('active_id'):
            res['document_id'] = self._context.get('active_id')
        
        # Tự động chọn nhân viên hiện tại (tìm theo email)
        if self.env.user.email:
            employee = self.env['om.hr.employee'].search([('email', '=', self.env.user.email)], limit=1)
            if employee:
                res['signer_id'] = employee.id
                # Tìm chứng thư số của nhân viên
                certificate = self.env['om.digital.certificate'].search([
                    ('employee_id', '=', employee.id),
                    ('is_active', '=', True)
                ], limit=1)
                if certificate:
                    res['certificate_id'] = certificate.id
        
        return res

    def action_sign(self):
        """Thực hiện ký số"""
        self.ensure_one()
        
        if not self.document_id:
            raise UserError('Vui lòng chọn văn bản cần ký!')
        
        # Lấy hình ảnh chữ ký dựa trên phương thức
        signature_image = None
        
        if self.signature_method == 'draw':
            signature_image = self.signature_draw
        elif self.signature_method == 'upload':
            signature_image = self.signature_upload
        elif self.signature_method == 'font':
            # Tạo chữ ký font (giả lập - trong thực tế cần dùng thư viện font)
            signature_image = self._generate_font_signature()
        
        if not signature_image:
            raise UserError('Vui lòng tạo hoặc upload chữ ký!')
        
        # Nếu chưa chọn người ký, tự động tìm theo email
        if not self.signer_id:
            if self.env.user.email:
                employee = self.env['om.hr.employee'].search([('email', '=', self.env.user.email)], limit=1)
                if employee:
                    self.signer_id = employee.id
                else:
                    raise UserError('Vui lòng chọn người ký hoặc cập nhật email trong thông tin nhân viên để khớp với email của bạn!')
            else:
                raise UserError('Vui lòng chọn người ký!')
        
        # Tạo hash chữ ký
        content = f"{self.document_id.id}_{self.signer_id.id}_{fields.Datetime.now()}_{signature_image}"
        signature_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Lấy IP address
        ip_address = ''
        try:
            if hasattr(self.env['ir.http'], '_get_request_ip'):
                ip_address = self.env['ir.http']._get_request_ip()
        except:
            pass
        
        # Tạo bản ghi chữ ký số
        signature = self.env['om.document.signature'].create({
            'document_id': self.document_id.id,
            'signer_id': self.signer_id.id,
            'certificate_id': self.certificate_id.id if self.certificate_id else False,
            'signature_type': 'internal',
            'signature_method': 'image_otp',
            'signature_image': signature_image,
            'signature_hash': signature_hash,
            'signed_date': fields.Datetime.now(),
            'ip_address': ip_address,
            'state': 'signed',
            'page_number': self.page_number,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'otp_code': self.otp_code,
            'notes': self.notes,
        })
        
        # Nhúng chữ ký vào PDF (nếu có file PDF)
        if self.document_id.attachment_ids:
            pdf_attachment = self.document_id.attachment_ids.filtered(lambda a: a.mimetype == 'application/pdf')
            if pdf_attachment:
                signed_pdf = self._embed_signature_to_pdf(pdf_attachment[0], signature_image, self.position_x, self.position_y, self.page_number)
                if signed_pdf:
                    signature.write({
                        'signed_file': signed_pdf,
                        'signed_filename': f"{self.document_id.name}_signed.pdf",
                    })
        
        # Cập nhật trạng thái văn bản
        if self.document_id.status == 'approved':
            self.document_id.write({'status': 'signed'})
        
        # Ghi lịch sử (dùng sudo để bypass security)
        self.env['om.document.history'].sudo().create_history(
            document_id=self.document_id.id,
            action='sign',
            notes=f'Đã ký số văn bản bằng phương thức {dict(self._fields["signature_method"].selection).get(self.signature_method)}'
        )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'om.document.signature',
            'res_id': signature.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _generate_font_signature(self):
        """Tạo chữ ký font (giả lập - cần thư viện font thực tế)"""
        # Trong thực tế, cần dùng thư viện như PIL/Pillow để tạo hình ảnh chữ ký từ font
        # Ở đây chỉ trả về None, người dùng cần upload hoặc vẽ chữ ký
        return None

    def _embed_signature_to_pdf(self, pdf_attachment, signature_image, x, y, page_num):
        """Nhúng chữ ký vào PDF"""
        try:
            # Cần thư viện như PyPDF2 hoặc reportlab để nhúng chữ ký vào PDF
            # Ở đây chỉ trả về None, cần cài đặt thư viện và implement logic
            # import PyPDF2
            # from reportlab.pdfgen import canvas
            # ... logic nhúng chữ ký vào PDF ...
            return None
        except Exception as e:
            # Log lỗi nhưng không raise để không block quá trình ký
            return None

