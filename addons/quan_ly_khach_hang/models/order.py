# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Order(models.Model):
    _name = 'qlkh.order'
    _description = 'Đơn hàng'
    _order = 'order_date desc, name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Đơn hàng',
        required=True,
        readonly=True,
        default=lambda self: self._generate_order_code(),
        help='Mã đơn hàng'
    )
    
    order_date = fields.Datetime(
        string='Ngày đặt hàng',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help='Ngày và giờ đặt hàng'
    )
    
    customer_id = fields.Many2one(
        'qlkh.customer',
        string='Khách hàng',
        required=True,
        tracking=True,
        help='Khách hàng đặt hàng'
    )
    
    # MỨC 1: Liên kết với HR Employee (dữ liệu gốc)
    salesperson_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên bán hàng',
        tracking=True,
        help='Nhân viên phụ trách đơn hàng này'
    )
    
    order_line_ids = fields.One2many(
        'qlkh.order.line',
        'order_id',
        string='Chi tiết đơn hàng',
        help='Danh sách sản phẩm trong đơn hàng'
    )
    
    total_amount = fields.Monetary(
        string='Thành tiền',
        currency_field='currency_id',
        compute='_compute_total_amount',
        store=True,
        help='Tổng tiền của đơn hàng'
    )
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Mới'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái',
        default='draft',
        tracking=True,
        help='Trạng thái đơn hàng'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về đơn hàng'
    )

    @api.depends('order_line_ids', 'order_line_ids.subtotal')
    def _compute_total_amount(self):
        """Tính tổng tiền đơn hàng"""
        for record in self:
            record.total_amount = sum(record.order_line_ids.mapped('subtotal'))

    @api.model
    def _generate_order_code(self):
        """Tự động tạo mã đơn hàng"""
        sequence = self.env['ir.sequence'].next_by_code('qlkh.order.code') or 'DHH00001'
        return sequence

    def action_confirm(self):
        """Xác nhận đơn hàng"""
        for record in self:
            if not record.order_line_ids:
                raise UserError('Đơn hàng phải có ít nhất một sản phẩm!')
            
            # Kiểm tra tồn kho
            for line in record.order_line_ids:
                if line.product_id.stock_quantity < line.quantity:
                    raise UserError(
                        f'Sản phẩm {line.product_id.name} không đủ tồn kho! '
                        f'Còn lại: {line.product_id.stock_quantity}, cần: {line.quantity}'
                    )
            
            # Trừ tồn kho
            for line in record.order_line_ids:
                line.product_id.stock_quantity -= line.quantity
            
            record.state = 'confirmed'
            # Cập nhật số lần mua hàng của khách hàng
            record.customer_id._compute_purchase_count()
            
            # MỨC 2: Tự động tạo văn bản đi (hợp đồng/hóa đơn) khi đơn hàng được xác nhận
            self._auto_create_document_outgoing(record)
        
        return True
    
    def _auto_create_document_outgoing(self, order):
        """MỨC 2: Tự động tạo văn bản đi khi đơn hàng được xác nhận"""
        # Kiểm tra xem module quan_ly_van_ban có được cài đặt không
        if 'om.document.outgoing' not in self.env:
            return False
        
        # Tìm loại văn bản "Hợp đồng" hoặc "Hóa đơn"
        doc_type = self.env['om.document.type'].search([
            ('name', 'ilike', 'Hợp đồng')
        ], limit=1)
        
        if not doc_type:
            # Nếu không có, tạo loại văn bản mặc định
            doc_type = self.env['om.document.type'].create({
                'name': 'Hợp đồng',
                'code': 'HD',
            })
        
        # Tạo văn bản đi tự động
        document = self.env['om.document.outgoing'].create({
            'name': f'HĐ-{order.name}',
            'document_type_id': doc_type.id,
            'date_sent': fields.Date.today(),
            'date_document': fields.Date.today(),
            'sender': self.env.company.name or 'Công ty',
            'recipient': order.customer_id.name,
            'subject': f'Hợp đồng đơn hàng {order.name} - Tổng tiền: {order.total_amount:,.0f} VNĐ',
            'status': 'draft',
            'priority': 'normal',
            'customer_id': order.customer_id.id,
            'order_id': order.id,
            'assigned_employee_id': order.salesperson_id.id if order.salesperson_id else False,
            'notes': f'Tự động tạo từ đơn hàng {order.name}',
        })
        
        return document

    def action_complete(self):
        """Hoàn thành đơn hàng"""
        for record in self:
            if record.state != 'confirmed':
                raise UserError('Chỉ có thể hoàn thành đơn hàng đã xác nhận!')
            record.state = 'completed'
            # Cập nhật tổng tiền đã chi tiêu của khách hàng
            record.customer_id._compute_total_spent()
        
        return True

    def action_cancel(self):
        """Hủy đơn hàng"""
        for record in self:
            if record.state == 'completed':
                raise UserError('Không thể hủy đơn hàng đã hoàn thành!')
            
            # Trả lại tồn kho nếu đã xác nhận
            if record.state == 'confirmed':
                for line in record.order_line_ids:
                    line.product_id.stock_quantity += line.quantity
            
            record.state = 'cancelled'
        
        return True

    def action_draft(self):
        """Quay lại trạng thái nháp"""
        for record in self:
            if record.state == 'completed':
                raise UserError('Không thể quay lại nháp từ đơn hàng đã hoàn thành!')
            record.state = 'draft'
        
        return True


class OrderLine(models.Model):
    _name = 'qlkh.order.line'
    _description = 'Chi tiết đơn hàng'
    _order = 'order_id, id'

    order_id = fields.Many2one(
        'qlkh.order',
        string='Đơn hàng',
        required=True,
        ondelete='cascade',
        help='Đơn hàng'
    )
    
    product_id = fields.Many2one(
        'qlkh.product',
        string='Tên sản phẩm',
        required=True,
        help='Sản phẩm'
    )
    
    quantity = fields.Integer(
        string='Số lượng',
        required=True,
        default=1,
        help='Số lượng sản phẩm'
    )
    
    unit_price = fields.Monetary(
        string='Đơn giá',
        currency_field='currency_id',
        required=True,
        help='Giá một đơn vị sản phẩm'
    )
    
    subtotal = fields.Monetary(
        string='Thành tiền',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True,
        help='Thành tiền = Số lượng × Đơn giá'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='order_id.currency_id',
        store=True
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        """Tính thành tiền"""
        for record in self:
            record.subtotal = record.quantity * record.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Khi chọn sản phẩm, tự động điền đơn giá"""
        if self.product_id:
            self.unit_price = self.product_id.unit_price

    @api.constrains('quantity')
    def _check_quantity(self):
        """Kiểm tra số lượng phải dương"""
        for record in self:
            if record.quantity <= 0:
                raise ValidationError('Số lượng phải lớn hơn 0!')

