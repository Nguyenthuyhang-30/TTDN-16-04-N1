# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quản lý văn bản',
    'version': '17.0.1.0.7',
    'category': 'Administration',
    'summary': 'Quản lý văn bản - Document Management',
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'description': """
        Module quản lý văn bản cho Odoo 17
        ===================================
        
        Tính năng:
        - Quản lý loại văn bản
        - Quản lý văn bản đến
        - Quản lý văn bản đi
        - Theo dõi trạng thái văn bản
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'om_hr_custom',
        'quan_ly_khach_hang',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'security/ir.model.access.digital_signature.xml',
        'data/ir_cron_data.xml',
        # Email templates - cần module 'mail' được cài đặt
        # BƯỚC 1: Cài đặt module "Discuss" (mail) trong Apps
        # BƯỚC 2: Uncomment dòng sau và upgrade lại module
        'data/email_template_data.xml',
        'views/loai_van_ban_views.xml',
        'views/van_ban_den_views.xml',
        'views/van_ban_di_views.xml',
        'views/sign_document_wizard_views.xml',
        'views/chung_thu_so_views.xml',
        'views/chu_ky_so_views.xml',
        'views/quy_trinh_duyet_views.xml',
        'views/lich_su_van_ban_views.xml',
        'views/document_reminder_views.xml',
        'views/document_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'quan_ly_van_ban/static/src/js/document_dashboard.js',
            'quan_ly_van_ban/static/src/css/document_form.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

