from . import models

def post_init_hook(env):
    """Sửa dữ liệu sau khi module được cài đặt hoặc upgrade"""
    try:
        # Sửa các record có document_id không hợp lệ
        env.cr.execute("""
            UPDATE ai_document_summary 
            SET document_id = NULL 
            WHERE document_id IS NOT NULL 
            AND document_id NOT IN (
                SELECT id FROM om_document_incoming WHERE id IS NOT NULL
            )
        """)
        env.cr.commit()
    except Exception:
        env.cr.rollback()
from . import wizard
from . import controllers

