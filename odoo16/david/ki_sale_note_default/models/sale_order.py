# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    note_template_id = fields.Many2one(
        'sale.default.note.template',
        string='Note Template',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        note_template = self.env['sale.default.note.template'].search([('partner_ids', 'in', self.partner_id.id)],
                                                                      limit=1, order="id asc")
        self.note_template_id = False
        if note_template:
            self.update({
                'note_template_id': note_template.id,
            })
        return super(SaleOrderInherit, self)._onchange_partner_id_warning()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    note_template_id = fields.Many2one(
        'sale.default.note.template',
        string='Note Template',
    )
    product_note = fields.Char(
        string='Note'
    )

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrderLine, self).default_get(fields_list)
        if self._context.get('default_note_template_id', False):
            notes = self.env['sale.default.note.template'].browse(self._context.get('default_note_template_id', False))
            if 'display_type' in res:
                if res['display_type'] == 'line_note':
                    res.update({
                        'name': notes.note,
                    })
        return res

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        if self._context.get('default_note_template_id', False):
            notes = self.env['sale.default.note.template'].browse(self._context.get('default_note_template_id', False))
            self.product_note = False
            if self.product_id == notes.product_id:
                self.update({
                    'product_note': notes.product_note,
                })
                # order_id = self
                # # print("=================== self.order_id", self.order_id)
                # # order_id = self.env['sale.order'].browse(self._context.get('active_id'))
                # print("================ order_id", order_id)
                # print("================ self._context", self._context)
                # # order_line = self.env['sale.order.line']
                # new_line = self.create({
                #     # 'order_id': order_id,
                #     'display_type': 'line_note',
                #     'name': notes.product_note,
                # })
                # print("================== 92 new_line", new_line)
        return super(SaleOrderLine, self)._onchange_product_id_warning()
