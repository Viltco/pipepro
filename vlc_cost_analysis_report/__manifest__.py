# -*- coding: utf-8 -*-
{
    'name': "Cost Analysis Report",

    'summary': """
        Cost Analysis Report""",

    'description': """
        Cost Analysis Report
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'mrp',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp'],

    # always loaded
    'data': [
        'reports/cost_analysis_template.xml',
        'reports/cost_analysis_report.xml',
        # 'views/views.xml',
    ],

}
