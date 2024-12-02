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
        string="Order"
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    helpdesk_ticket_type = fields.Many2one(
        'helpdesk.ticket.type',
        string='Complaint Type',
    )
    sub_complaint_type = fields.Selection([('right bud problem', 'Right Bud Problem'),
                                           ('left bud problem', 'Left Bud Problem'), ],
                                          string="Sub Complaint Type"
                                          )
    # contact_device_no = fields.Char(
    #     string="Contact Device No"
    # )
    product_purchase = fields.Selection([
        ('ecommerce', 'ecommerce'),
        ('retail', 'retail'),
    ],
        string='Product Purchase From'
    )
    color = fields.Selection([
        ('black', 'Black'),
        ('white', 'White'),
    ],
        string='Color'
    )
    # purchase_date = fields.Char(
    #     string="Purchase Date"
    # )
    purchase_date = fields.Date(
        string="Purchase Date"
    )
    street = fields.Char(
        string="Street"
    )
    city = fields.Many2one(
        'res.city',
        string='City',
    )
    state = fields.Many2one(
        'res.country.state',
        string='State',
    )
    pincode = fields.Char(
        string="Pincode"
    )
    country = fields.Many2one(
        'res.country',
        string='Country',
    )
    landmark = fields.Char(
        string="Landmark"
    )
    invoice_number = fields.Char(
        string="Invoice Number"
    )
    upload_inv = fields.Binary(
        string='Upload Invoice',
        copy=False
    )
    document_name = fields.Char(
        string='Document Name'
    )

    # Assuming you want to generate sequence for a 'name' field
    name = fields.Char(
        string='Ticket Number',
        required=False,
        copy=False,
        readonly=True,
        index=True,
    )

    # @api.model
    # def _get_default_name(self):
    #     return self.env['ir.sequence'].next_by_code('helpdesk.ticket') or '/'
