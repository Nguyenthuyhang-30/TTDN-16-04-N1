# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migration script để chuyển đổi field gemini_model từ Char sang Selection
    """
    # Xóa column cũ nếu tồn tại (sẽ được tạo lại với type mới)
    cr.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ai_config' 
        AND column_name = 'gemini_model'
    """)
    
    if cr.rowcount > 0:
        # Nếu field tồn tại và là text/varchar, xóa nó
        cr.execute("""
            ALTER TABLE ai_config DROP COLUMN IF EXISTS gemini_model
        """)

