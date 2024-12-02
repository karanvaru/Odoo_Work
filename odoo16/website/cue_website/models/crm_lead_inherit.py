from odoo import fields, models, api


class CrmLeadInherits(models.Model):
    _inherit = 'crm.lead'
    _description = 'Crm Lead'

    web_lead_type = fields.Selection(
        [
            ('partner', 'Partner'),
            ('contact', 'Contact'),
            ('user', 'User')
        ],
        string='Lead Type',
        readonly=True
    )

    home_status = fields.Selection(
        [
            ('upgrade_existing_system', 'Upgrade Existing System'),
            ('explore_new_system', 'Explore New System'),
        ],
        string='Home Status',
        readonly=False
    )
    exist_partner = fields.Selection(
        [
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        string='Exist Partner',
        readonly=True
    )
    lead_city_id = fields.Many2one(
        'res.city',
        string="City Select"
    )

    # @api.model
    # def create(self, vals):
    #     res = super(CrmLeadInherits, self).create(vals)
    #     if "website_id" in self._context:
    #         if 'web_lead_type' not in vals:
    #             res['web_lead_type'] = 'contact'
    #         if 'home_status' in vals:
    #             res['web_lead_type'] = 'user'
    #         res['web_lead_type'] = 'partner'
    #     return res
