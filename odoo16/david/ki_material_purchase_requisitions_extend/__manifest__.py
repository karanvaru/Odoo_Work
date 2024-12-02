# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Material Purchase Requisitions Extend",
    'summary': """Material Purchase Requisitions Extend""",
    'description': """Material Purchase Requisitions Extend""",
    "version": "1.3.2",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    "depends": [
        'material_purchase_requisitions',
        'stock'
        # 'sale',
        # 'ki_job_card_extend',
    ],
    "data": [
        'views/purchase_requisition_view.xml'
    ],
    "application": False,
    'installable': True,
}
