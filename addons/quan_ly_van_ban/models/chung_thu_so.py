# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date


class DigitalCertificate(models.Model):
    _name = 'om.digital.certificate'
    _description = 'Chứng thư số'
    _order = 'employee_id, expiry_date desc'

    name = fields.Char(
        string='Tên chứng thư',
        required=True,
        help='Tên chứng thư số'
    )
    
    employee_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên',
        required=True,
        help='Nhân viên sở hữu chứng thư số'
    )
    
    certificate_serial = fields.Char(
        string='Số seri chứng thư',
        required=True,
        help='Số seri của chứng thư số'
    )
    
    certificate_type = fields.Selection([
        ('usb_token', 'USB Token'),
        ('remote', 'Ký số từ xa'),
        ('image_otp', 'Ký hình ảnh + OTP'),
    ], string='Loại chứng thư',
        required=True,
        default='usb_token',
        help='Loại chứng thư số'
    )
    
    issuer = fields.Char(
        string='Nhà cung cấp',
        help='Nhà cung cấp chứng thư số (VNPT-CA, Viettel-CA, FPT-CA...)'
    )
    
    issue_date = fields.Date(
        string='Ngày cấp',
        required=True,
        default=fields.Date.today,
        help='Ngày cấp chứng thư số'
    )
    
    expiry_date = fields.Date(
        string='Ngày hết hạn',
        required=True,
        help='Ngày hết hạn chứng thư số'
    )
    
    is_active = fields.Boolean(
        string='Đang hoạt động',
        default=True,
        compute='_compute_is_active',
        store=True,
        help='Chứng thư số có đang hoạt động không'
    )
    
    certificate_file = fields.Binary(
        string='File chứng thư',
        help='File chứng thư số (nếu có)'
    )
    
    certificate_filename = fields.Char(
        string='Tên file chứng thư',
        help='Tên file chứng thư số'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về chứng thư số'
    )
    
    signature_count = fields.Integer(
        string='Số lần đã ký',
        compute='_compute_signature_count',
        help='Tổng số lần đã sử dụng chứng thư này để ký'
    )

    @api.depends('expiry_date')
    def _compute_is_active(self):
        """Tính toán trạng thái hoạt động dựa trên ngày hết hạn"""
        today = date.today()
        for record in self:
            record.is_active = record.expiry_date >= today if record.expiry_date else False

    def _compute_signature_count(self):
        """Đếm số lần đã sử dụng chứng thư để ký"""
        for record in self:
            record.signature_count = self.env['om.document.signature'].search_count([
                ('certificate_id', '=', record.id),
                ('state', '=', 'signed')
            ])

    @api.constrains('expiry_date', 'issue_date')
    def _check_dates(self):
        """Kiểm tra ngày hết hạn phải sau ngày cấp"""
        for record in self:
            if record.expiry_date and record.issue_date:
                if record.expiry_date <= record.issue_date:
                    raise ValidationError('Ngày hết hạn phải sau ngày cấp!')

