from odoo import api, fields, models, _


class CrmLeadInherit(models.Model):
    _inherit = "crm.lead"

    lead_date = fields.Date('Lead Date')
    kw_capacity = fields.Float('KW Capacity')
    lead_status = fields.Char('Current Status')
    user_comment = fields.Text('Comment of Assigned person')
