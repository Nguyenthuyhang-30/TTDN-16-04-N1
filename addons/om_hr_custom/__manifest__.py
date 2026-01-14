# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 17 HR Management',
    'version': '17.0.1.0.7',
    'category': 'Human Resources',
    'summary': 'Quản lý nhân sự - Human Resources Management',
    'images': [
        'static/description/icon.png',
    ],
    'description': """
        Module quản lý nhân sự cho Odoo 17
        ===================================
        
        Tính năng:
        - Quản lý thông tin nhân viên
        - Xem danh sách nhân viên
        - Quản lý phòng ban
        - Chấm công: giờ vào, giờ ra, giờ nghỉ, số giờ làm
        - Bảng lương: tính lương theo số công, thưởng, phạt
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_payroll_views.xml',
        'security/ir.model.access.attendance_payroll.xml',
        'security/ir.model.access.contract.xml',
        'views/hr_actions.xml',
        'views/hr_dashboard_views.xml',
        'views/hr_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'om_hr_custom/static/src/js/hr_dashboard.js',
            'om_hr_custom/static/src/css/employee_form.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

