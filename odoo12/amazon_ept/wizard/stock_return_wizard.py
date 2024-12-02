from odoo import models, fields, api


class stock_return_picking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.multi
    def _create_returns(self):
        new_picking, pick_type_id = super(stock_return_picking, self)._create_returns()
        self.env['stock.picking'].browse(new_picking).write({'is_fba_wh_picking': False})
        return new_picking, pick_type_id
