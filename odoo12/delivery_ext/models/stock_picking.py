from odoo import fields, models, api
from odoo.addons.delivery.models.stock_picking import StockPicking as BaseStockPicking


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        res = super(BaseStockPicking, self).action_done()
        for pick in self:
            if pick.carrier_id:
                if pick.carrier_id.integration_level == 'rate_and_ship' and pick.picking_type_code != 'incoming':
                    pick.send_to_shipper()
                pick._add_delivery_cost_to_so()
        return res

    BaseStockPicking.action_done = action_done
