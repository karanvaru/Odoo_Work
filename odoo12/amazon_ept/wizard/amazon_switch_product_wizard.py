from odoo import models, fields, api
from odoo.exceptions import Warning


class amazon_switch_product_wizard(models.TransientModel):
    _name = "amazon.switch.product.wizard"
    _description = 'amazon.switch.product.wizard'

    from_fulfillment_by = fields.Selection(
        [('MFN', 'Manufacturer Fulfillment Network'), ('AFN', 'Amazon Fulfillment Network')],
        string="From Fulfillment By", default='MFN')
    to_fulfillment_by = fields.Selection(
        [('MFN', 'Manufacturer Fulfillment Network'), ('AFN', 'Amazon Fulfillment Network')],
        string="To Fulfillment By", default='AFN')
    instance_id = fields.Many2one("amazon.instance.ept", "Instance")
    amazon_product_ids = fields.Many2many("amazon.product.ept", 'amazon_product_switch_rel',
                                          'wizard_id', 'amazon_product_id', "Amazon Product",
                                          readonly=False)

    @api.onchange('from_fulfillment_by')
    def on_change_from_fulfillment(self):
        for record in self:
            record.to_fulfillment_by = False

#     @api.multi
#     def switch_products(self):
#         if self.from_fulfillment_by == self.to_fulfillment_by:
#             raise Warning("Source and Destination Network Must be different")
#         if not self.amazon_product_ids:
#             return True
#         amazon_product_obj = self.env['amazon.product.ept']
#         if self.from_fulfillment_by == 'MFN' and self.to_fulfillment_by == 'AFN':
#             amazon_product_obj.switch_product_from_mfn_to_afn(self.instance_id,
#                                                               self.amazon_product_ids)
#         elif self.from_fulfillment_by == 'AFN' and self.to_fulfillment_by == 'MFN':
#             amazon_product_obj.switch_product_from_afn_to_mfn(self.instance_id,
#                                                               self.amazon_product_ids)
#         return True
