{
    'name': 'AI Integration & External API',
    'version': '17.0.1.0.1',
    'category': 'Tools',
    'summary': 'Tích hợp AI/LLM và External API cho hệ thống',
    'description': """
        Module tích hợp AI và External API cho Odoo 17
        =============================================
        
        Tính năng AI:
        - AI tóm tắt văn bản tự động
        - OCR bóc tách dữ liệu từ hóa đơn/CV
        - Trợ lý ảo giải đáp nội quy
        
        Tính năng External API:
        - Đồng bộ lịch Google Calendar
        - Gửi thông báo qua Telegram/Zalo
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'om_hr_custom',
    ],
    # Lưu ý: external_dependencies đã được loại bỏ để tránh lỗi khi cài đặt
    # Các thư viện Python sẽ được kiểm tra và báo lỗi khi sử dụng (không chặn cài đặt)
    # Thư viện cần thiết: openai, google-generativeai, requests, pytesseract, Pillow
    # Đã được cài trong Dockerfile, nếu thiếu sẽ báo lỗi khi sử dụng tính năng
    'data': [
        'security/ir.model.access.csv',
        'views/ai_config_views.xml',
        'views/ai_document_summary_views.xml',
        'views/ai_ocr_views.xml',
        'views/ai_assistant_wizard_views.xml',
        'views/ai_menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}

