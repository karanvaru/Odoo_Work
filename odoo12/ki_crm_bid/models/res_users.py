from odoo import models, fields, api


class RES_users(models.Model):
    _inherit = 'res.users'

    has_bid_access = fields.Boolean(
        "Create Bid Access"
    )

    def write(self, values):
        if 'has_bid_access' in values:
            if values['has_bid_access'] == True:
                values.update({
                    'groups_id': [(4, self.env.ref('ki_crm_bid.group_enable_bid_access').id)]
                })
            else:
                values.update({
                    'groups_id': [(3, self.env.ref('ki_crm_bid.group_enable_bid_access').id)]
                })
        return super(RES_users, self).write(values)
