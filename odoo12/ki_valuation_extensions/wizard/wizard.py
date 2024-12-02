from odoo import models, fields, api
import datetime
import calendar


class Wizard(models.TransientModel):
    _name = 'stock.valuation.generate.wizard'
    _description = "Wizard: stock.valuation.generate.wizard "

    def _default_start_date(self):
        return datetime.date.today().replace(day=1)
    def _default_end_date(self):
        date=datetime.date.today()
        res = calendar.monthrange(date.year, date.month)
        return datetime.date.today().replace(day=res[1])

    start_date = fields.Date(string="Start Date", required=True, default=_default_start_date )
    end_date = fields.Date(default=_default_end_date, required=True)
    # product_categ_id = fields.Many2many('product.category', string="Product Category")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env['res.company']._company_default_get('stock.valuation.generate.wizard'))
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type")
    # is_move_sync = fields.Boolean(string="Receipts Move Update")
    # is_mrp_move_sync = fields.Boolean(string="MRP Move Update")
    # is_delivery_move_sync = fields.Boolean(string="Delivery Move Update")

    def regenerea_valuation_wizard_action_button(self):
        moves = self.env['stock.move'].search([
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('company_id', '=', self.company_id.id),
            # ('product_id.categ_id', 'not in', self.product_categ_id.ids),
            ('state', '=', 'done'),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('account_move_ids', '=', False),
        ], order="date asc")
        if self.picking_type_id.code == 'incoming':
            moves.stock_move_syc_custom()
            moves.action_generate_valuations()
        elif self.picking_type_id.code == 'mrp_operation':
            moves.stock_mrp_move_syc_custom()
            moves.action_generate_valuations()
        elif self.picking_type_id.code == 'outgoing':
            moves.action_generate_valuations()
        else:
            moves.action_generate_valuations()

    # def regenerea_valuation_wizard_action_button(self):
    #
    #     moves = self.env['stock.move'].search([
    #         ('date', '>=', self.start_date),
    #         ('date', '<=', self.end_date),
    #         ('company_id', '=', self.company_id.id),
    #         # ('product_id.categ_id', 'not in', self.product_categ_id.ids),
    #         ('state', '=', 'done'),
    #         ('picking_type_id', '=', self.picking_type_id.id,
    #          'account_move_ids','=',False),
    #     ], order="date asc")
    #     print("The values of moves is", moves)
    #     for move in moves:
    #         print("mmmmmmmmmmmm", move,move.account_move_ids)
    #     # if self.picking_type_id.code == 'incoming':
    #     #     moves.stock_move_syc_custom()
    #     #     moves.action_generate_valuations()
    #     # elif self.picking_type_id.code == 'mrp_operation':
    #     #     moves.stock_mrp_move_syc_custom()
    #     #     moves.action_generate_valuations()
    #     # elif self.picking_type_id.code == 'outgoing':
    #     #     moves.action_generate_valuations()
    #     # else:
    #     #     moves.action_generate_valuations()

        # mrp_move = self.env.['mrp.production'].search([
        #     ('date', '>=',)])
#         act = self.env.ref('stock.stock_move_action').read([])[0]
#         act['domain'] = [('date', '>=', self.start_date), ('date', '<=', self.end_date),('company_id', '=', self.company_id.id), ('state', '=', 'done')]
#         return act

    # def regenerea_valuation_wizard_action_button(self):
    #
    #     if self.start_date and self.end_date:
    #         rec = self.env['stock.move'].search(
    #             [('date', '>=', self.start_date), ('date', '<=', self.end_date)])
    #     elif self.start_date:
    #         rec = self.env['stock.move'].search([('date', '>=', self.start_date)])
    #     else:
    #         rec = self.env['stock.move'].search([('date', '<=', self.end_date)])
    #     return
