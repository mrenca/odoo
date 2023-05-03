# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase approval',
    'version': '1.0',
    'author': "William Tobar",
    'category': 'Inventory/Purchase',
    'summary': 'Purchase orders approvals',
    'website': 'https://www.odoo.com/app/purchase',
    'depends': ['purchase'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/custom_workflow.xml',
        'views/purchase_report_inherit.xml',
    ]
}
