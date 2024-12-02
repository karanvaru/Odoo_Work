# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_cost_estimation_accounting = fields.Boolean(string="Budget Integration")
    multiple_cost_estimate = fields.Boolean(string="Multiple Cost Estimate", default=True)
    cancel_non_conf_ce = fields.Boolean(string="Cancel Non Confirmed Cost Estimate")
    one_approved_cost_est = fields.Boolean(string="One Approved Cost Estimate")
    quotation_restriction = fields.Boolean(string="Quotation Restriction")
    quotation_description_product = fields.Selection([
        ('sp', 'Salable Product Description'),
        ('ci', 'Cost Item  Description'),
    ], string='Product Quotation Description', default='sp')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        multiple_cost_estimate = params.get_param('multiple_cost_estimate', default=True)
        one_approved_cost_est = params.get_param('one_approved_cost_est', default=False)
        cancel_non_conf_ce = params.get_param('cancel_non_conf_ce', default=False)
        quotation_restriction= params.get_param('quotation_restriction', default=False)
        quotation_description_product = params.get_param('quotation_description_product', default='sp')
        res.update(
            multiple_cost_estimate=multiple_cost_estimate,
            one_approved_cost_est=one_approved_cost_est,
            cancel_non_conf_ce=cancel_non_conf_ce,
            quotation_description_product=quotation_description_product,
            quotation_restriction=quotation_restriction,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("multiple_cost_estimate", self.multiple_cost_estimate)
        self.env['ir.config_parameter'].sudo().set_param("one_approved_cost_est", self.one_approved_cost_est)
        self.env['ir.config_parameter'].sudo().set_param("cancel_non_conf_ce", self.cancel_non_conf_ce)
        self.env['ir.config_parameter'].sudo().set_param("quotation_restriction", self.quotation_restriction)
        self.env['ir.config_parameter'].sudo().set_param("quotation_description_product",
                                                         self.quotation_description_product)

    @api.onchange('multiple_cost_estimate')
    def onchange_multiple_cost_estimate(self):
        if not self.multiple_cost_estimate:
            self.cancel_non_conf_ce = False

    @api.onchange('one_approved_cost_est')
    def onchange_one_approved_cost_est(self):
        if not self.one_approved_cost_est:
            self.cancel_non_conf_ce = False
