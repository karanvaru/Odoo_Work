
from odoo import api, models, fields, _
from odoo.exceptions import UserError

import json
from datetime import datetime


class UpdatevehicleNO(models.Model):
    _name = 'consolidate.bill'

    transportation_mode = fields.Selection([('1', 'Road'),
                                            ('2', 'Rail'),
                                            ('3', 'Air'),
                                            ('4', 'Ship'),
                                            ], string="Transportation Mode", default='1')
    transporter_id = fields.Many2one('res.partner', string="Transporter")
    trans_id = fields.Char("Transporter ID")
    state_id = fields.Many2one('res.country.state', "State")
    city = fields.Char("Place")
    vehicle_no = fields.Char("Vehicle No")
    ewaybills_order_ids = fields.Many2many('stock.picking', 'rel_picking_consolidate', 'consolidate_id',
                                           'picking_id', string="Orders")
    transportation_doc_date = fields.Date('Transport Document Date')

    def generate_bill(self):
        order_list = []
        line_data = []
        time2 = datetime.strptime(self.transportation_doc_date, "%Y-%m-%d")
        consolidate_dic = {
            'fromPlace': self.city,
            'fromState': self.state_id.port_code,
            'vehicleNo': self.vehicle_no,
            'transMode': self.transportation_mode,
            'transDocN': self.trans_id,
            'transDocDate': time2.strftime('%d/%m/%Y')
        }
        for line in self.ewaybills_order_ids:
            line_dic = {
                'ewbNo': line.ewaybill_no
            }
            line_data.append(line_dic)
            order_list.append(line)
        consolidate_dic.update({'tripSheetEwbBills': line_data})
        configuration = self.env['eway.configuration'].search([])
        data_base64 = json.dumps(consolidate_dic)
        response = configuration.generate_eway('GENCEWB', warehouse=data_base64)
        if response and response.status_code == 200:
            for order in order_list:
                order.consolidate_eway = (response.json()).get('cEwbNo')
                order.conslidate_ebill_date = (response.json()).get('cEwbDate')
        else:
            raise UserError(_(response.text))
