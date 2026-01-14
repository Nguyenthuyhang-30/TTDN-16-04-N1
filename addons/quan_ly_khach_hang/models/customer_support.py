# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class CustomerSupport(models.Model):
    _name = 'qlkh.customer.support'
    _description = 'Hỗ trợ khách hàng'
    _order = 'start_time desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    customer_id = fields.Many2one(
        'qlkh.customer',
        string='Khách hàng',
        required=True,
        tracking=True,
        help='Khách hàng cần hỗ trợ'
    )
    
    contact_method = fields.Selection([
        ('email', 'Email'),
        ('phone', 'Điện thoại'),
        ('message', 'Nhắn tin'),
        ('in_person', 'Trực tiếp'),
    ], string='Phương thức liên lạc',
        required=True,
        default='email',
        tracking=True,
        help='Phương thức khách hàng liên hệ'
    )
    
    start_time = fields.Datetime(
        string='Thời gian bắt đầu',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help='Thời gian bắt đầu hỗ trợ'
    )
    
    end_time = fields.Datetime(
        string='Thời gian kết thúc',
        tracking=True,
        help='Thời gian kết thúc hỗ trợ'
    )
    
    support_days = fields.Integer(
        string='Số ngày hỗ trợ',
        compute='_compute_support_days',
        store=True,
        help='Số ngày hỗ trợ (từ thời gian bắt đầu đến kết thúc)'
    )
    
    state = fields.Selection([
        ('new', 'Mới'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái',
        default='new',
        tracking=True,
        help='Trạng thái yêu cầu hỗ trợ'
    )
    
    assigned_staff_id = fields.Many2one(
        'res.users',
        string='Nhân viên phụ trách (User)',
        tracking=True,
        default=lambda self: self.env.user,
        help='Nhân viên được phân công xử lý (User)'
    )
    
    # MỨC 1: Liên kết với HR Employee (dữ liệu gốc)
    assigned_employee_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên phụ trách',
        tracking=True,
        help='Nhân viên được phân công xử lý (từ module HR)'
    )
    
    customer_rating = fields.Selection([
        ('1', '1 - Rất không hài lòng'),
        ('2', '2 - Không hài lòng'),
        ('3', '3 - Bình thường'),
        ('4', '4 - Hài lòng'),
        ('5', '5 - Rất hài lòng'),
    ], string='Điểm đánh giá từ khách hàng',
        tracking=True,
        help='Đánh giá của khách hàng về dịch vụ hỗ trợ'
    )
    
    rating_score = fields.Integer(
        string='Điểm đánh giá',
        compute='_compute_rating_score',
        store=True,
        help='Điểm đánh giá dạng số (1-5)'
    )
    
    description = fields.Text(
        string='Mô tả',
        help='Mô tả vấn đề hoặc yêu cầu hỗ trợ'
    )
    
    solution = fields.Text(
        string='Giải pháp',
        help='Giải pháp đã áp dụng'
    )

    @api.depends('customer_rating')
    def _compute_rating_score(self):
        """Chuyển đổi đánh giá từ selection sang số"""
        for record in self:
            if record.customer_rating:
                record.rating_score = int(record.customer_rating)
            else:
                record.rating_score = 0

    @api.depends('start_time', 'end_time')
    def _compute_support_days(self):
        """Tính số ngày hỗ trợ"""
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.support_days = delta.days
            else:
                record.support_days = 0

    def action_start(self):
        """Bắt đầu xử lý"""
        for record in self:
            record.state = 'in_progress'
            if not record.start_time:
                record.start_time = fields.Datetime.now()
        
        return True

    def action_resolve(self):
        """Giải quyết yêu cầu"""
        for record in self:
            record.state = 'resolved'
            if not record.end_time:
                record.end_time = fields.Datetime.now()
        
        return True

    def action_cancel(self):
        """Hủy yêu cầu"""
        for record in self:
            record.state = 'cancelled'
        
        return True

    @api.constrains('end_time', 'start_time')
    def _check_time(self):
        """Kiểm tra thời gian kết thúc phải sau thời gian bắt đầu"""
        for record in self:
            if record.end_time and record.start_time:
                if record.end_time < record.start_time:
                    raise ValidationError('Thời gian kết thúc phải sau thời gian bắt đầu!')

