from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    """Method inherited by Dhruvi [1-10-2018]
    to pass producturl value while creating stock.move"""

    @api.multi
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name,
                               origin, values, group_id):
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom,
                                                            location_id, name, origin, values,
                                                            group_id)
        res.update({'producturl': values.get('producturl', False)})
        return res
