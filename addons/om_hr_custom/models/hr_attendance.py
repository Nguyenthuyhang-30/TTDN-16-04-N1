# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class HrAttendance(models.Model):
    _name = 'om.hr.attendance'
    _description = 'Chấm công'
    _order = 'date desc, check_in desc'

    name = fields.Char(
        string='Mã chấm công',
        required=True,
        default=lambda self: self._generate_attendance_code(),
        help='Mã chấm công tự động'
    )
    
    employee_id = fields.Many2one(
        'om.hr.employee',
        string='Nhân viên',
        required=True,
        ondelete='cascade',
        help='Nhân viên chấm công'
    )
    
    date = fields.Date(
        string='Ngày chấm công',
        required=True,
        default=fields.Date.today,
        help='Ngày chấm công'
    )
    
    # Giờ chuẩn
    standard_check_in = fields.Datetime(
        string='Giờ vào chuẩn',
        compute='_compute_standard_times',
        store=False,
        help='Giờ vào chuẩn: 8h30'
    )
    
    standard_check_out = fields.Datetime(
        string='Giờ ra chuẩn',
        compute='_compute_standard_times',
        store=False,
        help='Giờ ra chuẩn: 17h30'
    )
    
    standard_break_start = fields.Datetime(
        string='Giờ nghỉ bắt đầu chuẩn',
        compute='_compute_standard_times',
        store=False,
        help='Giờ nghỉ bắt đầu chuẩn: 12h30'
    )
    
    standard_break_end = fields.Datetime(
        string='Giờ nghỉ kết thúc chuẩn',
        compute='_compute_standard_times',
        store=False,
        help='Giờ nghỉ kết thúc chuẩn: 13h30'
    )
    
    check_in = fields.Datetime(
        string='Giờ vào',
        required=True,
        default=lambda self: self._get_default_check_in(),
        help='Thời gian vào làm'
    )
    
    check_out = fields.Datetime(
        string='Giờ ra',
        default=lambda self: self._get_default_check_out(),
        help='Thời gian ra về'
    )
    
    break_start = fields.Datetime(
        string='Giờ nghỉ bắt đầu',
        default=lambda self: self._get_default_break_start(),
        help='Thời gian bắt đầu nghỉ (mặc định: 12h30)'
    )
    
    break_end = fields.Datetime(
        string='Giờ nghỉ kết thúc',
        default=lambda self: self._get_default_break_end(),
        help='Thời gian kết thúc nghỉ (mặc định: 13h30)'
    )
    
    break_duration = fields.Float(
        string='Thời gian nghỉ (giờ)',
        compute='_compute_break_duration',
        store=True,
        help='Tổng thời gian nghỉ tính bằng giờ'
    )
    
    worked_hours = fields.Float(
        string='Số giờ làm',
        compute='_compute_worked_hours',
        store=True,
        help='Tổng số giờ làm việc (đã trừ giờ nghỉ)'
    )
    
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('checked_in', 'Đã vào'),
        ('checked_out', 'Đã ra'),
        ('absent', 'Vắng mặt'),
        ('late', 'Đi muộn'),
        ('early', 'Về sớm'),
    ], string='Trạng thái',
        default='draft',
        required=True,
        help='Trạng thái chấm công'
    )
    
    # Thông tin so sánh với giờ chuẩn
    is_late = fields.Boolean(
        string='Đi muộn',
        compute='_compute_late_early',
        store=True,
        help='Đi muộn so với giờ chuẩn (8h30)'
    )
    
    is_early = fields.Boolean(
        string='Về sớm',
        compute='_compute_late_early',
        store=True,
        help='Về sớm so với giờ chuẩn (17h30)'
    )
    
    late_minutes = fields.Float(
        string='Số phút đi muộn',
        compute='_compute_late_early',
        store=True,
        help='Số phút đi muộn so với giờ chuẩn'
    )
    
    early_minutes = fields.Float(
        string='Số phút về sớm',
        compute='_compute_late_early',
        store=True,
        help='Số phút về sớm so với giờ chuẩn'
    )
    
    late_warning = fields.Char(
        string='Cảnh báo đi muộn',
        compute='_compute_late_early',
        store=False,
        help='Thông báo cảnh báo nếu đi muộn'
    )
    
    early_warning = fields.Char(
        string='Cảnh báo về sớm',
        compute='_compute_late_early',
        store=False,
        help='Thông báo cảnh báo nếu về sớm'
    )
    
    notes = fields.Text(
        string='Ghi chú',
        help='Ghi chú về chấm công'
    )
    
    # Trường để hiển thị giờ nghỉ dạng text (ví dụ: 12h30-13h30)
    break_time_display = fields.Char(
        string='Giờ nghỉ',
        compute='_compute_break_time_display',
        help='Hiển thị giờ nghỉ dạng text (ví dụ: 12h30-13h30)'
    )
    
    # Trường để hiển thị giờ vào/ra/nghỉ (ví dụ: 8h30 | 17h30 | 12h30-13h30)
    time_summary = fields.Char(
        string='Tóm tắt giờ',
        compute='_compute_time_summary',
        help='Tóm tắt: Giờ vào | Giờ ra | Giờ nghỉ (ví dụ: 8h30 | 17h30 | 12h30-13h30)'
    )

    @api.depends('date')
    def _compute_standard_times(self):
        """Tính toán giờ chuẩn dựa trên ngày chấm công"""
        for record in self:
            if record.date:
                # Giờ vào chuẩn: 8h30
                record.standard_check_in = datetime.combine(record.date, datetime.min.time().replace(hour=8, minute=30))
                # Giờ ra chuẩn: 17h30
                record.standard_check_out = datetime.combine(record.date, datetime.min.time().replace(hour=17, minute=30))
                # Giờ nghỉ bắt đầu chuẩn: 12h30
                record.standard_break_start = datetime.combine(record.date, datetime.min.time().replace(hour=12, minute=30))
                # Giờ nghỉ kết thúc chuẩn: 13h30
                record.standard_break_end = datetime.combine(record.date, datetime.min.time().replace(hour=13, minute=30))
            else:
                record.standard_check_in = False
                record.standard_check_out = False
                record.standard_break_start = False
                record.standard_break_end = False

    @api.model
    def _get_default_check_in(self):
        """Lấy giờ vào mặc định: 8h30 của ngày hôm nay"""
        today = fields.Date.today()
        return datetime.combine(today, datetime.min.time().replace(hour=8, minute=30))

    @api.model
    def _get_default_check_out(self):
        """Lấy giờ ra mặc định: 17h30 của ngày hôm nay"""
        today = fields.Date.today()
        return datetime.combine(today, datetime.min.time().replace(hour=17, minute=30))

    @api.model
    def _get_default_break_start(self):
        """Lấy giờ nghỉ bắt đầu mặc định: 12h30 của ngày hôm nay"""
        today = fields.Date.today()
        return datetime.combine(today, datetime.min.time().replace(hour=12, minute=30))

    @api.model
    def _get_default_break_end(self):
        """Lấy giờ nghỉ kết thúc mặc định: 13h30 của ngày hôm nay"""
        today = fields.Date.today()
        return datetime.combine(today, datetime.min.time().replace(hour=13, minute=30))

    @api.depends('break_start', 'break_end')
    def _compute_break_duration(self):
        """Tính thời gian nghỉ"""
        for record in self:
            if record.break_start and record.break_end:
                delta = record.break_end - record.break_start
                record.break_duration = delta.total_seconds() / 3600.0
            else:
                record.break_duration = 0.0

    @api.depends('check_in', 'check_out', 'break_duration')
    def _compute_worked_hours(self):
        """Tính số giờ làm việc (tổng giờ - giờ nghỉ)"""
        for record in self:
            if record.check_in and record.check_out:
                delta = record.check_out - record.check_in
                total_hours = delta.total_seconds() / 3600.0
                record.worked_hours = total_hours - record.break_duration
            else:
                record.worked_hours = 0.0

    @api.depends('break_start', 'break_end')
    def _compute_break_time_display(self):
        """Hiển thị giờ nghỉ dạng text"""
        for record in self:
            if record.break_start and record.break_end:
                # Convert sang timezone của user trước khi format
                start_dt = fields.Datetime.context_timestamp(record, record.break_start)
                end_dt = fields.Datetime.context_timestamp(record, record.break_end)
                start_time = start_dt.time().strftime('%Hh%M')
                end_time = end_dt.time().strftime('%Hh%M')
                record.break_time_display = f"{start_time}-{end_time}"
            else:
                record.break_time_display = ""

    @api.depends('check_in', 'check_out', 'break_start', 'break_end')
    def _compute_time_summary(self):
        """Tính toán tóm tắt giờ: Giờ vào | Giờ ra | Giờ nghỉ (ví dụ: 8h30 | 17h30 | 12h30-13h30)"""
        for record in self:
            parts = []
            
            # Giờ vào - Convert sang timezone của user
            if record.check_in:
                check_in_dt = fields.Datetime.context_timestamp(record, record.check_in)
                check_in_time = check_in_dt.time().strftime('%Hh%M')
                parts.append(check_in_time)
            else:
                parts.append("--")
            
            # Giờ ra - Convert sang timezone của user
            if record.check_out:
                check_out_dt = fields.Datetime.context_timestamp(record, record.check_out)
                check_out_time = check_out_dt.time().strftime('%Hh%M')
                parts.append(check_out_time)
            else:
                parts.append("--")
            
            # Giờ nghỉ - Convert sang timezone của user
            if record.break_start and record.break_end:
                break_start_dt = fields.Datetime.context_timestamp(record, record.break_start)
                break_end_dt = fields.Datetime.context_timestamp(record, record.break_end)
                break_start_time = break_start_dt.time().strftime('%Hh%M')
                break_end_time = break_end_dt.time().strftime('%Hh%M')
                parts.append(f"{break_start_time}-{break_end_time}")
            else:
                parts.append("--")
            
            # Format: Giờ vào | Giờ ra | Giờ nghỉ
            record.time_summary = " | ".join(parts)

    @api.depends('check_in', 'check_out', 'date')
    def _compute_late_early(self):
        """Tính toán đi muộn/về sớm so với giờ chuẩn"""
        for record in self:
            record.is_late = False
            record.is_early = False
            record.late_minutes = 0.0
            record.early_minutes = 0.0
            record.late_warning = ""
            record.early_warning = ""
            
            # Ngưỡng cảnh báo: chỉ cảnh báo nếu muộn/về sớm >= 1 phút
            THRESHOLD_MINUTES = 1.0
            
            if record.check_in and record.date:
                # Convert check_in sang timezone của user
                check_in_user = fields.Datetime.context_timestamp(record, record.check_in)
                # Tính giờ vào chuẩn: 8h30 (theo timezone của user)
                standard_check_in = datetime.combine(check_in_user.date(), datetime.min.time().replace(hour=8, minute=30))
                # So sánh giờ vào với giờ chuẩn (chỉ so sánh phần giờ, không so sánh ngày)
                check_in_time = check_in_user.time()
                standard_time = standard_check_in.time()
                
                # Tính số phút muộn
                check_in_dt = datetime.combine(check_in_user.date(), check_in_time)
                standard_dt = datetime.combine(check_in_user.date(), standard_time)
                delta = check_in_dt - standard_dt
                late_minutes = delta.total_seconds() / 60.0
                
                # Chỉ cảnh báo nếu muộn >= 1 phút
                if late_minutes >= THRESHOLD_MINUTES:
                    record.is_late = True
                    record.late_minutes = late_minutes
                    # Tạo cảnh báo
                    hours = int(late_minutes // 60)
                    minutes = int(late_minutes % 60)
                    if hours > 0:
                        record.late_warning = f"⚠️ Đi muộn {hours} giờ {minutes} phút (sau 8h30)"
                    else:
                        record.late_warning = f"⚠️ Đi muộn {minutes} phút (sau 8h30)"
            
            if record.check_out and record.date:
                # Convert check_out sang timezone của user
                check_out_user = fields.Datetime.context_timestamp(record, record.check_out)
                # Tính giờ ra chuẩn: 17h30 (theo timezone của user)
                standard_check_out = datetime.combine(check_out_user.date(), datetime.min.time().replace(hour=17, minute=30))
                # So sánh giờ ra với giờ chuẩn (chỉ so sánh phần giờ, không so sánh ngày)
                check_out_time = check_out_user.time()
                standard_time = standard_check_out.time()
                
                # Tính số phút về sớm
                check_out_dt = datetime.combine(check_out_user.date(), check_out_time)
                standard_dt = datetime.combine(check_out_user.date(), standard_time)
                delta = standard_dt - check_out_dt
                early_minutes = delta.total_seconds() / 60.0
                
                # Chỉ cảnh báo nếu về sớm >= 1 phút
                if early_minutes >= THRESHOLD_MINUTES:
                    record.is_early = True
                    record.early_minutes = early_minutes
                    # Tạo cảnh báo
                    hours = int(early_minutes // 60)
                    minutes = int(early_minutes % 60)
                    if hours > 0:
                        record.early_warning = f"⚠️ Về sớm {hours} giờ {minutes} phút (trước 17h30)"
                    else:
                        record.early_warning = f"⚠️ Về sớm {minutes} phút (trước 17h30)"


    @api.model
    def _generate_attendance_code(self):
        """Tự động tạo mã chấm công"""
        sequence = self.env['ir.sequence'].next_by_code('hr.attendance.code') or 'CC0001'
        return sequence

    @api.model
    def create(self, vals):
        """Override create để tự động cập nhật trạng thái và bảng lương"""
        if not vals.get('name'):
            vals['name'] = self._generate_attendance_code()
        
        # Tự động điền giờ nghỉ nếu chưa có
        if vals.get('date') and not vals.get('break_start'):
            date_obj = fields.Date.from_string(vals['date']) if isinstance(vals['date'], str) else vals['date']
            vals['break_start'] = datetime.combine(date_obj, datetime.min.time().replace(hour=12, minute=30))
        
        if vals.get('date') and not vals.get('break_end'):
            date_obj = fields.Date.from_string(vals['date']) if isinstance(vals['date'], str) else vals['date']
            vals['break_end'] = datetime.combine(date_obj, datetime.min.time().replace(hour=13, minute=30))
        
        record = super(HrAttendance, self).create(vals)
        
        # Tự động cập nhật bảng lương nếu chấm công có cả giờ vào và giờ ra
        if record.check_in and record.check_out:
            record._update_payroll(record)
        
        return record

    def write(self, vals):
        """Override write để tự động cập nhật trạng thái và bảng lương"""
        result = super(HrAttendance, self).write(vals)
        
        # Tự động cập nhật trạng thái khi thay đổi giờ vào/ra
        for record in self:
            need_update_status = False
            if vals.get('check_in') or vals.get('check_out') or vals.get('date'):
                need_update_status = True
            
            if need_update_status:
                # Ngưỡng cảnh báo: chỉ đánh dấu muộn/về sớm nếu >= 1 phút
                THRESHOLD_MINUTES = 1.0
                
                if record.check_in and not record.check_out:
                    # Kiểm tra đi muộn
                    if record.date:
                        # Convert sang timezone của user
                        check_in_user = fields.Datetime.context_timestamp(record, record.check_in)
                        standard_check_in = datetime.combine(check_in_user.date(), datetime.min.time().replace(hour=8, minute=30))
                        check_in_time = check_in_user.time()
                        standard_time = standard_check_in.time()
                        
                        # Tính số phút muộn
                        check_in_dt = datetime.combine(check_in_user.date(), check_in_time)
                        standard_dt = datetime.combine(check_in_user.date(), standard_time)
                        delta = check_in_dt - standard_dt
                        late_minutes = delta.total_seconds() / 60.0
                        
                        # Chỉ đánh dấu muộn nếu >= 1 phút
                        if late_minutes >= THRESHOLD_MINUTES:
                            record.status = 'late'
                        else:
                            record.status = 'checked_in'
                    else:
                        record.status = 'checked_in'
                elif record.check_in and record.check_out:
                    # Kiểm tra đi muộn/về sớm
                    if record.date:
                        # Convert sang timezone của user
                        check_in_user = fields.Datetime.context_timestamp(record, record.check_in)
                        check_out_user = fields.Datetime.context_timestamp(record, record.check_out)
                        
                        standard_check_in = datetime.combine(check_in_user.date(), datetime.min.time().replace(hour=8, minute=30))
                        standard_check_out = datetime.combine(check_out_user.date(), datetime.min.time().replace(hour=17, minute=30))
                        
                        check_in_time = check_in_user.time()
                        check_out_time = check_out_user.time()
                        standard_in_time = standard_check_in.time()
                        standard_out_time = standard_check_out.time()
                        
                        # Tính số phút về sớm
                        check_out_dt = datetime.combine(check_out_user.date(), check_out_time)
                        standard_dt = datetime.combine(check_out_user.date(), standard_out_time)
                        delta_early = standard_dt - check_out_dt
                        early_minutes = delta_early.total_seconds() / 60.0
                        
                        # Tính số phút đi muộn
                        check_in_dt = datetime.combine(check_in_user.date(), check_in_time)
                        standard_dt = datetime.combine(check_in_user.date(), standard_in_time)
                        delta_late = check_in_dt - standard_dt
                        late_minutes = delta_late.total_seconds() / 60.0
                        
                        # Ưu tiên về sớm trước, sau đó mới đi muộn
                        if early_minutes >= THRESHOLD_MINUTES:
                            record.status = 'early'
                        elif late_minutes >= THRESHOLD_MINUTES:
                            record.status = 'late'
                        else:
                            record.status = 'checked_out'
                    else:
                        record.status = 'checked_out'
            
            # Tự động cập nhật bảng lương khi chấm công có cả giờ vào và giờ ra (bất kể status)
            if record.check_in and record.check_out and (vals.get('check_out') or vals.get('check_in') or vals.get('date')):
                self._update_payroll(record)
        
        return result
    
    def _update_payroll(self, attendance):
        """Cập nhật bảng lương khi có chấm công mới hoặc thay đổi"""
        if not attendance.employee_id or not attendance.date:
            return
        
        # Tìm bảng lương của nhân viên trong tháng/năm của chấm công
        year = attendance.date.year
        month = attendance.date.strftime('%m')
        
        payrolls = self.env['om.hr.payroll'].search([
            ('employee_id', '=', attendance.employee_id.id),
            ('year', '=', year),
            ('month', '=', month),
        ])
        
        # Tự động tính lại cho tất cả bảng lương liên quan
        for payroll in payrolls:
            # Invalidate cache để force compute lại
            payroll.invalidate_recordset([
                'attendance_count', 'total_worked_hours',
                'late_violation_count', 'early_violation_count', 'total_violation_count', 'violation_penalty_amount'
            ])
            payroll._compute_attendance_data()
            payroll._compute_violation_penalty()
            payroll._compute_salary()

    def action_check_in(self):
        """Hành động chấm công vào"""
        self.ensure_one()
        vals = {
            'check_in': fields.Datetime.now(),
        }
        
        # Tự động điền giờ nghỉ nếu chưa có
        if self.date and not self.break_start:
            vals['break_start'] = datetime.combine(self.date, datetime.min.time().replace(hour=12, minute=30))
        if self.date and not self.break_end:
            vals['break_end'] = datetime.combine(self.date, datetime.min.time().replace(hour=13, minute=30))
        
        self.write(vals)
        return True

    def action_check_out(self):
        """Hành động chấm công ra"""
        self.ensure_one()
        if not self.check_in:
            raise UserError("Vui lòng chấm công vào trước!")
        
        vals = {
            'check_out': fields.Datetime.now(),
        }
        
        # Tự động điền giờ nghỉ nếu chưa có
        if self.date and not self.break_start:
            vals['break_start'] = datetime.combine(self.date, datetime.min.time().replace(hour=12, minute=30))
        if self.date and not self.break_end:
            vals['break_end'] = datetime.combine(self.date, datetime.min.time().replace(hour=13, minute=30))
        
        self.write(vals)
        return True
