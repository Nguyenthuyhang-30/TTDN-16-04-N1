# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class HrDashboard(models.TransientModel):
    _name = 'om.hr.dashboard'
    _description = 'Dashboard Quản lý nhân sự'

    # Thống kê tổng quan
    total_employees = fields.Integer(
        string='Tổng số nhân viên',
        compute='_compute_statistics',
        help='Tổng số nhân viên trong hệ thống'
    )
    
    working_employees = fields.Integer(
        string='Đang làm việc',
        compute='_compute_statistics',
        help='Số nhân viên đang làm việc'
    )
    
    resigned_employees = fields.Integer(
        string='Nghỉ việc',
        compute='_compute_statistics',
        help='Số nhân viên đã nghỉ việc'
    )
    
    suspended_employees = fields.Integer(
        string='Tạm nghỉ',
        compute='_compute_statistics',
        help='Số nhân viên tạm nghỉ'
    )
    
    # Thống kê theo vai trò
    employee_count = fields.Integer(
        string='Nhân viên',
        compute='_compute_statistics',
        help='Số nhân viên kinh doanh'
    )
    
    manager_count = fields.Integer(
        string='Trưởng phòng',
        compute='_compute_statistics',
        help='Số trưởng phòng'
    )
    
    director_count = fields.Integer(
        string='Giám đốc',
        compute='_compute_statistics',
        help='Số giám đốc'
    )
    
    # Thống kê theo phòng ban
    total_departments = fields.Integer(
        string='Tổng số phòng ban',
        compute='_compute_statistics',
        help='Tổng số phòng ban'
    )
    
    # Thống kê quyền
    can_draft_count = fields.Integer(
        string='Có quyền soạn thảo',
        compute='_compute_statistics',
        help='Số nhân viên có quyền soạn thảo'
    )
    
    can_approve_count = fields.Integer(
        string='Có quyền duyệt',
        compute='_compute_statistics',
        help='Số nhân viên có quyền duyệt'
    )
    
    can_final_approve_count = fields.Integer(
        string='Có quyền phê duyệt',
        compute='_compute_statistics',
        help='Số nhân viên có quyền phê duyệt'
    )
    
    # Field trigger để computed fields được tính toán
    compute_trigger = fields.Boolean(
        string='Trigger',
        default=True,
        help='Field trigger để computed fields được tính toán'
    )
    
    # Dữ liệu cho biểu đồ (JSON fields)
    chart_employee_status_data = fields.Text(
        string='Dữ liệu biểu đồ trạng thái nhân viên',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ tròn trạng thái nhân viên'
    )
    
    chart_role_data = fields.Text(
        string='Dữ liệu biểu đồ vai trò',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ tròn vai trò'
    )
    
    chart_permissions_data = fields.Text(
        string='Dữ liệu biểu đồ phân quyền',
        compute='_compute_statistics',
        help='Dữ liệu JSON cho biểu đồ cột phân quyền'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create để tính toán statistics"""
        records = super(HrDashboard, self).create(vals_list)
        for record in records:
            record._compute_statistics()
        return records

    @api.depends('compute_trigger')
    def _compute_statistics(self):
        """Tính toán các thống kê"""
        Employee = self.env['om.hr.employee']
        Department = self.env['om.hr.department']
        
        # Tổng số nhân viên
        total = Employee.search_count([])
        
        # Theo trạng thái
        working = Employee.search_count([('employee_status', '=', 'working')])
        resigned = Employee.search_count([('employee_status', '=', 'resigned')])
        suspended = Employee.search_count([('employee_status', '=', 'suspended')])
        
        # Theo vai trò
        employee_role = Employee.search_count([('role', '=', 'employee')])
        manager_role = Employee.search_count([('role', '=', 'manager')])
        director_role = Employee.search_count([('role', '=', 'director')])
        
        # Phòng ban
        departments = Department.search_count([('active', '=', True)])
        
        # Quyền
        can_draft = Employee.search_count([('can_draft', '=', True)])
        can_approve = Employee.search_count([('can_approve', '=', True)])
        can_final_approve = Employee.search_count([('can_final_approve', '=', True)])
        
        # Cập nhật giá trị
        self.total_employees = total
        self.working_employees = working
        self.resigned_employees = resigned
        self.suspended_employees = suspended
        self.employee_count = employee_role
        self.manager_count = manager_role
        self.director_count = director_role
        self.total_departments = departments
        self.can_draft_count = can_draft
        self.can_approve_count = can_approve
        self.can_final_approve_count = can_final_approve
        
        # Dữ liệu cho biểu đồ
        import json
        # Biểu đồ tròn - Trạng thái nhân viên
        self.chart_employee_status_data = json.dumps({
            'labels': ['Đang làm việc', 'Nghỉ việc', 'Tạm nghỉ'],
            'data': [working, resigned, suspended],
            'colors': ['#11998e', '#f093fb', '#fa709a']
        })
        
        # Biểu đồ tròn - Vai trò
        self.chart_role_data = json.dumps({
            'labels': ['Nhân viên', 'Trưởng phòng', 'Giám đốc'],
            'data': [employee_role, manager_role, director_role],
            'colors': ['#4facfe', '#43e97b', '#fa709a']
        })
        
        # Biểu đồ cột - Phân quyền
        self.chart_permissions_data = json.dumps({
            'labels': ['Soạn thảo', 'Duyệt', 'Phê duyệt'],
            'data': [can_draft, can_approve, can_final_approve],
            'colors': ['#667eea', '#11998e', '#fa709a']
        })

    def action_view_employees(self):
        """Mở danh sách nhân viên"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nhân viên',
            'res_model': 'om.hr.employee',
            'view_mode': 'tree,form',
            'domain': [],
            'context': {},
        }
    
    def action_view_working_employees(self):
        """Mở danh sách nhân viên đang làm việc"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nhân viên đang làm việc',
            'res_model': 'om.hr.employee',
            'view_mode': 'tree,form',
            'domain': [('employee_status', '=', 'working')],
            'context': {},
        }
    
    def action_view_departments(self):
        """Mở danh sách phòng ban"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phòng ban',
            'res_model': 'om.hr.department',
            'view_mode': 'tree,form',
            'domain': [('active', '=', True)],
            'context': {},
        }
    
    def get_chart_data(self):
        """Method để lấy dữ liệu biểu đồ"""
        self.ensure_one()
        self._compute_statistics()
        return {
            'chart_employee_status_data': self.chart_employee_status_data,
            'chart_role_data': self.chart_role_data,
            'chart_permissions_data': self.chart_permissions_data,
        }

