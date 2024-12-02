# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields,api,_
from odoo.exceptions import UserError


class AffiliateVisitInherit(models.Model):
    _inherit = "affiliate.visit"

    affiliate_method = fields.Selection(selection_add=[('parentcommission', 'Parent Commission')])
    parent_affiliate =fields.Many2one(string='Parent Affiliate', comodel_name='res.partner', related='affiliate_partner_id.parent_affiliate')

    def action_confirm(self):
        result = super(AffiliateVisitInherit,self).action_confirm
        if result and self.affiliate_partner_id.parent_affiliate and self.affiliate_method == 'pps':
            vals = {
                'affiliate_method': 'parentcommission',
                'affiliate_type': self.affiliate_type,
                'type_id': self.type_id,
                'type_name': self.type_name,
                'is_converted': self.is_converted,
                'sales_order_line_id': self.sales_order_line_id.id,
                'affiliate_partner_id': self.affiliate_partner_id.parent_affiliate.id,
                'affiliate_key': self.affiliate_partner_id.parent_affiliate.res_affiliate_key,
                'convert_date': fields.Datetime.to_string(fields.Datetime.now()),
                'price_total': self.price_total,
                'affiliate_program_id': self.affiliate_program_id.id,
                'state': 'draft',
                'product_quantity': self.product_quantity,
            }
            parent_visit_create = self.env['affiliate.visit'].sudo().create(vals)
            _logger.info("----------parent_visit_create--%r----", parent_visit_create)
            status = parent_visit_create._calcParentComsn()
        return result


    def _calcParentComsn(self):
        self.amt_type = str(self.affiliate_program_id.parent_commision)+" % parent comsn"
        self.commission_amt = self.price_total * (self.affiliate_program_id.parent_commision/100)
        self.state = 'confirm'
        return True

    # method call from server action override
    @api.model
    def create_invoice(self):

        # get the value of enable ppc from settings
        ConfigValues = self.env['res.config.settings'].sudo().website_constant()
        check_enable_ppc = ConfigValues.get('enable_ppc')
        aff_vst = self._context.get('active_ids')
        act_invoice = self.env['account.invoice']
        # check the first visit of context is ppc or pps and enable pps
        affiliate_method_type = self.browse([aff_vst[0]]).affiliate_method
        _logger.info('----server action affiliate_method--%r--------', self.browse([aff_vst[0]]).affiliate_method)
        if affiliate_method_type == 'ppc' and (not check_enable_ppc):
            raise UserError("Pay per click is disable, so you can't generate it's invoice")

        invoice_ids = []
        for v in aff_vst:
            vst = self.browse([v])

            if vst.state == 'confirm':
                inv_id = act_invoice.create({
                    'partner_id': vst.affiliate_partner_id.id,
                    'type': 'in_invoice',
                    'date_invoice': fields.Datetime.to_string(fields.Datetime.now()),
                })
                if vst.sales_order_line_id and vst.affiliate_method == "pps":
                    dic = {
                        'name': "Type " + vst.affiliate_type + " on Pay Per Sale ",
                        'quantity': 1,
                        'price_unit': vst.commission_amt,
                        'invoice_id': inv_id.id,
                        'product_id': ConfigValues.get('aff_product_id'),
                    }
                elif (not vst.sales_order_line_id) and vst.affiliate_method == "ppc":
                    dic = {
                        'name': "Type " + vst.affiliate_type + " on Pay Per Click ",
                        'price_unit': vst.commission_amt,
                        'quantity': 1,
                        'invoice_id': inv_id.id,
                        'product_id': ConfigValues.get('aff_product_id'),

                    }
                else:
                    dic = {
                        'name': "Type " + vst.affiliate_type + " on Parent Commission ",
                        'price_unit': vst.commission_amt,
                        'quantity': 1,
                        'invoice_id': inv_id.id,
                        'product_id': ConfigValues.get('aff_product_id'),

                    }
                vst.state = 'invoice'
                vst.act_invoice_id = inv_id.id
                line = self.with_context({'journal_id': inv_id.journal_id.id}).env['account.invoice.line'].create(
                    dic)
                invoice_ids.append(inv_id)

        # _logger.info('----invoice_ids--%r--------', invoice_ids)
        # _logger.info('----aff_vst--%r--------', aff_vst)
        msg = str(len(invoice_ids)) + ' records has been invoiced out of ' + str(len(aff_vst))

        partial_id = self.env['wk.wizard.message'].create({'text': msg})
        return {
            'name': "Message",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wk.wizard.message',
            'res_id': partial_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
