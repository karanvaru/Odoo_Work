from odoo import models, fields, api


class InventorySmartButton(models.Model):
    _inherit = 'stock.picking'

    count = fields.Integer(compute='compute_count')
    journal_count = fields.Integer(compute='compute_journal_count')

    def compute_journal_count(self):
        for record in self:
            entry = record.env['account.move'].search_count([('stock_move_id.picking_id', '=', record.id)])
            if entry:
                record.journal_count = entry
            else:
                record.journal_count = 0

    def get_stock_move(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Moves',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': [('picking_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_stock_journal(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('stock_move_id.picking_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_count(self):
        for record in self:
            entry = record.env['stock.move'].search_count([('picking_id', '=', record.id)])
            if entry:
                record.count = entry
            else:
                record.count = 0
