from odoo import models, fields, api

class ShiprocketChannels(models.Model):
    _name = "shiprocket.channels"
    
    name = fields.Char(string='Channel Name')
    chanel_code = fields.Char(string='Chanel Code')
    chanel_status = fields.Char(string='Chanel Status')
