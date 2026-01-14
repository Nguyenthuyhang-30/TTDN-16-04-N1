# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class AIAssistantWizard(models.TransientModel):
    _name = 'ai.assistant.wizard'
    _description = 'Trợ lý ảo giải đáp nội quy'

    question = fields.Text(
        string='Câu hỏi',
        required=True,
        help='Nhập câu hỏi về nội quy, quy định công ty...'
    )
    
    answer = fields.Text(
        string='Câu trả lời',
        readonly=True,
        help='Câu trả lời từ AI'
    )
    
    context_type = fields.Selection([
        ('hr_policy', 'Nội quy nhân sự'),
        ('attendance', 'Quy định chấm công'),
        ('payroll', 'Quy định lương thưởng'),
        ('customer', 'Quy định khách hàng'),
        ('document', 'Quy định văn bản'),
        ('general', 'Chung'),
    ], string='Chủ đề',
        default='general',
        help='Chủ đề câu hỏi'
    )
    

    def action_ask(self):
        """MỨC 3: Sử dụng AI để trả lời câu hỏi"""
        self.ensure_one()
        
        if not self.question:
            raise UserError('Vui lòng nhập câu hỏi!')
        
        try:
            config = self.env['ai.config'].get_active_config()
            
            # Kiểm tra cấu hình
            if not config.ai_provider:
                raise UserError('Chưa cấu hình AI Provider! Vui lòng vào AI & API → Cấu hình AI để thiết lập.')
            
            if config.ai_provider == 'openai' and not config.openai_api_key:
                raise UserError('Chưa cấu hình OpenAI API Key! Vui lòng vào AI & API → Cấu hình AI để nhập API Key.')
            
            if config.ai_provider == 'gemini' and not config.gemini_api_key:
                raise UserError('Chưa cấu hình Gemini API Key! Vui lòng vào AI & API → Cấu hình AI để nhập API Key.')
            
            # Xây dựng context dựa trên chủ đề
            context = self._get_context(self.context_type)
            
            prompt = f"""
            Bạn là trợ lý ảo của công ty, chuyên giải đáp các câu hỏi về nội quy và quy định.
            
            Thông tin nội quy công ty:
            {context}
            
            Câu hỏi: {self.question}
            
            Hãy trả lời câu hỏi một cách rõ ràng, chính xác và thân thiện bằng tiếng Việt.
            """
            
            answer = None
            gemini_quota_error = False
            
            # Thử provider được chọn trước
            if config.ai_provider == 'openai':
                try:
                    answer = self._call_openai(config, prompt)
                except UserError as e:
                    error_msg = str(e)
                    if 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                        # OpenAI hết quota, thử Gemini nếu có
                        if config.gemini_api_key:
                            try:
                                answer = self._call_gemini(config, prompt)
                            except:
                                raise UserError(
                                    f'Cả OpenAI và Gemini đều hết quota!\n\n'
                                    f'Vui lòng:\n'
                                    f'1. Kiểm tra quota tại:\n'
                                    f'   - OpenAI: https://platform.openai.com/account/billing\n'
                                    f'   - Gemini: https://aistudio.google.com/app/apikey\n'
                                    f'2. Nạp thêm credit hoặc đợi quota reset\n'
                                    f'3. Thử lại sau'
                                )
                        else:
                            raise
                    else:
                        raise
            elif config.ai_provider == 'gemini':
                try:
                    answer = self._call_gemini(config, prompt)
                except UserError as e:
                    error_msg = str(e)
                    if 'quota' in error_msg.lower() or 'limit' in error_msg.lower() or 'vượt quá giới hạn' in error_msg:
                        gemini_quota_error = True
                        # Gemini hết quota, tự động thử OpenAI nếu có
                        if config.openai_api_key:
                            try:
                                answer = self._call_openai(config, prompt)
                                # Thông báo đã tự động chuyển sang OpenAI
                                if answer:
                                    answer = f"[⚠️ Lưu ý: Gemini đã hết quota, đã tự động chuyển sang OpenAI]\n\n{answer}"
                            except:
                                raise UserError(
                                    f'Gemini đã hết quota và OpenAI cũng không khả dụng!\n\n'
                                    f'Vui lòng:\n'
                                    f'1. Kiểm tra quota Gemini tại: https://aistudio.google.com/app/apikey\n'
                                    f'2. Kiểm tra quota OpenAI tại: https://platform.openai.com/account/billing\n'
                                    f'3. Nạp thêm credit hoặc đợi quota reset\n'
                                    f'4. Thử lại sau'
                                )
                        else:
                            raise UserError(
                                f'Đã vượt quá giới hạn sử dụng Gemini API!\n\n'
                                f'Giải pháp:\n'
                                f'1. Đợi quota reset (thường là hàng ngày hoặc hàng tháng)\n'
                                f'2. Nâng cấp gói Gemini tại: https://aistudio.google.com/app/apikey\n'
                                f'3. Cấu hình OpenAI API Key để tự động fallback khi Gemini hết quota\n'
                                f'   (Vào AI & API → Cấu hình AI → Nhập OpenAI API Key)'
                            )
                    else:
                        raise
            else:
                raise UserError('Chưa cấu hình AI Provider!')
            
            if not answer or not answer.strip():
                raise UserError('AI không trả về câu trả lời. Vui lòng thử lại hoặc kiểm tra cấu hình API.')
            
            # Xử lý text để đảm bảo hiển thị ngang (không bị dọc)
            import re
            # Loại bỏ tất cả ký tự xuống dòng và thay bằng khoảng trắng
            answer = answer.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            # Thay thế nhiều khoảng trắng liên tiếp bằng một khoảng trắng
            answer = re.sub(r'\s+', ' ', answer)
            # Loại bỏ khoảng trắng thừa ở đầu và cuối
            answer = answer.strip()
            # Format lại: thêm xuống dòng sau dấu chấm, chấm hỏi, chấm than để dễ đọc
            # Chỉ khi có khoảng trắng và chữ cái hoa tiếp theo (đầu câu mới)
            answer = re.sub(r'\.\s+([A-ZĂÂĐÊÔƠƯ])', r'.\n\n\1', answer)
            answer = re.sub(r'\?\s+([A-ZĂÂĐÊÔƠƯ])', r'?\n\n\1', answer)
            answer = re.sub(r'!\s+([A-ZĂÂĐÊÔƠƯ])', r'!\n\n\1', answer)
            
            # Lưu câu trả lời đã được format
            self.write({'answer': answer})
            
            # Reload view để hiển thị câu trả lời
            # Dùng action window với res_id để reload wizard
            return {
                'type': 'ir.actions.act_window',
                'name': 'Trợ lý ảo',
                'res_model': 'ai.assistant.wizard',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
                'context': dict(self.env.context),
            }
            
        except UserError:
            # Re-raise UserError để hiển thị thông báo lỗi rõ ràng
            raise
        except Exception as e:
            error_msg = str(e)
            # Cải thiện thông báo lỗi
            if 'API key' in error_msg or 'API_KEY' in error_msg:
                raise UserError(f'Lỗi API Key: {error_msg}\n\nVui lòng kiểm tra lại API Key trong AI & API → Cấu hình AI.')
            elif 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                raise UserError(f'Đã vượt quá giới hạn sử dụng API: {error_msg}\n\nVui lòng kiểm tra quota của bạn.')
            else:
                raise UserError(f'Lỗi khi xử lý câu hỏi: {error_msg}\n\nVui lòng kiểm tra:\n1. API Key có hợp lệ không\n2. Kết nối mạng\n3. Cấu hình AI Provider')
    
    def _get_context(self, context_type):
        """Lấy context dựa trên chủ đề"""
        contexts = {
            'hr_policy': """
            - Giờ làm việc: 8h30 - 17h30
            - Giờ nghỉ: 12h30 - 13h30
            - Nhân viên phải chấm công đầy đủ
            """,
            'attendance': """
            - Đi muộn sau 8h30 sẽ bị phạt 50,000 VNĐ/lần
            - Về sớm trước 17h30 sẽ bị phạt 50,000 VNĐ/lần
            - Phải có cả giờ vào và giờ ra mới tính công
            """,
            'payroll': """
            - Lương được tính dựa trên số công thực tế
            - Phạt đi muộn/về sớm tự động trừ vào lương
            - Thưởng và phạt thủ công có thể được thêm vào
            """,
            'customer': """
            - Khách hàng được phân loại: Tiềm năng cao, Tiềm năng thấp, Khách hàng thường
            - Trạng thái: Mới, Cũ, VIP
            - Đơn hàng tự động tạo văn bản đi khi xác nhận
            """,
            'document': """
            - Văn bản đến có độ ưu tiên cao sẽ tự động gán nhân viên
            - Văn bản đi tự động tạo khi đơn hàng được xác nhận
            """,
            'general': 'Thông tin chung về công ty và quy định làm việc.',
        }
        return contexts.get(context_type, contexts['general'])
    
    def _call_openai(self, config, prompt):
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
                    {'role': 'system', 'content': 'Bạn là trợ lý ảo chuyên nghiệp, luôn trả lời bằng tiếng Việt.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise UserError(f'Lỗi OpenAI API: {str(e)}')
    
    def _call_gemini(self, config, prompt):
        """Gọi Gemini API với auto-fallback"""
        try:
            try:
                import google.generativeai as genai
            except ImportError:
                raise UserError('Chưa cài đặt thư viện google-generativeai')
            
            api_key = config.gemini_api_key.strip() if config.gemini_api_key else ''
            if not api_key:
                raise UserError('Gemini API Key không được để trống! Vui lòng cấu hình trong AI & API → Cấu hình AI.')
            
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
                        raise UserError(
                            'Gemini API Key không hợp lệ!\n\n'
                            'Vui lòng:\n'
                            '1. Kiểm tra lại API key trong AI & API → Cấu hình AI\n'
                            '2. Lấy API key mới tại: https://aistudio.google.com/app/apikey\n'
                            '3. Đảm bảo API key được copy đầy đủ'
                        )
                    elif 'quota' in error_msg.lower() or 'limit' in error_msg.lower() or 'vượt quá giới hạn' in error_msg:
                        # Không raise ngay, để action_ask có thể fallback sang OpenAI
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

