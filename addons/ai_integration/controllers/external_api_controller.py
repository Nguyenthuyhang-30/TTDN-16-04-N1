# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import requests
import json

class ExternalAPIController(http.Controller):
    
    @http.route('/ai/send_telegram', type='json', auth='user')
    def send_telegram_notification(self, message, **kwargs):
        """MỨC 3: Gửi thông báo qua Telegram"""
        config = request.env['ai.config'].get_active_config()
        
        if not config.telegram_bot_token or not config.telegram_chat_id:
            return {'success': False, 'message': 'Chưa cấu hình Telegram'}
        
        try:
            url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': config.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            return {'success': True, 'message': 'Đã gửi thông báo Telegram'}
        except Exception as e:
            return {'success': False, 'message': f'Lỗi: {str(e)}'}
    
    @http.route('/ai/send_zalo', type='json', auth='user')
    def send_zalo_notification(self, message, **kwargs):
        """MỨC 3: Gửi thông báo qua Zalo"""
        config = request.env['ai.config'].get_active_config()
        
        if not config.zalo_oa_id or not config.zalo_access_token:
            return {'success': False, 'message': 'Chưa cấu hình Zalo'}
        
        try:
            url = "https://openapi.zalo.me/v2.0/oa/message"
            headers = {
                'access_token': config.zalo_access_token,
                'Content-Type': 'application/json'
            }
            data = {
                'recipient': {
                    'user_id': config.zalo_oa_id
                },
                'message': {
                    'text': message
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return {'success': True, 'message': 'Đã gửi thông báo Zalo'}
        except Exception as e:
            return {'success': False, 'message': f'Lỗi: {str(e)}'}

