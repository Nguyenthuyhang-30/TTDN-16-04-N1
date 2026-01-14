{
    'name': 'Quản lý khách hàng',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Hệ thống quản lý khách hàng, đơn hàng, sản phẩm và hỗ trợ',
    'description': """
        Module quản lý khách hàng cho Odoo 17
        ======================================
        
        Tính năng:
        - Quản lý thông tin khách hàng
        - Quản lý đơn hàng và chi tiết đơn hàng
        - Quản lý sản phẩm và tồn kho
        - Hỗ trợ khách hàng và đánh giá
        - Gửi email và thông báo
        - Thống kê và bảng xếp hạng khách hàng
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'om_hr_custom',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/customer_views.xml',
        'views/product_views.xml',
        'views/order_views.xml',
        'views/customer_support_views.xml',
        'views/email_notification_views.xml',
        'views/customer_dashboard_views.xml',
        'views/customer_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'quan_ly_khach_hang/static/src/js/customer_dashboard.js',
            'quan_ly_khach_hang/static/src/css/customer_form.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

