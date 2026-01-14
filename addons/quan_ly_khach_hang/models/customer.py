# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Customer(models.Model):
    _name = 'qlkh.customer'
    _description = 'Khách hàng'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Tên khách hàng',
        required=True,
        tracking=True,
        help='Họ và tên khách hàng'
    )
    
    phone = fields.Char(
        string='Số điện thoại',
        tracking=True,
        help='Số điện thoại liên hệ'
    )
    
    email = fields.Char(
        string='Email',
        tracking=True,
        help='Địa chỉ email'
    )
    
    company = fields.Char(
        string='Công ty',
        tracking=True,
        help='Tên công ty'
    )
    
    classification = fields.Selection([
        ('high_potential', 'Tiềm năng cao'),
        ('low_potential', 'Tiềm năng thấp'),
        ('regular', 'Khách hàng thường'),
    ], string='Phân loại khách hàng',
        default='regular',
        tracking=True,
        help='Phân loại khách hàng'
    )
    
    status = fields.Selection([
        ('new', 'Mới'),
        ('old', 'Cũ'),
        ('vip', 'VIP'),
    ], string='Trạng thái khách hàng',
        default='new',
        tracking=True,
        help='Trạng thái khách hàng'
    )
    
    purchase_count = fields.Integer(
        string='Số lần mua hàng',
        compute='_compute_purchase_count',
        store=True,
        help='Tổng số lần mua hàng (tự động tính từ đơn hàng)'
    )
    
    total_spent = fields.Monetary(
        string='Tổng tiền đã chi tiêu',
        currency_field='currency_id',
        compute='_compute_total_spent',
        store=True,
        help='Tổng số tiền khách hàng đã chi tiêu (tự động tính từ đơn hàng)'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    order_ids = fields.One2many(
        'qlkh.order',
        'customer_id',
        string='Đơn hàng',
        help='Danh sách đơn hàng của khách hàng'
    )
    
    support_ids = fields.One2many(
        'qlkh.customer.support',
        'customer_id',
        string='Hỗ trợ',
        help='Danh sách yêu cầu hỗ trợ'
    )
    
    create_date = fields.Datetime(
        string='Ngày tạo',
        readonly=True,
        help='Ngày tạo bản ghi'
    )

    @api.model
    def default_get(self, fields_list):
        """Set giá trị mặc định khi tạo mới"""
        res = super(Customer, self).default_get(fields_list)
        if 'purchase_count' in fields_list:
            res['purchase_count'] = 0
        if 'total_spent' in fields_list:
            res['total_spent'] = 0.0
        return res

    @api.depends('order_ids', 'order_ids.state')
    def _compute_purchase_count(self):
        """Tính số lần mua hàng"""
        for record in self:
            # Đếm số đơn hàng đã hoàn thành hoặc đã xác nhận
            if record.order_ids:
                completed_orders = record.order_ids.filtered(
                    lambda o: o.state in ['confirmed', 'completed']
                )
                record.purchase_count = len(completed_orders)
            else:
                record.purchase_count = 0

    @api.depends('order_ids', 'order_ids.total_amount', 'order_ids.state')
    def _compute_total_spent(self):
        """Tính tổng tiền đã chi tiêu"""
        for record in self:
            # Tính tổng tiền từ các đơn hàng đã hoàn thành
            if record.order_ids:
                completed_orders = record.order_ids.filtered(
                    lambda o: o.state == 'completed'
                )
                record.total_spent = sum(completed_orders.mapped('total_amount')) or 0.0
            else:
                record.total_spent = 0.0

