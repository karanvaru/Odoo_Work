from odoo import models, fields, api


class StudentDetails(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(track_visibility='True',index=True)
    street = fields.Char(track_visibility='True')
    phone = fields.Char(track_visibility='True')
    mobile = fields.Char(track_visibility='True')
    email = fields.Char(track_visibility='True')
    website = fields.Char(track_visibility='True')
    pan = fields.Char(track_visibility='True')
    # last_2_yr_avg_revenue_in_crores = fields.Char(string="Last 2 Yr Avg Revenue (in Crores)", track_visibility='always')
    # top_five_customers_for_reference_name = fields.Char(string="Top 5 Customers (for Reference)")

