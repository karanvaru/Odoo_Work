# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
#import odoo.addons.decimal_precision as dp odoo13
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class SupportInvoiceLine(models.Model):
    _name = "support.invoice.line"
    _description = "Support Invoice Line"
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    name = fields.Text(
        string='Description'
    )
    price_unit = fields.Float(
        string='Unit Price',
#        digits=dp.get_precision('Product Price') odoo13
        digits='Product Price',
        
    )
    quantity = fields.Float(
        string='Quantity',
#        digits=dp.get_precision('Product Unit of Measure'), odoo13
        digits='Product Unit of Measure',
        required=True,
        default=1
    )
    product_uom_qty = fields.Float(
#        string='Quantity',  odoo13
        string='Product UOM Quantity', 
#        digits=dp.get_precision('Product Unit of Measure'), odoo13
        digits='Product Unit of Measure',
        required=True, default=1.0,
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
    )
    support_id = fields.Many2one(
        'helpdesk.support',
        string='Support Invoice',
    )
    tax_id = fields.Many2many(
        'account.tax',
        string='Taxes',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account'
    )
    is_invoice = fields.Boolean(
        string='Is Invoice Create',
        # tracking=True,
        default=False,
        copy=False,
    )

#    @api.multi odoo13
    def _compute_tax_id(self):
        for line in self:
            fpos = line.support_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id
            line.tax_id = taxes

#    @api.multi odoo13
    @api.onchange('product_id')
    def custom_product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            vals['product_uom'] = self.product_id.uom_id.id
        vals['price_unit'] = self.product_id.lst_price
        vals['name'] = self.product_id.name
        self.update(vals)
        return {'domain': domain}
        
    @api.onchange('product_uom', 'product_uom_qty')
    def custom_product_uom_change(self):
        if not self.product_uom:
            self.price_unit = 0.0
            return
        if self.support_id.partner_id.property_product_pricelist and self.support_id.partner_id:
            price = self.support_id.partner_id.property_product_pricelist._get_product_price(
                self.product_id, self.product_uom_qty or 1.0) #16
            product = self.product_id.with_context(
                lang=self.support_id.partner_id.lang,
                partner=self.support_id.partner_id.id,
                quantity=self.product_uom_qty,
                date_order=fields.Datetime.now,
                pricelist=self.support_id.partner_id.property_product_pricelist.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position'),
            )
            # self.price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, self.tax_id)
            self.price_unit = self.env['account.tax']._fix_tax_included_price(price, product.taxes_id, self.tax_id)#16

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
