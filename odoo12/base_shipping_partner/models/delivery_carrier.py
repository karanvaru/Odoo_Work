from odoo import models, fields, api, _

# https://gist.github.com/kennwilson/3902548
COUNTRIES_WITHOUT_POSTCODES = [
    'AO', 'AG', 'AW', 'BS', 'BZ', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CF', 'KM',
    'CG', 'CD', 'CK', 'CI', 'DJ', 'DM', 'GQ', 'ER', 'FJ', 'TF', 'GM', 'GH',
    'GD', 'GN', 'GY', 'HK', 'IE', 'JM', 'KE', 'KI', 'MO', 'MW', 'ML', 'MR',
    'MU', 'MS', 'NR', 'AN', 'NU', 'KP', 'PA', 'QA', 'RW', 'KN', 'LC', 'ST',
    'SC', 'SL', 'SB', 'SO', 'ZA', 'SR', 'SY', 'TZ', 'TL', 'TK', 'TO', 'TT',
    'TV', 'UG', 'AE', 'VU', 'YE', 'ZW'
]

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    shipping_partner_id = fields.Many2one('shipping.partner', string="Shipping Partner")

    @api.multi
    def check_required_value_shipping_request(self, orders):
        for order in orders:
            if not order.order_line:
                return _("You don't have any item to ship.")
            else:
                if all(order.order_line.mapped(lambda l: l.product_id.type in ['service', 'digital'])):
                    return _("The estimated rate cannot be computed because all your products are service/digital.")

                order_lines_without_weight = order.order_line.filtered(lambda line_item: not line_item.product_id.type in ['service','digital'] and not line_item.product_id.weight and not line_item.is_delivery)
                for order_line in order_lines_without_weight:
                    return _("Please define weight in product : \n %s") % order_line.product_id.name

            missing_value = self.check_required_value_in_shipping_address(order.warehouse_id.partner_id)
            if missing_value:
                fields = ", ".join(missing_value)
                return (_("There are some missing the values of the Warehouse address. \n Missing field(s) : %s  ") % fields)

            missing_value = self.check_required_value_in_shipping_address(order.partner_shipping_id)
            if missing_value:
                fields = ", ".join(missing_value)
                return (_("There are some missing the values of the Customer address. \n Missing field(s) : %s  ") % fields)

        if not self.shipping_partner_id:
            return _("Shipping Partner isn't defined delivery method.")
        return False

    @api.multi
    def check_required_value_in_shipping_address(self, partner, additional_fields=[]):
        missing_value = []
        mandatory_fields = ['city', 'country_id']
        if partner.country_id.code not in COUNTRIES_WITHOUT_POSTCODES:
            mandatory_fields.append('zip')
        mandatory_fields.extend(additional_fields)
        if not partner.street and not partner.street2:
            mandatory_fields.append('street')
        for field in mandatory_fields:
            if not getattr(partner, field):
                missing_value.append(field)
        return missing_value

    def convert_product_weight(self, unit, weight):
        weight_uom_id = self.env.ref('uom.product_uom_kgm', raise_if_not_found=False)
        if unit == 'KG':
            return weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        elif unit == 'LB':
            return weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_lb'), round=False)
        else:
            raise ValueError

    @api.multi
    def check_max_weight(self, order, shipment_weight):
        for order_line in order.order_line:
            if order_line.product_id and order_line.product_id.weight > shipment_weight:
                return (_("Product weight is more than maximum weight."))
        return False
