# # res_partner_gst.py
#
# from odoo import models, fields, api
#
# class ResPartnerGST(models.Model):
#     _name = 'res.partner.gst'
#     _description = 'Partner GST Information'
#
#     gstin = fields.Char('GSTIN', required=True)
#     # Add other necessary fields for partner registration
#
#     @api.model
#     def send_data_to_gst_portal(self, partner_data):
#         api_url = 'https://example.com/gst_portal/api/registration'
#         api_key = '462dec555ef9e99480037cc6883b3f080210b5bc'
#
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {api_key}'
#         }
#
#         response = self.env['ir.http'].send(
#             method='POST',
#             url=api_url,
#             headers=headers,
#             data=partner_data
#         )
#
#         return response
#
#     def handle_gst_portal_response(self, response):
#         if response.status_code == 200:
#             self.write({'status': 'registered'})
#         else:
#             self.write({'status': 'error'})
