from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    ed_no = fields.Char(
        string='E.D No',
        copy=False,
        readonly=True
    )
    departure_date = fields.Date(
        string="Departure Date",
        default=fields.Date.today(),
        readonly=True
    )

    ship_flight = fields.Char(
        string="Ship/Flight",
        copy=False,
        readonly=True
    )
    # third_schedule = fields.Date(
    #     string="Third Schedule",
    #     readonly=True
    # )

    staying_at = fields.Char(
        string="Staying at",
        readonly=True
    )

    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)
        if 'booked_data' in ui_order:
            result['ed_no'] = ui_order['booked_data']['ed_no']
            result['ship_flight'] = ui_order['booked_data']['ship_flight']
            result['staying_at'] = ui_order['booked_data']['staying_at']
            result['departure_date'] = ui_order['booked_data']['departure_date'] or False
            # result['third_schedule'] = ui_order['booked_data']['third_schedule'] or False
        return result

#     def _generate_pos_order_invoice(self):
#         res = super(PosOrder, self)._generate_pos_order_invoice()
#         move_id = self.env['account.move'].browse(res['res_id'])
#         move_id.update({
#             'departure_date': self.departure_date,
#             'ship_flight': self.ship_flight,
#             'ed_no': self.ed_no,
#             'staying_at': self.staying_at,
#             'is_duty_free_confirm': True
#         })
#         return res

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        vals.update({
            'departure_date': self.departure_date,
            'ship_flight': self.ship_flight,
            'ed_no': self.ed_no,
            'staying_at': self.staying_at,
            'is_duty_free_confirm': True
        })
        return vals

    def _prepare_invoice_line(self, order_line):
        vals = super(PosOrder, self)._prepare_invoice_line(order_line)
        if order_line.product_id.default_code:
            vals.update({
                'item_code': order_line.product_id.default_code
            })
        return vals

