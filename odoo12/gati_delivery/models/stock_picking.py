from odoo import fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    gati_pickup_date = fields.Datetime("Pickup Date")
    gati_docket_id = fields.Many2one('gati.docket.package.number', string="Gati Docket Number")
    gati_packet_id = fields.Many2one('gati.docket.package.number', string="Gati Package Number")
    gati_from_location_code_id = fields.Many2one('gati.location.code', string="Gati From Location")
    gati_location_code_id = fields.Many2one('gati.location.code', string="Gati To Location")
    is_eway_bill = fields.Boolean('Is Eway Bill')
    ewaybill_number = fields.Char('Eway Bill Number')
    ewaybill_date = fields.Date('Eway Bill Date')
    gati_from_pincode = fields.Char(compute='_compute_pincode', string="From PinCode", help="Technical field to filter location.")
    gati_to_pincode = fields.Char(compute='_compute_pincode', string="From PinCode", help="Technical field to filter location.")

    def get_gati_from_and_to_address(self):
        self.ensure_one()
        is_dropship_picking = False
        if self.picking_type_id.default_location_src_id.usage == 'supplier' and self.picking_type_id.default_location_dest_id.usage == 'customer':
            is_dropship_picking = True
        from_address = self.partner_id if is_dropship_picking else self.picking_type_id.warehouse_id.partner_id
        to_address = self.purchase_id.dest_address_id if is_dropship_picking else self.partner_id
        if self.picking_type_code == 'incoming':
            return to_address, from_address
        return from_address, to_address

    def _compute_pincode(self):
        for record in self:
            from_address, to_address = record.get_gati_from_and_to_address()
            self.gati_from_pincode = from_address.zip or ''
            self.gati_to_pincode = to_address.zip or ''

    def fetch_gati_location_code(self, pincode):
        fetch_location_res = self.carrier_id.shipping_partner_id._gati_send_request('GKEPincodeserviceablity.jsp', request_data={}, prod_environment=self.carrier_id.prod_environment,
                                                                                    params={'reqid': self.carrier_id.shipping_partner_id.gati_token, 'pincode': pincode},
                                                                                    method="POST")
        if fetch_location_res and fetch_location_res.get('result') == 'successful':
            for location in fetch_location_res.get('serviceDtls'):
                location_code = self.env['gati.location.code'].search([('location_code', '=', location.get('locationCode'))])
                if not location_code:
                    location_code.create({'name': location.get('location') or '', 'location_code': location.get('locationCode') or '',
                                          'gati_ou': location.get('ou') or '',
                                          'service_type': location.get('serviceType') or '', 'distance': location.get('distance ') or '',
                                          'pincode': fetch_location_res.get('requid') or ''})
        else:
            raise UserError(_(fetch_location_res.get('errmsg')))
        return True

    def get_gati_location_code(self):
        self.fetch_gati_location_code(self.gati_from_pincode)
        self.fetch_gati_location_code(self.gati_to_pincode)
        return True