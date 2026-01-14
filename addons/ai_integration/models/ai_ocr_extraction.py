# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import io

class OCRExtraction(models.Model):
    _name = 'ai.ocr.extraction'
    _description = 'OCR Bóc tách dữ liệu từ hình ảnh'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Tên',
        required=True,
        help='Tên file hoặc tài liệu'
    )
    
    document_type = fields.Selection([
        ('invoice', 'Hóa đơn'),
        ('cv', 'CV/Resume'),
        ('contract', 'Hợp đồng'),
        ('other', 'Khác'),
    ], string='Loại tài liệu',
        required=True,
        default='invoice',
        help='Loại tài liệu cần bóc tách'
    )
    
    image = fields.Binary(
        string='Hình ảnh/Tài liệu',
        required=True,
        help='Upload hình ảnh hoặc file PDF cần bóc tách'
    )
    
    image_filename = fields.Char(
        string='Tên file'
    )
    
    extracted_text = fields.Text(
        string='Văn bản đã bóc tách',
        readonly=True,
        help='Văn bản được OCR bóc tách từ hình ảnh'
    )
    
    extracted_data = fields.Text(
        string='Dữ liệu đã xử lý',
        readonly=True,
        help='Dữ liệu đã được AI xử lý và cấu trúc hóa'
    )
    
    status = fields.Selection([
        ('draft', 'Nháp'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
    ], string='Trạng thái',
        default='draft',
        tracking=True
    )
    
    error_message = fields.Text(
        string='Thông báo lỗi',
        readonly=True
    )

    def action_extract_ocr(self):
        """MỨC 3: Sử dụng OCR để bóc tách văn bản từ hình ảnh"""
        for record in self:
            if not record.image:
                raise UserError('Vui lòng upload hình ảnh hoặc tài liệu!')
            
            record.status = 'processing'
            record.error_message = False
            
            try:
                # Bước 1: OCR để lấy văn bản
                text = self._extract_text_with_ocr(record)
                record.extracted_text = text
                
                # Bước 2: Sử dụng AI để cấu trúc hóa dữ liệu
                structured_data = self._structure_data_with_ai(record, text)
                record.extracted_data = structured_data
                
                record.status = 'completed'
                
            except Exception as e:
                record.status = 'failed'
                record.error_message = str(e)
                raise UserError(f'Lỗi khi bóc tách: {str(e)}')
        
        return True
    
    def _extract_text_with_ocr(self, record):
        """Sử dụng Tesseract OCR để bóc tách văn bản"""
        try:
            try:
                from PIL import Image
                import pytesseract
            except ImportError as e:
                raise UserError(f'Chưa cài đặt thư viện OCR. Chạy: pip install pytesseract Pillow. Lỗi: {str(e)}')
            
            # Decode base64 image
            image_data = base64.b64decode(record.image)
            image = Image.open(io.BytesIO(image_data))
            
            # OCR với tiếng Việt
            text = pytesseract.image_to_string(image, lang='vie+eng')
            
            return text.strip()
            
        except Exception as e:
            raise UserError(f'Lỗi OCR: {str(e)}')
    
    def _structure_data_with_ai(self, record, text):
        """Sử dụng AI để cấu trúc hóa dữ liệu đã OCR"""
        config = self.env['ai.config'].get_active_config()
        
        if record.document_type == 'invoice':
            prompt = f"""
            Hãy phân tích và trích xuất thông tin từ hóa đơn sau đây. 
            Trả về dưới dạng JSON với các trường: số hóa đơn, ngày, tên khách hàng, tổng tiền, danh sách sản phẩm.
            
            Văn bản:
            {text}
            """
        elif record.document_type == 'cv':
            prompt = f"""
            Hãy phân tích và trích xuất thông tin từ CV sau đây.
            Trả về dưới dạng JSON với các trường: họ tên, email, số điện thoại, kinh nghiệm, kỹ năng, học vấn.
            
            Văn bản:
            {text}
            """
        else:
            prompt = f"""
            Hãy phân tích và tóm tắt thông tin chính từ tài liệu sau:
            
            {text}
            """
        
        try:
            if config.ai_provider == 'openai':
                return self._call_openai_api(config, prompt)
            elif config.ai_provider == 'gemini':
                return self._call_gemini_api(config, prompt)
            else:
                return text  # Fallback: trả về text gốc
        except Exception as e:
            return f"Lỗi khi xử lý AI: {str(e)}\n\nVăn bản gốc:\n{text}"
    
    def _call_openai_api(self, config, prompt):
        """Gọi OpenAI API"""
        try:
            try:
                from openai import OpenAI
            except ImportError:
                raise UserError('Chưa cài đặt thư viện openai')
            
            client = OpenAI(api_key=config.openai_api_key)
            
            response = client.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {'role': 'system', 'content': 'Bạn là trợ lý phân tích tài liệu chuyên nghiệp.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise UserError(f'Lỗi OpenAI API: {str(e)}')
    
    def _call_gemini_api(self, config, prompt):
        """Gọi Gemini API với auto-fallback"""
        try:
            try:
                import google.generativeai as genai
            except ImportError:
                raise UserError('Chưa cài đặt thư viện google-generativeai')
            
            api_key = config.gemini_api_key.strip() if config.gemini_api_key else ''
            if not api_key:
                raise UserError('Gemini API Key không được để trống!')
            
            genai.configure(api_key=api_key)
            
            # Lấy danh sách model có sẵn từ API
            try:
                available_models = [m.name.replace('models/', '') for m in genai.list_models() 
                                  if 'generateContent' in m.supported_generation_methods]
            except:
                available_models = []
            
            # Danh sách model để thử
            models_to_try = []
            if config.gemini_model:
                model_name = str(config.gemini_model).strip() if config.gemini_model else ''
                if model_name:
                    models_to_try.append(model_name)
            
            # Thêm các model fallback
            fallback_models = [
                'gemini-pro',
                'gemini-1.5-pro',
                'gemini-1.5-flash',
                'gemini-1.5-pro-latest',
                'gemini-1.5-flash-latest',
            ]
            
            # Nếu có danh sách model có sẵn, ưu tiên các model đó
            if available_models:
                flash_models = [m for m in available_models if 'flash' in m.lower()]
                pro_models = [m for m in available_models if 'pro' in m.lower() and 'flash' not in m.lower()]
                other_models = [m for m in available_models if m not in flash_models and m not in pro_models]
                models_to_try.extend(flash_models + pro_models + other_models)
            else:
                models_to_try.extend(fallback_models)
            
            models_to_try = [m for m in models_to_try if m]
            models_to_try = list(dict.fromkeys(models_to_try))
            
            last_error = None
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    if 'API key not valid' in error_msg or 'API_KEY_INVALID' in error_msg:
                        raise UserError('Gemini API Key không hợp lệ! Vui lòng kiểm tra lại trong Cấu hình AI.')
                    elif 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                        raise UserError('Đã vượt quá giới hạn sử dụng Gemini API.')
                    elif 'not found' in error_msg.lower() or 'not supported' in error_msg.lower() or '404' in error_msg:
                        continue
                    else:
                        raise
            
            if last_error:
                raise UserError(f'Không thể sử dụng model Gemini. Đã thử: {", ".join(models_to_try)}. Lỗi: {str(last_error)}')
            raise UserError('Gemini API không trả về kết quả.')
        except UserError:
            raise
        except Exception as e:
            raise UserError(f'Lỗi Gemini API: {str(e)}')

