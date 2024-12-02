from odoo import api, fields, models, _


class UpdateSaleStockWizard(models.TransientModel):
    _name = 'update.sale.stock.wizard'

    start_date = fields.Date(
        'Start Date',
        required=True
    )
    end_date = fields.Date(
        'End Date',
        required=True
    )
    type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('stock_move', 'Stock Move')
    ], string="Type")

    def action_submit(self):
        if self.type == 'sale':
            sale_order = self.env['sale.order'].search([
                ('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date)])
            for rec in sale_order:
                rec.picking_ids.mapped('move_lines').mapped('account_move_ids').update({
                    'custom_source_document': rec.name
                })
                rec.invoice_ids.mapped('move_id').update({
                    'custom_source_document': rec.name
                })

        if self.type == 'purchase':
            purchase_order = self.env['purchase.order'].search([
                ('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date)])
            for rec in purchase_order:
                rec.picking_ids.mapped('move_lines').mapped('account_move_ids').update({
                    'custom_source_document': rec.name
                })
                rec.invoice_ids.mapped('move_id').update({
                    'custom_source_document': rec.name
                })

        if self.type == 'stock_move':
            stock_move = self.env['stock.move'].search([
                ('date', '>=', self.start_date), ('date', '<=', self.end_date),
                ('categ_id', '=', False)])
            for rec in stock_move:
                rec.update({
                    'categ_id': rec.product_id.categ_id.id
                })

