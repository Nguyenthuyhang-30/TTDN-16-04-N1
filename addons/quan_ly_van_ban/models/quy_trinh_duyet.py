# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class DocumentApproval(models.Model):
    _name = 'om.document.approval'
    _description = 'Quy trình duyệt văn bản'
    _order = 'sequence, id'

    name = fields.Char(
        string='Tên bước duyệt',
        compute='_compute_name',
        store=True,
        help='Tên bước duyệt'
    )
    
    document_id = fields.Many2one(
        'om.document.outgoing',
        string='Văn bản',
        required=True,
        ondelete='cascade',
        help='Văn bản cần duyệt'
    )
    
    approver_id = fields.Many2one(
        'om.hr.employee',
        string='Người duyệt',
        required=True,
        help='Nhân viên duyệt văn bản'
    )
    
    role = fields.Selection([
        ('employee', 'Nhân viên'),
        ('manager', 'Trưởng phòng'),
        ('director', 'Giám đốc'),
    ], string='Vai trò',
        required=True,
        help='Vai trò của người duyệt'
    )
    
    sequence = fields.Integer(
        string='Thứ tự',
        default=1,
        required=True,
        help='Thứ tự duyệt (1 = duyệt đầu tiên)'
    )
    
    state = fields.Selection([
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('skipped', 'Bỏ qua'),
    ], string='Trạng thái',
        default='pending',
        required=True,
        help='Trạng thái duyệt'
    )
    
    approval_date = fields.Datetime(
        string='Ngày duyệt',
        help='Thời gian duyệt văn bản'
    )
    
    comment = fields.Text(
        string='Nhận xét',
        help='Nhận xét của người duyệt'
    )
    
    deadline = fields.Datetime(
        string='Hạn duyệt',
        help='Thời hạn phải duyệt'
    )
    
    is_overdue = fields.Boolean(
        string='Quá hạn',
        compute='_compute_is_overdue',
        help='Bước duyệt có quá hạn không'
    )

    @api.depends('document_id', 'approver_id', 'sequence')
    def _compute_name(self):
        """Tự động tạo tên bước duyệt"""
        for record in self:
            if record.document_id and record.approver_id:
                doc_name = record.document_id.name or record.document_id.number
                approver_name = record.approver_id.name
                role_name = dict(record._fields['role'].selection).get(record.role, '')
                record.name = f"{doc_name} - {role_name} - {approver_name}"
            else:
                record.name = 'Bước duyệt'

    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        """Tính toán trạng thái quá hạn"""
        now = fields.Datetime.now()
        for record in self:
            if record.deadline and record.state == 'pending':
                record.is_overdue = record.deadline < now
            else:
                record.is_overdue = False

    def action_approve(self):
        """Duyệt văn bản"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError('Chỉ có thể duyệt các bước đang chờ duyệt!')
        
        # Kiểm tra quyền của người duyệt
        if not self.approver_id:
            raise UserError('Chưa chọn người duyệt!')
        
        # Kiểm tra trạng thái nhân viên
        if self.approver_id.employee_status != 'working':
            raise UserError(f'Nhân viên {self.approver_id.name} không đang làm việc, không thể duyệt!')
        
        # Kiểm tra quyền duyệt
        if self.role == 'director':
            # Giám đốc cần quyền phê duyệt
            if not self.approver_id.check_permission('final_approve'):
                raise UserError(f'Nhân viên {self.approver_id.name} không có quyền phê duyệt!')
        else:
            # Trưởng phòng và nhân viên cần quyền duyệt
            if not self.approver_id.check_permission('approve'):
                raise UserError(f'Nhân viên {self.approver_id.name} không có quyền duyệt!')
        
        # Kiểm tra các bước trước đã được duyệt chưa
        previous_approvals = self.env['om.document.approval'].search([
            ('document_id', '=', self.document_id.id),
            ('sequence', '<', self.sequence),
            ('state', '!=', 'approved')
        ])
        if previous_approvals:
            raise UserError('Vui lòng duyệt các bước trước đó trước!')
        
        self.write({
            'state': 'approved',
            'approval_date': fields.Datetime.now(),
        })
        
        # Kiểm tra xem đã duyệt hết chưa
        all_approvals = self.env['om.document.approval'].search([
            ('document_id', '=', self.document_id.id)
        ])
        if all(approval.state == 'approved' for approval in all_approvals):
            # Tất cả đã duyệt, chuyển văn bản sang trạng thái "Đã duyệt"
            self.document_id.write({'status': 'approved'})
        
        return True

    def action_reject(self):
        """Từ chối văn bản"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError('Chỉ có thể từ chối các bước đang chờ duyệt!')
        
        self.write({
            'state': 'rejected',
            'approval_date': fields.Datetime.now(),
        })
        
        # Chuyển văn bản về trạng thái nháp
        self.document_id.write({'status': 'draft'})
        
        return True

    def action_skip(self):
        """Bỏ qua bước duyệt"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError('Chỉ có thể bỏ qua các bước đang chờ duyệt!')
        
        self.write({
            'state': 'skipped',
        })
        
        return True

