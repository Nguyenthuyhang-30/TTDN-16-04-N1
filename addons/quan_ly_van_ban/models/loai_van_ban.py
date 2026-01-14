# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class DocumentType(models.Model):
    _name = 'om.document.type'
    _description = 'Loại văn bản'
    _order = 'name'

    name = fields.Char(
        string='Tên loại văn bản',
        required=True,
        help='Tên loại văn bản (ví dụ: Công văn, Quyết định, Thông báo...)'
    )
    
    code = fields.Char(
        string='Mã loại',
        help='Mã loại văn bản'
    )
    
    description = fields.Text(
        string='Mô tả',
        help='Mô tả về loại văn bản'
    )
    
    active = fields.Boolean(
        string='Hoạt động',
        default=True,
        help='Nếu bỏ chọn, loại văn bản này sẽ bị ẩn'
    )
    
    incoming_count = fields.Integer(
        string='Số văn bản đến',
        compute='_compute_document_count'
    )
    
    outgoing_count = fields.Integer(
        string='Số văn bản đi',
        compute='_compute_document_count'
    )

    @api.depends('name')
    def _compute_document_count(self):
        """Đếm số lượng văn bản đến và đi theo loại"""
        for record in self:
            record.incoming_count = self.env['om.document.incoming'].search_count([
                ('document_type_id', '=', record.id)
            ])
            record.outgoing_count = self.env['om.document.outgoing'].search_count([
                ('document_type_id', '=', record.id)
            ])

