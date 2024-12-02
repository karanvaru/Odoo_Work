from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm
        if self.opportunity_id:
            self.opportunity_id.action_set_won_rainbowman()
        return res

