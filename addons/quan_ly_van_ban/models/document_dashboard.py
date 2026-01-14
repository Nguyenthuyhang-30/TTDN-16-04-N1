# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class DocumentDashboard(models.TransientModel):
    _name = 'om.document.dashboard'
    _description = 'Dashboard Quản lý văn bản'

    # Thống kê văn bản đi
    total_outgoing = fields.Integer(
        string='Tổng văn bản đi',
        compute='_compute_statistics',
        help='Tổng số văn bản đi'
    )
    
    draft_outgoing = fields.Integer(
        string='Văn bản nháp',
        compute='_compute_statistics',
        help='Số văn bản đi ở trạng thái nháp'
    )
    
    pending_approval_outgoing = fields.Integer(
        string='Chờ duyệt',
        compute='_compute_statistics',
        help='Số văn bản đi chờ duyệt'
    )
    
    approved_outgoing = fields.Integer(
        string='Đã duyệt',
        compute='_compute_statistics',
        help='Số văn bản đi đã duyệt'
    )
    
    signed_outgoing = fields.Integer(
        string='Đã ký',
        compute='_compute_statistics',
        help='Số văn bản đi đã ký'
    )
    
    sent_outgoing = fields.Integer(
        string='Đã gửi',
        compute='_compute_statistics',
        help='Số văn bản đi đã gửi'
    )
    
    # Thống kê văn bản đến
    total_incoming = fields.Integer(
        string='Tổng văn bản đến',
        compute='_compute_statistics',
        help='Tổng số văn bản đến'
    )
    
    draft_incoming = fields.Integer(
        string='Văn bản đến nháp',
        compute='_compute_statistics',
        help='Số văn bản đến ở trạng thái nháp'
    )
    
    processing_incoming = fields.Integer(
        string='Đang xử lý',
        compute='_compute_statistics',
        help='Số văn bản đến đang xử lý'
    )
    
    completed_incoming = fields.Integer(
        string='Hoàn thành',
        compute='_compute_statistics',
        help='Số văn bản đến đã hoàn thành'
    )
    
    # Thống kê quy trình duyệt
    pending_approvals = fields.Integer(
        string='Chờ duyệt',
        compute='_compute_statistics',
        help='Số bước duyệt đang chờ'
    )
    
    approved_approvals = fields.Integer(
        string='Đã duyệt',
        compute='_compute_statistics',
        help='Số bước duyệt đã duyệt'
    )
    
    rejected_approvals = fields.Integer(
        string='Từ chối',
        compute='_compute_statistics',
        help='Số bước duyệt bị từ chối'
    )
    
    # Thống kê chữ ký số
    pending_signatures = fields.Integer(
        string='Chờ ký',
        compute='_compute_statistics',
        help='Số chữ ký số chờ ký'
    )
    
    signed_signatures = fields.Integer(
        string='Đã ký',
        compute='_compute_statistics',
        help='Số chữ ký số đã ký'
    )
    
    total_certificates = fields.Integer(
        string='Tổng chứng thư số',
        compute='_compute_statistics',
        help='Tổng số chứng thư số'
    )
    
    # Field trigger để computed fields được tính toán
    compute_trigger = fields.Boolean(
        string='Trigger',
        default=True,
        help='Field trigger để computed fields được tính toán'
    )
    
    # Dữ liệu cho biểu đồ (JSON fields)
    chart_outgoing_status_data = fields.Text(
        string='Dữ liệu biểu đồ văn bản đi',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ cột văn bản đi'
    )
    
    chart_incoming_status_data = fields.Text(
        string='Dữ liệu biểu đồ văn bản đến',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ cột văn bản đến'
    )
    
    chart_approval_data = fields.Text(
        string='Dữ liệu biểu đồ quy trình duyệt',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ tròn quy trình duyệt'
    )
    
    chart_signature_data = fields.Text(
        string='Dữ liệu biểu đồ chữ ký số',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ tròn chữ ký số'
    )
    
    chart_trend_data = fields.Text(
        string='Dữ liệu biểu đồ xu hướng',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ đường xu hướng'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create để tính toán statistics"""
        records = super(DocumentDashboard, self).create(vals_list)
        for record in records:
            record._compute_statistics()
        return records

    @api.depends('compute_trigger')
    def _compute_statistics(self):
        """Tính toán các thống kê"""
        Outgoing = self.env['om.document.outgoing']
        Incoming = self.env['om.document.incoming']
        Approval = self.env['om.document.approval']
        Signature = self.env['om.document.signature']
        Certificate = self.env['om.digital.certificate']
        
        # Văn bản đi
        total_out = Outgoing.search_count([])
        draft_out = Outgoing.search_count([('status', '=', 'draft')])
        pending_approval_out = Outgoing.search_count([('status', '=', 'pending_approval')])
        approved_out = Outgoing.search_count([('status', '=', 'approved')])
        signed_out = Outgoing.search_count([('status', '=', 'signed')])
        sent_out = Outgoing.search_count([('status', '=', 'sent')])
        
        # Văn bản đến
        total_in = Incoming.search_count([])
        draft_in = Incoming.search_count([('status', '=', 'draft')])
        processing_in = Incoming.search_count([('status', '=', 'processing')])
        completed_in = Incoming.search_count([('status', '=', 'completed')])
        
        # Quy trình duyệt
        pending_app = Approval.search_count([('state', '=', 'pending')])
        approved_app = Approval.search_count([('state', '=', 'approved')])
        rejected_app = Approval.search_count([('state', '=', 'rejected')])
        
        # Chữ ký số
        pending_sig = Signature.search_count([('state', '=', 'pending')])
        signed_sig = Signature.search_count([('state', '=', 'signed')])
        total_cert = Certificate.search_count([('is_active', '=', True)])
        
        # Cập nhật giá trị
        self.total_outgoing = total_out
        self.draft_outgoing = draft_out
        self.pending_approval_outgoing = pending_approval_out
        self.approved_outgoing = approved_out
        self.signed_outgoing = signed_out
        self.sent_outgoing = sent_out
        self.total_incoming = total_in
        self.draft_incoming = draft_in
        self.processing_incoming = processing_in
        self.completed_incoming = completed_in
        self.pending_approvals = pending_app
        self.approved_approvals = approved_app
        self.rejected_approvals = rejected_app
        self.pending_signatures = pending_sig
        self.signed_signatures = signed_sig
        self.total_certificates = total_cert
        
        # Dữ liệu cho biểu đồ
        import json
        import datetime
        
        # Biểu đồ cột - Văn bản đi
        self.chart_outgoing_status_data = json.dumps({
            'labels': ['Nháp', 'Chờ duyệt', 'Đã duyệt', 'Đã ký', 'Đã gửi'],
            'data': [draft_out, pending_approval_out, approved_out, signed_out, sent_out],
            'colors': ['#f093fb', '#fa709a', '#4facfe', '#43e97b', '#11998e']
        })
        
        # Biểu đồ cột - Văn bản đến
        self.chart_incoming_status_data = json.dumps({
            'labels': ['Nháp', 'Đang xử lý', 'Hoàn thành'],
            'data': [draft_in, processing_in, completed_in],
            'colors': ['#f093fb', '#fa709a', '#11998e']
        })
        
        # Biểu đồ tròn - Quy trình duyệt
        self.chart_approval_data = json.dumps({
            'labels': ['Chờ duyệt', 'Đã duyệt', 'Từ chối'],
            'data': [pending_app, approved_app, rejected_app],
            'colors': ['#fa709a', '#11998e', '#f093fb']
        })
        
        # Biểu đồ tròn - Chữ ký số
        self.chart_signature_data = json.dumps({
            'labels': ['Chờ ký', 'Đã ký'],
            'data': [pending_sig, signed_sig],
            'colors': ['#fa709a', '#11998e']
        })
        
        # Biểu đồ đường - Xu hướng (giả lập 6 tháng)
        months = []
        outgoing_trend = []
        incoming_trend = []
        for i in range(5, -1, -1):
            month_date = datetime.datetime.now() - datetime.timedelta(days=30*i)
            months.append(month_date.strftime('%m/%Y'))
            # Giả lập dữ liệu
            outgoing_trend.append(int(total_out * (0.6 + 0.4 * (6-i)/6)))
            incoming_trend.append(int(total_in * (0.6 + 0.4 * (6-i)/6)))
        
        self.chart_trend_data = json.dumps({
            'labels': months,
            'datasets': [
                {'label': 'Văn bản đi', 'data': outgoing_trend, 'color': '#667eea'},
                {'label': 'Văn bản đến', 'data': incoming_trend, 'color': '#11998e'}
            ]
        })

    def action_view_outgoing(self):
        """Mở danh sách văn bản đi"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Văn bản đi',
            'res_model': 'om.document.outgoing',
            'view_mode': 'tree,form',
            'domain': [],
            'context': {},
        }
    
    def action_view_incoming(self):
        """Mở danh sách văn bản đến"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Văn bản đến',
            'res_model': 'om.document.incoming',
            'view_mode': 'tree,form',
            'domain': [],
            'context': {},
        }
    
    def action_view_pending_approvals(self):
        """Mở danh sách quy trình duyệt chờ duyệt"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quy trình duyệt chờ duyệt',
            'res_model': 'om.document.approval',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'pending')],
            'context': {},
        }
    
    def get_chart_data(self):
        """Method để lấy dữ liệu biểu đồ"""
        self.ensure_one()
        self._compute_statistics()
        return {
            'chart_outgoing_status_data': self.chart_outgoing_status_data,
            'chart_incoming_status_data': self.chart_incoming_status_data,
            'chart_approval_data': self.chart_approval_data,
            'chart_signature_data': self.chart_signature_data,
            'chart_trend_data': self.chart_trend_data,
        }

