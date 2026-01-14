# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import os

class AIConfig(models.Model):
    _name = 'ai.config'
    _description = 'Cấu hình AI và External API'
    _order = 'name'

    name = fields.Char(
        string='Tên cấu hình',
        required=True,
        help='Tên cấu hình'
    )
    
    # OpenAI Configuration
    openai_api_key = fields.Char(
        string='OpenAI API Key',
        help='API Key từ OpenAI (https://platform.openai.com/api-keys)'
    )
    
    openai_model = fields.Selection([
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
    ], string='OpenAI Model',
        default='gpt-3.5-turbo',
        help='Mô hình OpenAI sử dụng'
    )
    
    # Google Gemini Configuration
    gemini_api_key = fields.Char(
        string='Gemini API Key',
        help='API Key từ Google Gemini (https://aistudio.google.com/app/apikey)'
    )
    
    gemini_model = fields.Selection([
        ('gemini-pro', 'Gemini Pro'),
        ('gemini-1.5-flash', 'Gemini 1.5 Flash'),
        ('gemini-1.5-pro', 'Gemini 1.5 Pro'),
        ('gemini-1.5-flash-latest', 'Gemini 1.5 Flash Latest'),
        ('gemini-1.5-pro-latest', 'Gemini 1.5 Pro Latest'),
    ], string='Gemini Model',
        default='gemini-pro',
        help='Tên model Gemini. Hệ thống sẽ tự động thử các model khác nếu model này không hoạt động.'
    )
    
    # Provider Selection
    ai_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('gemini', 'Google Gemini'),
    ], string='AI Provider',
        default='openai',
        help='Nhà cung cấp AI được sử dụng'
    )
    
    # External API Configuration
    telegram_bot_token = fields.Char(
        string='Telegram Bot Token',
        help='Token từ BotFather trên Telegram'
    )
    
    telegram_chat_id = fields.Char(
        string='Telegram Chat ID',
        help='Chat ID để nhận thông báo'
    )
    
    zalo_oa_id = fields.Char(
        string='Zalo OA ID',
        help='Zalo Official Account ID'
    )
    
    zalo_access_token = fields.Char(
        string='Zalo Access Token',
        help='Zalo Access Token'
    )
    
    google_calendar_client_id = fields.Char(
        string='Google Calendar Client ID',
        help='Google OAuth Client ID'
    )
    
    google_calendar_client_secret = fields.Char(
        string='Google Calendar Client Secret',
        help='Google OAuth Client Secret'
    )
    
    active = fields.Boolean(
        string='Kích hoạt',
        default=True,
        help='Kích hoạt cấu hình này'
    )

    @api.model
    def get_active_config(self):
        """Lấy cấu hình đang kích hoạt"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            # Tạo cấu hình mặc định
            config = self.create({
                'name': 'Cấu hình mặc định',
                'active': True,
            })
        return config
    
    def action_test_gemini_api(self):
        """Test Gemini API key"""
        self.ensure_one()
        if not self.gemini_api_key:
            raise UserError('Chưa nhập Gemini API Key!')
        
        try:
            import google.generativeai as genai
        except ImportError:
            raise UserError('Chưa cài đặt thư viện google-generativeai')
        
        api_key = self.gemini_api_key.strip()
        if not api_key:
            raise UserError('API Key không được để trống!')
        
        if not api_key.startswith('AIza'):
            raise UserError('API Key không đúng format! Phải bắt đầu bằng "AIza..."')
        
        try:
            genai.configure(api_key=api_key)
            
            # Thử lấy danh sách model
            try:
                models = genai.list_models()
                available_models = []
                for m in models:
                    if hasattr(m, 'supported_generation_methods') and 'generateContent' in m.supported_generation_methods:
                        model_name = m.name.replace('models/', '') if m.name.startswith('models/') else m.name
                        available_models.append(model_name)
                
                # Thử gọi API với model đầu tiên hoặc gemini-pro
                test_model = 'gemini-pro'
                if available_models:
                    # Ưu tiên flash, sau đó pro
                    flash_models = [m for m in available_models if 'flash' in m.lower()]
                    pro_models = [m for m in available_models if 'pro' in m.lower() and 'flash' not in m.lower()]
                    if flash_models:
                        test_model = flash_models[0]
                    elif pro_models:
                        test_model = pro_models[0]
                    elif available_models:
                        test_model = available_models[0]
                
                model = genai.GenerativeModel(test_model)
                response = model.generate_content("Xin chào")
                
                if response and hasattr(response, 'text') and response.text:
                    result_text = response.text.strip()
                elif response and hasattr(response, 'candidates'):
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        result_text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                    else:
                        result_text = "API trả về nhưng không có text"
                else:
                    result_text = "API trả về nhưng không có nội dung"
                
                # Tạo thông báo thành công
                models_list = ", ".join(available_models[:5])
                if len(available_models) > 5:
                    models_list += "..."
                
                message = (
                    f'✅ API Key hợp lệ!\n\n'
                    f'Model đã test: {test_model}\n\n'
                    f'Danh sách model có sẵn ({len(available_models)} models): {models_list}\n\n'
                    f'Response test: {result_text[:100]}...'
                )
                
                # Return action để hiển thị notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Test thành công!',
                        'message': message,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            except Exception as e:
                error_msg = str(e)
                if 'API key not valid' in error_msg or 'API_KEY_INVALID' in error_msg:
                    raise UserError('API Key không hợp lệ! Vui lòng kiểm tra lại.')
                elif 'not found' in error_msg.lower() or '404' in error_msg:
                    raise UserError(f'Model "{test_model}" không tìm thấy. Vui lòng thử model khác.')
                else:
                    raise UserError(f'Lỗi khi test API: {error_msg}')
        except UserError:
            raise
        except Exception as e:
            raise UserError(f'Lỗi khi test Gemini API: {str(e)}')

