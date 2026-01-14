# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerDashboard(models.TransientModel):
    _name = 'qlkh.customer.dashboard'
    _description = 'Dashboard Quản lý khách hàng'

    # Thống kê khách hàng
    total_customers = fields.Integer(
        string='Tổng số khách hàng',
        compute='_compute_statistics',
        help='Tổng số khách hàng trong hệ thống'
    )
    
    new_customers = fields.Integer(
        string='Khách hàng mới',
        compute='_compute_statistics',
        help='Số khách hàng mới'
    )
    
    old_customers = fields.Integer(
        string='Khách hàng cũ',
        compute='_compute_statistics',
        help='Số khách hàng cũ'
    )
    
    vip_customers = fields.Integer(
        string='Khách hàng VIP',
        compute='_compute_statistics',
        help='Số khách hàng VIP'
    )
    
    # Thống kê phân loại
    high_potential = fields.Integer(
        string='Tiềm năng cao',
        compute='_compute_statistics',
        help='Số khách hàng tiềm năng cao'
    )
    
    low_potential = fields.Integer(
        string='Tiềm năng thấp',
        compute='_compute_statistics',
        help='Số khách hàng tiềm năng thấp'
    )
    
    regular_customers = fields.Integer(
        string='Khách hàng thường',
        compute='_compute_statistics',
        help='Số khách hàng thường'
    )
    
    # Thống kê đơn hàng
    total_orders = fields.Integer(
        string='Tổng đơn hàng',
        compute='_compute_statistics',
        help='Tổng số đơn hàng'
    )
    
    draft_orders = fields.Integer(
        string='Đơn hàng nháp',
        compute='_compute_statistics',
        help='Số đơn hàng nháp'
    )
    
    confirmed_orders = fields.Integer(
        string='Đơn hàng mới',
        compute='_compute_statistics',
        help='Số đơn hàng đã xác nhận'
    )
    
    completed_orders = fields.Integer(
        string='Đơn hàng hoàn thành',
        compute='_compute_statistics',
        help='Số đơn hàng đã hoàn thành'
    )
    
    # Thống kê doanh thu
    total_revenue = fields.Monetary(
        string='Tổng doanh thu',
        currency_field='currency_id',
        compute='_compute_statistics',
        help='Tổng doanh thu từ các đơn hàng hoàn thành'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    # Field trigger để computed fields được tính toán
    compute_trigger = fields.Boolean(
        string='Trigger',
        default=True,
        help='Field trigger để computed fields được tính toán'
    )
    
    # Thống kê hỗ trợ
    total_support = fields.Integer(
        string='Tổng yêu cầu hỗ trợ',
        compute='_compute_statistics',
        help='Tổng số yêu cầu hỗ trợ'
    )
    
    pending_support = fields.Integer(
        string='Đang xử lý',
        compute='_compute_statistics',
        help='Số yêu cầu hỗ trợ đang xử lý'
    )
    
    resolved_support = fields.Integer(
        string='Đã giải quyết',
        compute='_compute_statistics',
        help='Số yêu cầu hỗ trợ đã giải quyết'
    )
    
    # Dữ liệu cho biểu đồ (JSON fields) - không store vì là TransientModel
    chart_customer_status_data = fields.Text(
        string='Dữ liệu biểu đồ trạng thái khách hàng',
        compute='_compute_statistics',
        store=False,
        help='Dữ liệu JSON cho biểu đồ tròn trạng thái khách hàng'
    )
    
    chart_classification_data = fields.Text(
        string='Dữ liệu biểu đồ phân loại',
        compute='_compute_statistics',
        store=False,
        help='Dữ liệu JSON cho biểu đồ tròn phân loại khách hàng'
    )
    
    chart_orders_data = fields.Text(
        string='Dữ liệu biểu đồ đơn hàng',
        compute='_compute_statistics',
        store=False,
        help='Dữ liệu JSON cho biểu đồ cột đơn hàng'
    )
    
    chart_revenue_data = fields.Text(
        string='Dữ liệu biểu đồ doanh thu',
        compute='_compute_statistics',
        store=False,
        help='Dữ liệu JSON cho biểu đồ đường doanh thu'
    )
    
    chart_combined_data = fields.Text(
        string='Dữ liệu biểu đồ kết hợp',
        compute='_compute_statistics',
        store=False,
        help='Dữ liệu JSON cho biểu đồ kết hợp bar + line'
    )
    
    chart_achievement_data = fields.Text(
        string='Dữ liệu biểu đồ thành tích',
        compute='_compute_statistics',
        store=False,
        help='Dữ liệu JSON cho donut chart với phần trăm'
    )
    
    chart_progress_data = fields.Text(
        string='Dữ liệu progress bars',
        compute='_compute_statistics',
        store=False,
        help='Dữ liệu JSON cho progress bars'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create để tính toán statistics"""
        records = super(CustomerDashboard, self).create(vals_list)
        for record in records:
            # Force compute statistics
            record._compute_statistics()
        return records

    @api.depends('compute_trigger')
    def _compute_statistics(self):
        """Tính toán các thống kê và dữ liệu biểu đồ"""
        import json
        import datetime
        
        for record in self:
            try:
                Customer = record.env['qlkh.customer']
                Order = record.env['qlkh.order']
                Support = record.env['qlkh.customer.support']
                
                # Khách hàng - Khởi tạo tất cả biến trước
                total = 0
                new = 0
                old = 0
                vip = 0
                high = 0
                low = 0
                regular = 0
                total_orders = 0
                draft_orders = 0
                confirmed_orders = 0
                completed_orders = 0
                total_revenue = 0.0
                total_support = 0
                pending_support = 0
                resolved_support = 0
                
                # Tính toán giá trị
                total = Customer.search_count([])
                new = Customer.search_count([('status', '=', 'new')])
                old = Customer.search_count([('status', '=', 'old')])
                vip = Customer.search_count([('status', '=', 'vip')])
                
                # Phân loại
                high = Customer.search_count([('classification', '=', 'high_potential')])
                low = Customer.search_count([('classification', '=', 'low_potential')])
                regular = Customer.search_count([('classification', '=', 'regular')])
                
                # Đơn hàng
                total_orders = Order.search_count([])
                draft_orders = Order.search_count([('state', '=', 'draft')])
                confirmed_orders = Order.search_count([('state', '=', 'confirmed')])
                completed_orders = Order.search_count([('state', '=', 'completed')])
                
                # Doanh thu
                completed_order_records = Order.search([('state', '=', 'completed')])
                total_revenue = sum(completed_order_records.mapped('total_amount')) or 0.0
                
                # Hỗ trợ
                total_support = Support.search_count([])
                pending_support = Support.search_count([('state', '=', 'pending')])
                resolved_support = Support.search_count([('state', '=', 'resolved')])
                
                # Cập nhật giá trị
                record.total_customers = total
                record.new_customers = new
                record.old_customers = old
                record.vip_customers = vip
                record.high_potential = high
                record.low_potential = low
                record.regular_customers = regular
                record.total_orders = total_orders
                record.draft_orders = draft_orders
                record.confirmed_orders = confirmed_orders
                record.completed_orders = completed_orders
                record.total_revenue = total_revenue
                record.total_support = total_support
                record.pending_support = pending_support
                record.resolved_support = resolved_support
                
                # Dữ liệu cho biểu đồ
                
                # Biểu đồ tròn - Trạng thái khách hàng
                record.chart_customer_status_data = json.dumps({
                    'labels': ['Mới', 'Cũ', 'VIP'],
                    'data': [new, old, vip],
                    'colors': ['#4facfe', '#43e97b', '#fa709a']
                })
                
                # Biểu đồ tròn - Phân loại khách hàng
                record.chart_classification_data = json.dumps({
                    'labels': ['Tiềm năng cao', 'Tiềm năng thấp', 'Khách hàng thường'],
                    'data': [high, low, regular],
                    'colors': ['#11998e', '#f093fb', '#4facfe']
                })
                
                # Biểu đồ cột - Đơn hàng
                record.chart_orders_data = json.dumps({
                    'labels': ['Nháp', 'Mới', 'Hoàn thành'],
                    'data': [draft_orders, confirmed_orders, completed_orders],
                    'colors': ['#f093fb', '#fa709a', '#11998e']
                })
                
                # Biểu đồ đường - Doanh thu (giả lập 6 tháng gần nhất)
                months = []
                revenue_data = []
                for i in range(5, -1, -1):
                    month_date = datetime.datetime.now() - datetime.timedelta(days=30*i)
                    months.append(month_date.strftime('%m/%Y'))
                    # Giả lập dữ liệu dựa trên doanh thu hiện tại
                    revenue_data.append(float(total_revenue) * (0.7 + 0.3 * (6-i)/6))
                
                record.chart_revenue_data = json.dumps({
                    'labels': months,
                    'data': revenue_data,
                    'color': '#667eea'
                })
                
                # Biểu đồ kết hợp (Bar + Line với 2 trục Y) - Đơn hàng và Doanh thu
                order_trend = []
                revenue_trend = []
                combined_labels = []
                for i in range(11, -1, -1):
                    day_date = datetime.datetime.now() - datetime.timedelta(days=i)
                    combined_labels.append(day_date.strftime('%d/%m'))
                    # Giả lập dữ liệu đơn hàng
                    order_trend.append(int(total_orders * (0.5 + 0.5 * (12-i)/12)))
                    # Giả lập dữ liệu doanh thu
                    revenue_trend.append(float(total_revenue) * (0.5 + 0.5 * (12-i)/12) / 1000)  # Chia 1000 để scale
                
                record.chart_combined_data = json.dumps({
                    'labels': combined_labels,
                    'barData': {
                        'label': 'Đơn hàng',
                        'data': order_trend,
                        'color': '#4facfe'
                    },
                    'lineData': {
                        'label': 'Doanh thu (x1000)',
                        'data': revenue_trend,
                        'color': '#43e97b'
                    }
                })
                
                # Dữ liệu cho donut chart với phần trăm
                total_target = 1000  # Mục tiêu giả định
                achievement_percent = min(100, int((total / total_target) * 100) if total_target > 0 else 0)
                record.chart_achievement_data = json.dumps({
                    'percent': achievement_percent,
                    'current': total,
                    'target': total_target,
                    'color': '#667eea'
                })
                
                # Dữ liệu cho progress bars
                record.chart_progress_data = json.dumps({
                    'income': min(100, int((total_revenue / (total_target * 1000)) * 100) if total_target > 0 else 0),
                    'orders': min(100, int((total_orders / total_target) * 100) if total_target > 0 else 0),
                    'customers': achievement_percent,
                    'support': min(100, int((resolved_support / max(1, total_support)) * 100) if total_support > 0 else 0)
                })
            except Exception as e:
                # Xử lý lỗi - đặt giá trị mặc định
                record.total_customers = 0
                record.new_customers = 0
                record.old_customers = 0
                record.vip_customers = 0
                record.high_potential = 0
                record.low_potential = 0
                record.regular_customers = 0
                record.total_orders = 0
                record.draft_orders = 0
                record.confirmed_orders = 0
                record.completed_orders = 0
                record.total_revenue = 0.0
                record.total_support = 0
                record.pending_support = 0
                record.resolved_support = 0
                record.chart_customer_status_data = json.dumps({'labels': [], 'data': [], 'colors': []})
                record.chart_classification_data = json.dumps({'labels': [], 'data': [], 'colors': []})
                record.chart_orders_data = json.dumps({'labels': [], 'data': [], 'colors': []})
                record.chart_revenue_data = json.dumps({'labels': [], 'data': [], 'color': ''})
                record.chart_combined_data = json.dumps({'labels': [], 'barData': {}, 'lineData': {}})
                record.chart_achievement_data = json.dumps({'percent': 0, 'current': 0, 'target': 0, 'color': ''})
                record.chart_progress_data = json.dumps({'income': 0, 'orders': 0, 'customers': 0, 'support': 0})
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error("Error computing statistics: %s", str(e))

    def action_view_customers(self):
        """Mở danh sách khách hàng"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Khách hàng',
            'res_model': 'qlkh.customer',
            'view_mode': 'tree,form',
            'domain': [],
            'context': {},
        }
    
    def action_view_orders(self):
        """Mở danh sách đơn hàng"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn hàng',
            'res_model': 'qlkh.order',
            'view_mode': 'tree,form',
            'domain': [],
            'context': {},
        }
    
    def action_view_vip_customers(self):
        """Mở danh sách khách hàng VIP"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Khách hàng VIP',
            'res_model': 'qlkh.customer',
            'view_mode': 'tree,form',
            'domain': [('status', '=', 'vip')],
            'context': {},
        }
    
    def get_chart_data(self):
        """Method để lấy dữ liệu biểu đồ - đảm bảo computed fields được tính toán"""
        self.ensure_one()
        # Đảm bảo computed fields được tính toán
        self._compute_statistics()
        return {
            'chart_customer_status_data': self.chart_customer_status_data,
            'chart_classification_data': self.chart_classification_data,
            'chart_orders_data': self.chart_orders_data,
            'chart_revenue_data': self.chart_revenue_data,
            'chart_combined_data': self.chart_combined_data,
            'chart_achievement_data': self.chart_achievement_data,
            'chart_progress_data': self.chart_progress_data,
        }

