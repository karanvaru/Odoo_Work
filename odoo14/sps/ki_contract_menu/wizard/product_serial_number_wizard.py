from odoo import api, fields, models, _


class ProductSerialNumberWizard(models.TransientModel):
    _name = 'product.serial.number.wizard'
    _description = 'Product Value Set'

    product_template_create_ids = fields.One2many(
        'product.serial.number.line.wizard',
        'product_wizard_id'
    )

    def action_confirm(self):
        if self.product_template_create_ids:
            vals_dict = {}
            val_serial_Number = {}
            val_printer_Number = {}
            for res in self.product_template_create_ids:
                if res.attribute_id.id not in vals_dict:
                    vals_dict[res.attribute_id.id] = []
                val_serial_Number[res.value_id.id] = res.barcode
                val_printer_Number[res.value_id.name] = res.value_id
                vals_dict[res.attribute_id.id].append(res.value_id.id)
            num_attribute_id = self.env.ref('ki_contract_menu.product_attribute_id_name').id
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
                        if pnumberatt and pnumberatt.product_attribute_value_id.id in val_serial_Number:
                            product.barcode = val_serial_Number[pnumberatt.product_attribute_value_id.id]

                        if pnumberatt and pnumberatt.name in val_printer_Number:
                            product.default_code = pnumberatt.name


class ProductSerialNumberWizardLine(models.TransientModel):
    _name = 'product.serial.number.line.wizard'
    _description = 'Product Value Line'

    @api.model
    def default_get(self, fields):
        res = self.env.ref('ki_contract_menu.product_attribute_id_name').id
        defaults = super(ProductSerialNumberWizardLine, self).default_get(fields)
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
        string='Values'
    )

    barcode = fields.Char(
        string='Serial Number'
    )

    product_wizard_id = fields.Many2one(
        'product.serial.number.wizard'
    )
