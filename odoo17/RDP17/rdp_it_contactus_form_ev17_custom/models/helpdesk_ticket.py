from odoo import models, fields, api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    customer_mobile = fields.Char(
        string="Customer Mobile"
    )
    serial_no = fields.Char(
        string="Serial Number"
    )
    order_id = fields.Char(
        string="Order",required="1"
    )
    product_name = fields.Char(string="Product",track_visibility = "onchange")
    helpdesk_ticket_type = fields.Many2one(
        'helpdesk.ticket.type',
        string='Complaint Type',required="1"
    )
    purchase_channel_ids = fields.Many2one(
        'purchase.channel', 
        string="Purchase Channel", 
        track_visibility="onchange"
        )
    purchase_date = fields.Date(
        string="Purchase Date",required="1"
    )
    street = fields.Char(
        string="Street",required="1"
    )
    city = fields.Many2one(
        'res.city',
        string='City',required="1"
    )
    state = fields.Many2one(
        'res.country.state',
        string='State',required="1"
    )
    pincode = fields.Char(
        string="Pincode",required="1"
    )
    country = fields.Many2one(
        'res.country',
        string='Country',required="1"
    )
    landmark = fields.Char(
        string="Landmark",required="1"
    )
    invoice_number = fields.Char(
        string="Invoice Number",required="1"
    )
    upload_inv = fields.Binary(
        string='Upload Invoice',required="1",
        copy=False
    )
    document_name = fields.Char(
        string='Document Name',required="1"
    )
    asp_engineer_id = fields.Many2one(
        'res.users',string="Assign to ASP",
        track_visibility = "onchange",
        help="This ticket will be assigned to ASP."
        )
    
    name = fields.Char(
        string='Ticket Number',
        required=False,
        copy=False,
        index=True,
    )



