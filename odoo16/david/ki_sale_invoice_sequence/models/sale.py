# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    category_type = fields.Selection(
        selection=[
            ('rental', 'Rental'),
            ('service', 'Service'),
            ('parts', 'Parts'),
            ('sale', 'Sales')
        ],
        string='Category Type',
        # required=True
    )

    def _prepare_invoice(self):
        res = super(SaleOrderInherit, self)._prepare_invoice()
        res['category_type'] = self.category_type
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # for vals in vals_list:
        #     if 'company_id' in vals:
        #         self = self.with_company(vals['company_id'])
        #     if 'category_type' in vals:
        #         sequence = self.env['quote.sequence.mapping'].search([('category_type', '=', vals['category_type'])],
        #                                                              limit=1)
        #         if sequence and sequence.sequence_id:
        #             vals['name'] = sequence.sequence_id.next_by_id()
        #         else:
        #             if vals.get('name', _("New")) == _("New"):
        #                 seq_date = fields.Datetime.context_timestamp(
        #                     self, fields.Datetime.to_datetime(vals['date_order'])
        #                 ) if 'date_order' in vals else None
        #                 vals['name'] = self.env['ir.sequence'].next_by_code(
        #                     'sale.order', sequence_date=seq_date) or _("New")
        #     else:
        #         if vals.get('name', _("New")) == _("New"):
        #             seq_date = fields.Datetime.context_timestamp(
        #                 self, fields.Datetime.to_datetime(vals['date_order'])
        #             ) if 'date_order' in vals else None
        #             vals['name'] = self.env['ir.sequence'].next_by_code(
        #                 'sale.order', sequence_date=seq_date) or _("New")

        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            sequence = False
            if 'category_type' in vals:
                sequence = self.env['quote.sequence.mapping'].search([('category_type', '=', vals['category_type'])],
                                                                     limit=1)
            if sequence and sequence.sequence_id:
                vals['name'] = sequence.sequence_id.next_by_id()
            elif vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(
                    vals.get('date_order'))) if 'date_order' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _("New")

        return super(models.Model, self).create(vals_list)
        SaleOrder = models.getModel('sale.order')
        SaleOrder.create = create
