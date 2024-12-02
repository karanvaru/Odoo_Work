# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CreateProductVariantWizard(models.TransientModel):
    _name = 'create.product.variant.wizard'
    _description = 'Create Product Variant'

    product_variant_create_ids = fields.One2many(
        'create.product.variant.line.wizard',
        'product_wizard_id'
    )

    def action_confirm(self):
        if self.product_variant_create_ids:
            vals_dict = {}
            val_engine_number = {}
            val_serial_number = {}
            val_vin_number = {}
            for res in self.product_variant_create_ids:
                if res.attribute_id.id not in vals_dict:
                    vals_dict[res.attribute_id.id] = []
                val_engine_number[res.value_id.id] = res.engine_number
                val_serial_number[res.value_id.id] = res.serial_number
                vals_dict[res.attribute_id.id].append(res.value_id.id)
                val_vin_number[res.value_id.id] = res.value_id.name
            num_attribute_id = self.env.ref('ki_sh_auto_part_extend.product_attribute_id_name').id
            productTemplate = self.env['product.template'].search([('id', '=', self._context.get('active_id'))])

            if self._context.get('active_model') == 'product.template' and self._context.get('active_id'):
                if productTemplate:
                    numberAttribute = False
                    for i in productTemplate.attribute_line_ids:
                        if i.attribute_id.id == num_attribute_id:
                            numberAttribute = i
                            break
                    att_line_ids = {
                        'attribute_id': num_attribute_id,
                        'value_ids': vals_dict[num_attribute_id]
                    }
                    if numberAttribute == False:
                        productTemplate.write({
                            'attribute_line_ids': [(0, 0, att_line_ids)]
                        })
                    else:
                        numberAttribute.write({
                            'value_ids': [(4, i) for i in vals_dict[num_attribute_id]]
                        })

                products = self.env['product.product'].search([('product_tmpl_id', '=', productTemplate.id)])
                for product in products:
                    pnumberatt = False
                    for pattribute in product.product_template_attribute_value_ids:
                        if pattribute.attribute_id.id == num_attribute_id:
                            pnumberatt = pattribute
                            break
                    if pnumberatt and pnumberatt.product_attribute_value_id.id in val_engine_number:
                        product.engine_number = val_engine_number[pnumberatt.product_attribute_value_id.id]
                    if pnumberatt and pnumberatt.product_attribute_value_id.id in val_serial_number:
                        product.serial_number = val_serial_number[pnumberatt.product_attribute_value_id.id]
                    if pnumberatt and pnumberatt.product_attribute_value_id.id in val_vin_number:
                        product.vin_number = val_vin_number[pnumberatt.product_attribute_value_id.id]


class CreateProductVariantLineWizard(models.TransientModel):
    _name = 'create.product.variant.line.wizard'
    _description = 'Create Product Variant Line'

    @api.model
    def default_get(self, fields):
        res = self.env.ref('ki_sh_auto_part_extend.product_attribute_id_name').id
        defaults = super(CreateProductVariantLineWizard, self).default_get(fields)
        defaults.update({
            'attribute_id': res
        })
        return defaults

    attribute_id = fields.Many2one(
        'product.attribute',
        string='Attributes'
    )
    value_id = fields.Many2one(
        'product.attribute.value',
        string='VIN Number'
    )
    product_wizard_id = fields.Many2one(
        'create.product.variant.wizard'
    )
    engine_number = fields.Char(
        string="Engine Number"
    )
    serial_number = fields.Char(
        string="Serial Number"
    )


