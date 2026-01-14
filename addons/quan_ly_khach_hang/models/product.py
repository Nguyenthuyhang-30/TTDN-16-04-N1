# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Product(models.Model):
    _name = 'qlkh.product'
    _description = 'Sản phẩm'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Tên sản phẩm',
        required=True,
        tracking=True,
        help='Tên sản phẩm'
    )
    
    product_type = fields.Selection([
        ('hard_drive', 'Ổ cứng'),
        ('ram', 'RAM'),
        ('cpu', 'CPU'),
        ('gpu', 'GPU'),
        ('motherboard', 'Bo mạch chủ'),
        ('other', 'Khác'),
    ], string='Loại sản phẩm',
        required=True,
        tracking=True,
        help='Loại sản phẩm'
    )
    
    brand = fields.Char(
        string='Thương hiệu',
        tracking=True,
        help='Thương hiệu sản phẩm'
    )
    
    unit_price = fields.Monetary(
        string='Đơn giá',
        currency_field='currency_id',
        required=True,
        tracking=True,
        help='Giá bán một đơn vị sản phẩm'
    )
    
    stock_quantity = fields.Integer(
        string='Số lượng tồn kho',
        default=0,
        tracking=True,
        help='Số lượng sản phẩm còn trong kho'
    )
    
    warranty_months = fields.Integer(
        string='Bảo hành (tháng)',
        default=0,
        tracking=True,
        help='Thời gian bảo hành (tính bằng tháng)'
    )
    
    total_inventory_value = fields.Monetary(
        string='Tổng giá trị kho',
        currency_field='currency_id',
        compute='_compute_total_inventory_value',
        store=True,
        help='Tổng giá trị tồn kho = Số lượng × Đơn giá'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    order_line_ids = fields.One2many(
        'qlkh.order.line',
        'product_id',
        string='Chi tiết đơn hàng',
        help='Danh sách chi tiết đơn hàng có sản phẩm này'
    )

    @api.depends('stock_quantity', 'unit_price')
    def _compute_total_inventory_value(self):
        """Tính tổng giá trị tồn kho"""
        for record in self:
            record.total_inventory_value = record.stock_quantity * record.unit_price

    @api.constrains('stock_quantity')
    def _check_stock_quantity(self):
        """Kiểm tra số lượng tồn kho không được âm"""
        for record in self:
            if record.stock_quantity < 0:
                raise ValidationError('Số lượng tồn kho không được âm!')

    @api.constrains('unit_price')
    def _check_unit_price(self):
        """Kiểm tra đơn giá phải dương"""
        for record in self:
            if record.unit_price < 0:
                raise ValidationError('Đơn giá phải lớn hơn hoặc bằng 0!')

