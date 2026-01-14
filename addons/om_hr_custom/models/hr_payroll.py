# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class HrPayroll(models.Model):
    _name = 'om.hr.payroll'
    _description = 'Bảng lương'
    _order = 'month desc, employee_id'

    name = fields.Char(
        string='Mã bảng lương',
        required=True,
        default=lambda self: self._generate_payroll_code(),
        help='Mã bảng lương tự động'
    )
    
    employee_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên',
        required=True,
        ondelete='cascade',
        help='Nhân viên được tính lương'
    )
    
    month = fields.Selection([
        ('01', 'Tháng 1'),
        ('02', 'Tháng 2'),
        ('03', 'Tháng 3'),
        ('04', 'Tháng 4'),
        ('05', 'Tháng 5'),
        ('06', 'Tháng 6'),
        ('07', 'Tháng 7'),
        ('08', 'Tháng 8'),
        ('09', 'Tháng 9'),
        ('10', 'Tháng 10'),
        ('11', 'Tháng 11'),
        ('12', 'Tháng 12'),
    ], string='Tháng',
        required=True,
        default=lambda self: datetime.now().strftime('%m'),
        help='Tháng tính lương'
    )
    
    year = fields.Integer(
        string='Năm',
        required=True,
        default=lambda self: datetime.now().year,
        help='Năm tính lương'
    )
    
    # Thông tin lương cơ bản
    basic_salary = fields.Monetary(
        string='Lương cơ bản',
        currency_field='currency_id',
        related='employee_id.salary',
        readonly=True,
        help='Lương cơ bản của nhân viên'
    )
    
    working_days_per_month = fields.Float(
        string='Số công chuẩn/tháng',
        default=26.0,
        help='Số công làm việc chuẩn trong 1 tháng (thường là 26 công)'
    )
    
    # Tính toán số công
    attendance_count = fields.Integer(
        string='Số công thực tế',
        compute='_compute_attendance_data',
        store=False,  # Không store để luôn tính lại khi mở form
        help='Số công đã làm trong tháng (dựa trên chấm công)'
    )
    
    total_worked_hours = fields.Float(
        string='Tổng giờ làm',
        compute='_compute_attendance_data',
        store=False,  # Không store để luôn tính lại khi mở form
        help='Tổng số giờ làm việc trong tháng'
    )
    
    # Thêm field để trigger compute khi chấm công thay đổi
    attendance_last_update = fields.Datetime(
        string='Cập nhật chấm công lần cuối',
        compute='_compute_attendance_last_update',
        store=False,
        help='Thời gian cập nhật chấm công lần cuối (để trigger tính lại)'
    )
    
    # Tính toán lương
    salary_per_day = fields.Monetary(
        string='Lương/ngày công',
        currency_field='currency_id',
        compute='_compute_salary',
        store=True,
        help='Lương tính trên 1 ngày công = Lương cơ bản / Số công chuẩn'
    )
    
    salary_from_attendance = fields.Monetary(
        string='Lương theo số công',
        currency_field='currency_id',
        compute='_compute_salary',
        store=True,
        help='Lương = Số công thực tế * (Lương cơ bản / Số công chuẩn)'
    )
    
    bonus = fields.Monetary(
        string='Thưởng',
        currency_field='currency_id',
        default=0.0,
        help='Số tiền thưởng'
    )
    
    penalty = fields.Monetary(
        string='Phạt (thủ công)',
        currency_field='currency_id',
        default=0.0,
        help='Số tiền phạt nhập thủ công'
    )
    
    # Phạt tự động từ đi muộn/về sớm
    late_violation_count = fields.Integer(
        string='Số lần đi muộn',
        compute='_compute_violation_penalty',
        store=False,
        help='Số lần đi muộn trong tháng'
    )
    
    early_violation_count = fields.Integer(
        string='Số lần về sớm',
        compute='_compute_violation_penalty',
        store=False,
        help='Số lần về sớm trong tháng'
    )
    
    total_violation_count = fields.Integer(
        string='Tổng số lần vi phạm',
        compute='_compute_violation_penalty',
        store=False,
        help='Tổng số lần đi muộn + về sớm'
    )
    
    violation_penalty_amount = fields.Monetary(
        string='Phạt tự động (đi muộn/về sớm)',
        currency_field='currency_id',
        compute='_compute_violation_penalty',
        store=True,
        help='Tiền phạt tự động = Số lần vi phạm * 50,000 VNĐ'
    )
    
    PENALTY_PER_VIOLATION = 50000.0  # Mức phạt mỗi lần vi phạm: 50,000 VNĐ
    
    total_salary = fields.Monetary(
        string='Tổng lương nhận',
        currency_field='currency_id',
        compute='_compute_salary',
        store=True,
        help='Tổng lương = Lương theo số công + Thưởng - Phạt'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('paid', 'Đã thanh toán'),
    ], string='Trạng thái',
        default='draft',
        required=True,
        help='Trạng thái bảng lương'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về bảng lương'
    )
    
    attendance_ids = fields.Many2many(
        'om.hr.attendance',
        string='Chấm công',
        compute='_compute_attendance_ids',
        help='Danh sách chấm công trong tháng'
    )

    @api.depends('employee_id', 'month', 'year')
    def _compute_attendance_ids(self):
        """Lấy danh sách chấm công trong tháng"""
        for record in self:
            if record.employee_id and record.month and record.year:
                # Tìm các chấm công trong tháng/năm (có giờ vào và giờ ra)
                attendances = self.env['om.hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '>=', f"{record.year}-{record.month}-01"),
                    ('date', '<', self._get_next_month_date(record.year, record.month)),
                    ('check_in', '!=', False),
                    ('check_out', '!=', False),
                ])
                record.attendance_ids = attendances
            else:
                record.attendance_ids = False

    @api.depends('employee_id', 'month', 'year')
    def _compute_attendance_data(self):
        """Tính số công và tổng giờ làm từ chấm công"""
        for record in self:
            if record.employee_id and record.month and record.year:
                # Tìm TẤT CẢ chấm công có cả giờ vào và giờ ra (không phụ thuộc vào trạng thái)
                start_date = f"{record.year}-{record.month}-01"
                end_date = self._get_next_month_date(record.year, record.month)
                
                all_attendances = self.env['om.hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '>=', start_date),
                    ('date', '<', end_date),
                    ('check_in', '!=', False),
                    ('check_out', '!=', False),
                ])
                
                # Số công thực tế = số chấm công có cả giờ vào và giờ ra (tính cả trạng thái Nháp)
                record.attendance_count = len(all_attendances)
                
                # Tổng giờ làm = tổng của TẤT CẢ chấm công có giờ vào và giờ ra
                if all_attendances:
                    record.total_worked_hours = sum(all_attendances.mapped('worked_hours'))
                else:
                    record.total_worked_hours = 0.0
            else:
                record.attendance_count = 0
                record.total_worked_hours = 0.0

    @api.depends('employee_id', 'month', 'year')
    def _compute_violation_penalty(self):
        """Tính số lần vi phạm và tiền phạt tự động"""
        for record in self:
            if record.employee_id and record.month and record.year:
                # Tìm các chấm công vi phạm trong tháng
                start_date = f"{record.year}-{record.month}-01"
                end_date = self._get_next_month_date(record.year, record.month)
                
                # Tìm chấm công đi muộn (is_late = True và có cả check_in và check_out)
                late_attendances = self.env['om.hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '>=', start_date),
                    ('date', '<', end_date),
                    ('check_in', '!=', False),
                    ('check_out', '!=', False),
                    ('is_late', '=', True),
                ])
                
                # Tìm chấm công về sớm (is_early = True và có cả check_in và check_out)
                early_attendances = self.env['om.hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '>=', start_date),
                    ('date', '<', end_date),
                    ('check_in', '!=', False),
                    ('check_out', '!=', False),
                    ('is_early', '=', True),
                ])
                
                record.late_violation_count = len(late_attendances)
                record.early_violation_count = len(early_attendances)
                record.total_violation_count = record.late_violation_count + record.early_violation_count
                
                # Tiền phạt tự động = Tổng số lần vi phạm * 50,000 VNĐ
                record.violation_penalty_amount = record.total_violation_count * self.PENALTY_PER_VIOLATION
            else:
                record.late_violation_count = 0
                record.early_violation_count = 0
                record.total_violation_count = 0
                record.violation_penalty_amount = 0.0

    @api.depends('basic_salary', 'working_days_per_month', 'attendance_count', 'bonus', 'penalty', 'violation_penalty_amount')
    def _compute_salary(self):
        """Tính toán lương"""
        for record in self:
            # Lương/ngày công = Lương cơ bản / Số công chuẩn
            if record.working_days_per_month > 0:
                record.salary_per_day = record.basic_salary / record.working_days_per_month
            else:
                record.salary_per_day = 0.0
            
            # Lương theo số công = Số công thực tế * Lương/ngày công
            record.salary_from_attendance = record.attendance_count * record.salary_per_day
            
            # Tổng phạt = Phạt thủ công + Phạt tự động (đi muộn/về sớm)
            total_penalty = record.penalty + record.violation_penalty_amount
            
            # Tổng lương = Lương theo số công + Thưởng - Tổng phạt
            record.total_salary = record.salary_from_attendance + record.bonus - total_penalty

    def _get_next_month_date(self, year, month):
        """Lấy ngày đầu tháng sau"""
        month_int = int(month)
        if month_int == 12:
            return f"{year + 1}-01-01"
        else:
            return f"{year}-{month_int + 1:02d}-01"

    @api.model
    def _generate_payroll_code(self):
        """Tự động tạo mã bảng lương"""
        sequence = self.env['ir.sequence'].next_by_code('hr.payroll.code') or 'BL0001'
        return sequence

    @api.model
    def create(self, vals):
        """Override create để tự động tính toán"""
        if not vals.get('name'):
            vals['name'] = self._generate_payroll_code()
        
        record = super(HrPayroll, self).create(vals)
        
        # Tự động tính lại khi tạo mới (sẽ tự động trigger compute)
        # Không cần gọi thủ công vì compute fields sẽ tự động chạy
        
        return record
    
    def read(self, fields=None, load='_classic_read'):
        """Override read để đảm bảo tính lại khi mở form"""
        result = super(HrPayroll, self).read(fields, load)
        # Trigger compute lại khi đọc record
        for record in self:
            record._compute_attendance_data()
            record._compute_violation_penalty()
            record._compute_salary()
        return result

    def action_confirm(self):
        """Xác nhận bảng lương"""
        for record in self:
            if record.status == 'draft':
                record.status = 'confirmed'
        return True

    def action_pay(self):
        """Đánh dấu đã thanh toán"""
        for record in self:
            if record.status != 'paid':
                record.status = 'paid'
        return True

    def action_recompute(self):
        """Tính lại bảng lương"""
        for record in self:
            # Invalidate cache để force compute lại
            record.invalidate_recordset([
                'attendance_count', 'total_worked_hours', 
                'late_violation_count', 'early_violation_count', 'total_violation_count', 'violation_penalty_amount',
                'salary_per_day', 'salary_from_attendance', 'total_salary'
            ])
            record._compute_attendance_data()
            record._compute_violation_penalty()
            record._compute_salary()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': 'Đã tính lại bảng lương thành công!',
                'type': 'success',
                'sticky': False,
            }
        }

