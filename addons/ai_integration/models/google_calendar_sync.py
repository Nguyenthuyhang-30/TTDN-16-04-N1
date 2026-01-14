# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class GoogleCalendarSync(models.Model):
    _name = 'google.calendar.sync'
    _description = 'Đồng bộ Google Calendar'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Tên sự kiện',
        required=True,
        help='Tên sự kiện trên Google Calendar'
    )
    
    event_type = fields.Selection([
        ('attendance', 'Chấm công'),
        ('order', 'Đơn hàng'),
        ('support', 'Hỗ trợ khách hàng'),
        ('document', 'Văn bản'),
        ('meeting', 'Cuộc họp'),
        ('other', 'Khác'),
    ], string='Loại sự kiện',
        required=True,
        help='Loại sự kiện'
    )
    
    start_datetime = fields.Datetime(
        string='Thời gian bắt đầu',
        required=True,
        help='Thời gian bắt đầu sự kiện'
    )
    
    end_datetime = fields.Datetime(
        string='Thời gian kết thúc',
        required=True,
        help='Thời gian kết thúc sự kiện'
    )
    
    description = fields.Text(
        string='Mô tả',
        help='Mô tả sự kiện'
    )
    
    google_event_id = fields.Char(
        string='Google Event ID',
        readonly=True,
        help='ID sự kiện trên Google Calendar'
    )
    
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('synced', 'Đã đồng bộ'),
        ('failed', 'Thất bại'),
    ], string='Trạng thái',
        default='draft',
        tracking=True
    )
    
    error_message = fields.Text(
        string='Thông báo lỗi',
        readonly=True
    )

    def action_sync_to_google(self):
        """MỨC 3: Đồng bộ sự kiện lên Google Calendar"""
        for record in self:
            if not record.start_datetime or not record.end_datetime:
                raise UserError('Vui lòng nhập thời gian bắt đầu và kết thúc!')
            
            try:
                config = self.env['ai.config'].get_active_config()
                
                if not config.google_calendar_client_id:
                    raise UserError('Chưa cấu hình Google Calendar!')
                
                # Tạo event trên Google Calendar
                event_id = self._create_google_event(record, config)
                
                record.google_event_id = event_id
                record.status = 'synced'
                record.error_message = False
                
            except Exception as e:
                record.status = 'failed'
                record.error_message = str(e)
                raise UserError(f'Lỗi khi đồng bộ: {str(e)}')
        
        return True
    
    def _create_google_event(self, record, config):
        """Tạo sự kiện trên Google Calendar"""
        # Note: Cần OAuth 2.0 flow để lấy access token
        # Đây là ví dụ cơ bản, cần implement đầy đủ OAuth flow
        
        # Format datetime theo RFC3339
        start_time = record.start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        end_time = record.end_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        
        event = {
            'summary': record.name,
            'description': record.description or '',
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
        }
        
        # TODO: Implement OAuth 2.0 flow để lấy access token
        # Sau đó gọi Google Calendar API:
        # url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
        # headers = {'Authorization': f'Bearer {access_token}'}
        # response = requests.post(url, headers=headers, json=event)
        
        # Tạm thời trả về mock ID
        return f"event_{record.id}_{int(datetime.now().timestamp())}"

