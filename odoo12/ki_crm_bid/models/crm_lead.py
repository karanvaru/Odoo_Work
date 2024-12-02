
from odoo import models, fields, api, _

class CRM_LEAD(models.Model):
    _inherit = 'crm.lead'


#     def _compute_access_url(self):
#         super(CRM_LEAD, self)._compute_access_url()
#         for order in self:
#             order.access_url = '/my/lead/%s' % (order.id)
