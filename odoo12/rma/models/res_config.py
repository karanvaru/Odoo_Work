# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class RmaConfigSettings(models.TransientModel):
    # _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    # selection = [
    #     ('all', 'All'),
    #     ('done', 'Only Done'),
    # ]

    allow_quote_cancellation = fields.Boolean(
        string="Allow cancellation of order quote.", help="Customer can cancel quotation order.")
    process_do_state = fields.Selection([
        ('all', 'All'),
        ('done', 'Only Done'),
    ], string="Process state")
    rma_term_condition = fields.Html(string="Term And Conditions")
    days_for_rma = fields.Integer(string="Return Policy",
                                  help="Number of days upto which customer can request for RMA after delivery done.")
    rma_day_apply_on = fields.Selection(
        [("so_date", "Order Date"), ("do_date", "Delivery Date")], string="Apply On")
    module_repair = fields.Boolean(
        "Allow repair of product in RMA.", help='Allows to manage all product repairs.\n')
    repair_location_id = fields.Many2one(
        'stock.location', 'Repair Location')
    show_rma_stage = fields.Boolean(string="Show RMA stage to customer.")

    @api.one
    def set_values(self):
        super(RmaConfigSettings, self).set_values()
        ir_default = self.env['ir.default'].sudo()

        ir_default.set('res.config.settings', 'allow_quote_cancellation', self.allow_quote_cancellation)
        ir_default.set('res.config.settings', 'process_do_state', self.process_do_state)
        ir_default.set('res.config.settings', 'rma_term_condition', self.rma_term_condition)
        ir_default.set('res.config.settings', 'days_for_rma', self.days_for_rma)
        ir_default.set('res.config.settings', 'rma_day_apply_on', self.rma_day_apply_on)
        ir_default.set('res.config.settings', 'repair_location_id', self.repair_location_id.id)
        ir_default.set('res.config.settings', 'show_rma_stage', self.show_rma_stage)
        return True

    @api.model
    def get_values(self):
        res = super(RmaConfigSettings, self).get_values()
        ir_default = self.env['ir.default'].sudo()
        allow_quote_cancellation = ir_default.get('res.config.settings', 'allow_quote_cancellation')
        process_do_state = ir_default.get('res.config.settings', 'process_do_state')
        rma_term_condition = ir_default.get(
            'res.config.settings', 'rma_term_condition') or "About Return and Refund Policies Most e-commerce stores should have a Return or Refund Policy, just as it should have a Privacy Policy. Wikipedia defines Returning as: In retail, returning is the process of a customer taking previously purchased merchandise back to the retailer, and in turn, receiving a cash refund, exchange for another item (identical or different), or a store credit. Most countries industry regulations require that stores (even digital) must have this kind of policy. eBay’s help pages mention that stores with return policies published online sell better (however, eBay requires all stores to have this policy): We’ve found that items with clear return policies typically sell better than items that don’t. A Terms and Conditions agreement for your store might be a good idea, but it is not required by law. If you’re looking for a Terms and Conditions agreement, you can generate it with our generator. What to include in your policy Your Return Policy should include at least the following sections: the numbers of days a customer can notify you for wanting to return an item after they received it what kind of refund you will give to the customer after the item is returned: another similar product, a store credit, etc. who will pay for the return shipping"
        days_for_rma = ir_default.get('res.config.settings', 'days_for_rma')
        rma_day_apply_on = ir_default.get('res.config.settings', 'rma_day_apply_on') or "do_date"
        show_rma_stage = ir_default.get('res.config.settings', 'show_rma_stage')
        repair_location_id = ir_default.get('res.config.settings', 'repair_location_id')
        res.update({
            'allow_quote_cancellation': allow_quote_cancellation,
            'process_do_state': process_do_state,
            'rma_term_condition': rma_term_condition,
            "days_for_rma": days_for_rma,
            "rma_day_apply_on": rma_day_apply_on,
            "repair_location_id": repair_location_id,
            "show_rma_stage": show_rma_stage,
        })
        return res

    # @api.onchange('days_for_rma')
    # def on_change_like(self):
    #     if self.days_for_rma < 0:
    #         raise UserError(('Number of days can not be negative.'))
    #         self.days_for_rma = 0
