from odoo import models,fields


class GenerateDocketPacketNumber(models.TransientModel):
    _name = 'generate.docket.packet.number'
    _description = 'Generate Docket Packet Number'

    from_number = fields.Integer(string="From Number")
    to_number = fields.Integer(string="To Number")
    type = fields.Selection([('docket', 'Docket'), ('packet', 'Packet')], string='Type')

    def create_docket_or_packet_number(self):
        gati_docket_package_number = self.env['gati.docket.package.number']
        for num in range(self.from_number, self.to_number):
            gati_docket_package_number.create({'name':num, 'type':self.type})
        gati_docket_package_number.create({'name': self.to_number, 'type': self.type})
        return True

