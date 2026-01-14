# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class DocumentSummary(models.Model):
    _name = 'ai.document.summary'
    _description = 'AI Tóm tắt văn bản'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Tiêu đề',
        required=True,
        help='Tiêu đề tóm tắt'
    )
    
    document_id = fields.Many2one(
        'om.document.incoming',
        string='Văn bản gốc',
        help='Văn bản cần tóm tắt',
        ondelete='set null'
    )
    
    original_text = fields.Text(
        string='Nội dung gốc',
        required=True,
        help='Nội dung văn bản cần tóm tắt'
    )
    
    summary = fields.Text(
        string='Tóm tắt',
        readonly=True,
        help='Nội dung đã được AI tóm tắt'
    )
    
    @api.depends('summary')
    def _compute_summary_display(self):
        """Compute field để hiển thị summary đã được xử lý"""
        for record in self:
            if record.summary:
                record.summary_display = self._process_text_for_horizontal_display(record.summary)
            else:
                record.summary_display = ''
    
    summary_display = fields.Text(
        string='Tóm tắt (Hiển thị)',
        compute='_compute_summary_display',
        store=False,
        help='Nội dung tóm tắt đã được xử lý để hiển thị ngang'
    )
    
    summary_length = fields.Selection([
        ('short', 'Ngắn (1-2 câu)'),
        ('medium', 'Trung bình (3-5 câu)'),
        ('long', 'Dài (1 đoạn)'),
    ], string='Độ dài tóm tắt',
        default='medium',
        help='Độ dài của bản tóm tắt'
    )
    
    use_simple_summary = fields.Boolean(
        string='Dùng tóm tắt đơn giản (không cần AI)',
        default=False,
        help='Nếu bật, sẽ dùng phương pháp tóm tắt đơn giản (lấy các câu đầu tiên) thay vì AI. Hữu ích khi AI không hoạt động.'
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
        readonly=True,
        help='Thông báo lỗi nếu có'
    )
    
    def action_summarize(self):
        """MỨC 3: Sử dụng AI để tóm tắt văn bản"""
        for record in self:
            if not record.id:
                raise UserError('Vui lòng lưu record trước khi tóm tắt!')
            if not record.original_text:
                raise UserError('Vui lòng nhập nội dung cần tóm tắt!')
            
            record.write({
                'status': 'processing',
                'error_message': False,
            })
            
            try:
                summary = None
                
                # Nếu người dùng chọn dùng simple summary, dùng luôn
                if record.use_simple_summary:
                    summary = self._summarize_simple(record)
                    if summary:
                        summary = f"[Tóm tắt tự động - không dùng AI] {summary}"
                else:
                    # Thử dùng AI
                    config = self.env['ai.config'].get_active_config()
                    
                    # Thử OpenAI trước nếu có cấu hình
                    if config.ai_provider == 'openai' and config.openai_api_key:
                        try:
                            summary = self._summarize_with_openai(record, config)
                        except UserError as e:
                            # Nếu là lỗi quota hoặc API key, không thử tiếp
                            error_msg = str(e)
                            if 'quota' in error_msg.lower() or 'insufficient_quota' in error_msg.lower():
                                # Lỗi quota, tự động fallback
                                pass
                            else:
                                # Lỗi khác, thử Gemini hoặc simple summary
                                pass
                        except Exception as e:
                            # Lỗi khác, thử Gemini hoặc simple summary
                            pass
                    
                    # Nếu chưa có summary, thử Gemini
                    if not summary and config.ai_provider == 'gemini' and config.gemini_api_key:
                        try:
                            summary = self._summarize_with_gemini(record, config)
                        except Exception as e:
                            # Nếu Gemini lỗi, thử OpenAI (nếu có) hoặc simple summary
                            if config.openai_api_key and config.ai_provider != 'openai':
                                try:
                                    summary = self._summarize_with_openai(record, config)
                                except:
                                    pass
                    
                    # Nếu vẫn chưa có summary, tự động fallback sang simple summary
                    if not summary:
                        summary = self._summarize_simple(record)
                        if summary:
                            summary = f"[Tóm tắt tự động - AI không khả dụng (quota hết hoặc lỗi), đã chuyển sang phương pháp đơn giản] {summary}"
                
                if not summary:
                    raise UserError('Không thể tạo tóm tắt. Vui lòng kiểm tra cấu hình AI hoặc thử lại.')
                
                # Xử lý text để đảm bảo hiển thị ngang (không bị dọc)
                summary = self._process_text_for_horizontal_display(summary)
                
                # Dùng write để đảm bảo dữ liệu được lưu
                record.write({
                    'summary': summary,
                    'status': 'completed',
                })
                
            except Exception as e:
                # Dùng write để đảm bảo dữ liệu được lưu
                record.write({
                    'status': 'failed',
                    'error_message': str(e)
                })
                raise UserError(f'Lỗi khi tóm tắt: {str(e)}')
        
        return True
    
    def _process_text_for_horizontal_display(self, text):
        """Xử lý text để đảm bảo hiển thị ngang (không bị dọc)"""
        if not text:
            return text
        
        import re
        # Loại bỏ HOÀN TOÀN tất cả ký tự xuống dòng và thay bằng khoảng trắng
        text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        # Loại bỏ các ký tự đặc biệt có thể gây xuống dòng
        text = text.replace('\t', ' ').replace('\v', ' ').replace('\f', ' ')
        # Thay thế nhiều khoảng trắng liên tiếp bằng một khoảng trắng
        text = re.sub(r'\s+', ' ', text)
        # Loại bỏ khoảng trắng thừa ở đầu và cuối
        text = text.strip()
        
        # KHÔNG thêm lại xuống dòng - để text hiển thị hoàn toàn ngang
        return text
    
    def _summarize_simple(self, record):
        """Tóm tắt đơn giản không cần AI - lấy các câu đầu tiên"""
        text = record.original_text.strip()
        if not text:
            return None
        
        # Tách thành các câu
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in '.!?。！？':
                sentence = current_sentence.strip()
                if sentence:
                    sentences.append(sentence)
                current_sentence = ""
        
        # Thêm câu cuối nếu còn
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Xác định số câu cần lấy dựa trên độ dài
        if record.summary_length == 'short':
            num_sentences = min(2, len(sentences))
        elif record.summary_length == 'long':
            num_sentences = min(10, len(sentences))
        else:  # medium
            num_sentences = min(5, len(sentences))
        
        # Lấy các câu đầu tiên
        selected_sentences = sentences[:num_sentences]
        summary = ' '.join(selected_sentences)
        
        # Xử lý text để hiển thị ngang
        summary = self._process_text_for_horizontal_display(summary)
        
        return summary
    
    def _summarize_with_openai(self, record, config):
        """Tóm tắt bằng OpenAI"""
        try:
            import openai
        except ImportError:
            raise UserError('Thư viện OpenAI chưa được cài đặt. Vui lòng cài đặt: pip install openai')
        
        try:
            client = openai.OpenAI(api_key=config.openai_api_key)
            
            # Xác định độ dài tóm tắt
            length_prompt = {
                'short': 'Tóm tắt ngắn gọn trong 1-2 câu.',
                'medium': 'Tóm tắt trong 3-5 câu.',
                'long': 'Tóm tắt chi tiết trong 1 đoạn văn.'
            }.get(record.summary_length, 'Tóm tắt trong 3-5 câu.')
            
            prompt = f"""Hãy tóm tắt văn bản sau đây bằng tiếng Việt. {length_prompt}

Văn bản:
{record.original_text}

Tóm tắt:"""
            
            response = client.chat.completions.create(
                model=config.openai_model or 'gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': 'Bạn là một trợ lý AI chuyên tóm tắt văn bản bằng tiếng Việt.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Xử lý text để hiển thị ngang
            summary = self._process_text_for_horizontal_display(summary)
            
            return summary
            
        except openai.error.AuthenticationError:
            raise UserError('Lỗi xác thực OpenAI API. Vui lòng kiểm tra API key.')
        except openai.error.RateLimitError:
            raise UserError('Đã vượt quá giới hạn API. Vui lòng thử lại sau.')
        except openai.error.APIError as e:
            error_msg = str(e)
            if 'insufficient_quota' in error_msg.lower() or 'quota' in error_msg.lower():
                raise UserError('Hết quota OpenAI. Vui lòng kiểm tra tài khoản hoặc thử dùng tóm tắt đơn giản.')
            raise UserError(f'Lỗi OpenAI API: {error_msg}')
        except Exception as e:
            raise UserError(f'Lỗi khi tóm tắt bằng OpenAI: {str(e)}')
    
    def _summarize_with_gemini(self, record, config):
        """Tóm tắt bằng Google Gemini"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise UserError('Thư viện Google Generative AI chưa được cài đặt. Vui lòng cài đặt: pip install google-generativeai')
        
        try:
            genai.configure(api_key=config.gemini_api_key)
            
            # Xác định model
            model_name = config.gemini_model or 'gemini-pro'
            # Thử các biến thể của model name
            model_variants = [
                model_name,
                f'models/{model_name}',
                model_name.replace('gemini-', 'gemini-1.5-'),
                f'models/{model_name.replace("gemini-", "gemini-1.5-")}',
            ]
            
            model = None
            last_error = None
            
            for variant in model_variants:
                try:
                    model = genai.GenerativeModel(variant)
                    # Test model bằng cách tạo một request đơn giản
                    break
                except Exception as e:
                    last_error = e
                    continue
            
            if not model:
                raise UserError(f'Không thể tìm thấy model Gemini. Đã thử: {", ".join(model_variants)}. Lỗi cuối: {str(last_error)}')
            
            # Xác định độ dài tóm tắt
            length_prompt = {
                'short': 'Tóm tắt ngắn gọn trong 1-2 câu.',
                'medium': 'Tóm tắt trong 3-5 câu.',
                'long': 'Tóm tắt chi tiết trong 1 đoạn văn.'
            }.get(record.summary_length, 'Tóm tắt trong 3-5 câu.')
            
            prompt = f"""Hãy tóm tắt văn bản sau đây bằng tiếng Việt. {length_prompt}

Văn bản:
{record.original_text}

Tóm tắt:"""
            
            response = model.generate_content(prompt)
            summary = response.text.strip()
            
            # Xử lý text để hiển thị ngang
            summary = self._process_text_for_horizontal_display(summary)
            
            return summary
            
        except Exception as e:
            error_msg = str(e)
            if 'api key' in error_msg.lower() or 'api_key' in error_msg.lower():
                raise UserError('Lỗi Gemini API: API key không hợp lệ. Vui lòng kiểm tra lại API key trong Cấu hình AI.')
            elif 'quota' in error_msg.lower():
                raise UserError('Hết quota Gemini. Vui lòng kiểm tra tài khoản hoặc thử dùng tóm tắt đơn giản.')
            elif 'not found' in error_msg.lower() or 'not available' in error_msg.lower():
                raise UserError(f'Model Gemini không tìm thấy hoặc không khả dụng. Lỗi: {error_msg}')
            else:
                raise UserError(f'Lỗi khi tóm tắt bằng Gemini: {error_msg}')
    
    @api.model
    def _fix_invalid_document_ids(self):
        """Sửa các record có document_id không hợp lệ"""
        try:
            # Sử dụng SQL để sửa trực tiếp
            self.env.cr.execute("""
                UPDATE ai_document_summary 
                SET document_id = NULL 
                WHERE document_id IS NOT NULL 
                AND document_id NOT IN (
                    SELECT id FROM om_document_incoming WHERE id IS NOT NULL
                )
            """)
            fixed_count = self.env.cr.rowcount
            if fixed_count > 0:
                self.env.cr.commit()
            return fixed_count
        except Exception:
            self.env.cr.rollback()
            return 0
    
    @api.model
    def _ensure_data_integrity(self):
        """Đảm bảo tính toàn vẹn dữ liệu - sửa các record có document_id không hợp lệ"""
        try:
            return self._fix_invalid_document_ids()
        except:
            return 0
    
    @api.model
    def create(self, vals):
        """Override create để tự động sửa dữ liệu trước khi tạo mới"""
        self._ensure_data_integrity()
        return super(DocumentSummary, self).create(vals)
    
    def write(self, vals):
        """Override write để tự động sửa dữ liệu trước khi ghi"""
        self._ensure_data_integrity()
        return super(DocumentSummary, self).write(vals)
    
    def read(self, fields=None, load='_classic_read'):
        """Override read để đảm bảo dữ liệu hợp lệ trước khi đọc"""
        try:
            self._ensure_data_integrity()
        except:
            pass
        
        # Sửa tất cả document_id không hợp lệ trước khi đọc
        try:
            self.env.cr.execute("""
                UPDATE ai_document_summary 
                SET document_id = NULL 
                WHERE document_id IS NOT NULL 
                AND document_id NOT IN (
                    SELECT id FROM om_document_incoming WHERE id IS NOT NULL
                )
            """)
            if self.env.cr.rowcount > 0:
                self.env.cr.commit()
        except:
            self.env.cr.rollback()
        
        # Thử đọc bình thường
        try:
            return super(DocumentSummary, self).read(fields, load)
        except (AttributeError, ValueError) as e:
            # Nếu lỗi do corrupt Many2one, sửa và đọc từ database trực tiếp
            if "'_unknown' object has no attribute 'id'" in str(e) or "not enough values to unpack" in str(e):
                # Sửa lại tất cả document_id
                try:
                    self.env.cr.execute("""
                        UPDATE ai_document_summary 
                        SET document_id = NULL 
                        WHERE document_id IS NOT NULL 
                        AND document_id NOT IN (
                            SELECT id FROM om_document_incoming WHERE id IS NOT NULL
                        )
                    """)
                    self.env.cr.commit()
                    # Invalidate cache
                    self.invalidate_recordset(['document_id'])
                except:
                    self.env.cr.rollback()
                
                # Đọc trực tiếp từ database, không dùng super().read() nữa
                result = []
                if not self.ids:
                    # Nếu không có ID (record mới), trả về default data
                    default_data = {
                        'id': False,
                        'name': False,
                        'document_id': False,
                        'original_text': False,
                        'summary': False,
                        'summary_display': False,
                        'summary_length': 'medium',
                        'use_simple_summary': False,
                        'status': 'draft',
                        'error_message': False,
                    }
                    if fields:
                        # Đảm bảo 'id' luôn có trong result
                        filtered_data = {k: v for k, v in default_data.items() if k in fields}
                        # Luôn thêm 'id' vào result, bất kể fields có gì
                        if 'id' not in filtered_data:
                            filtered_data['id'] = False
                        default_data = filtered_data
                    # Đảm bảo 'id' luôn có, kể cả khi không có fields
                    if 'id' not in default_data:
                        default_data['id'] = False
                    return [default_data]
                
                # Đọc từng record từ database
                for record_id in self.ids:
                    record_data = None
                    try:
                        # Đọc trực tiếp từ database
                        self.env.cr.execute("""
                            SELECT name, document_id, original_text, summary, summary_length, 
                                   use_simple_summary, status, error_message
                            FROM ai_document_summary 
                            WHERE id = %s
                        """, (record_id,))
                        row = self.env.cr.fetchone()
                        
                        if row:
                            record_data = {
                                'id': record_id,
                                'name': row[0] or False,
                                'document_id': row[1] if row[1] else False,
                                'original_text': row[2] or False,
                                'summary': row[3] or False,
                                'summary_length': row[4] or 'medium',
                                'use_simple_summary': row[5] or False,
                                'status': row[6] or 'draft',
                                'error_message': row[7] or False,
                            }
                            
                            # Compute summary_display
                            if record_data.get('summary'):
                                record_data['summary_display'] = self._process_text_for_horizontal_display(record_data['summary'])
                            else:
                                record_data['summary_display'] = False
                    except:
                        pass
                    
                    # Nếu không đọc được, tạo default data
                    if not record_data:
                        record_data = {
                            'id': record_id,
                            'name': False,
                            'document_id': False,
                            'original_text': False,
                            'summary': False,
                            'summary_display': False,
                            'summary_length': 'medium',
                            'use_simple_summary': False,
                            'status': 'draft',
                            'error_message': False,
                        }
                    
                    # Lọc theo fields nếu có, nhưng đảm bảo 'id' luôn có
                    if fields:
                        filtered_data = {k: v for k, v in record_data.items() if k in fields}
                        # Luôn thêm 'id' vào result, bất kể fields có gì
                        if 'id' not in filtered_data:
                            filtered_data['id'] = record_id
                        record_data = filtered_data
                    
                    # Đảm bảo 'id' luôn có, kể cả khi không có fields
                    if 'id' not in record_data:
                        record_data['id'] = record_id
                    
                    result.append(record_data)
                
                # Đảm bảo luôn trả về ít nhất 1 phần tử nếu có record
                # Nếu result rỗng nhưng có ids, tạo default data cho record đầu tiên
                if not result and self.ids:
                    record_id = self.ids[0]
                    default_data = {
                        'id': record_id,
                        'name': False,
                        'document_id': False,
                        'original_text': False,
                        'summary': False,
                        'summary_display': False,
                        'summary_length': 'medium',
                        'use_simple_summary': False,
                        'status': 'draft',
                        'error_message': False,
                    }
                    if fields:
                        # Đảm bảo 'id' luôn có trong result
                        filtered_data = {k: v for k, v in default_data.items() if k in fields}
                        # Luôn thêm 'id' vào result, bất kể fields có gì
                        if 'id' not in filtered_data:
                            filtered_data['id'] = record_id
                        default_data = filtered_data
                    
                    # Đảm bảo 'id' luôn có, kể cả khi không có fields
                    if 'id' not in default_data:
                        default_data['id'] = record_id
                    
                    result.append(default_data)
                
                return result
            else:
                raise
    
    def action_fix_invalid_documents(self):
        """Sửa các record có document_id không hợp lệ - có thể gọi từ UI"""
        fixed_count = self.env['ai.document.summary']._fix_invalid_document_ids()
        if fixed_count > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Đã sửa dữ liệu',
                    'message': f'Đã sửa {fixed_count} record có document_id không hợp lệ.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Không có lỗi',
                    'message': 'Tất cả các record đều hợp lệ.',
                    'type': 'info',
                    'sticky': False,
                }
            }
