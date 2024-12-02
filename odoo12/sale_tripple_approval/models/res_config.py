# # -*- coding: utf-8 -*-
# 
# from odoo import fields, models, api
# 
# 
# class SaleConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
# 
#     so_three_step_validation =  fields.Boolean(
#         'Three Step Approval'
#     )
#     so_finance_validation_amount = fields.Monetary(
#         'Finance Validation Amount',
#         default=0.0
#     )
#     so_director_validation_amount = fields.Monetary(
#         'Director Validation Amount',
#         default=0.0
#     )
#     so_email_template_id = fields.Many2one(
#         'mail.template',
#         string='Sale Approval Email Template',
#     )
#     so_refuse_template_id = fields.Many2one(
#         'mail.template',
#         string='Sale Refuse Email Template',
#     )
# 
#     @api.model
#     def get_values(self):
#         res = super(SaleConfigSettings, self).get_values()
#         params = self.env['ir.config_parameter'].sudo()
#         res.update(
#             so_three_step_validation = params.get_param('sale_tripple_approval.so_three_step_validation'),
# #             finance_validation_amount = params.get_param('purchase_tripple_approval.finance_validation_amount'),
# #             director_validation_amount = params.get_param('purchase_tripple_approval.director_validation_amount'),
# #             email_template_id = params.get_param('purchase_tripple_approval.email_template_id'),
# #             refuse_template_id = params.get_param('purchase_tripple_approval.refuse_template_id')
#         )
#         if self.so_email_template_id:
#             res.update(
#             email_template_id = params.get_param('sale_tripple_approval.so_email_template_id'),
#         )
#         return res
# 
#     @api.multi
#     def set_values(self):
#         super(SaleConfigSettings, self).set_values()
#         ICPSudo = self.env['ir.config_parameter'].sudo()
#         ICPSudo.set_param("sale_tripple_approval.so_three_step_validation", self.so_three_step_validation)
# #         ICPSudo.set_param("purchase_tripple_approval.finance_validation_amount", self.finance_validation_amount)
# #         ICPSudo.set_param("purchase_tripple_approval.director_validation_amount", self.director_validation_amount)
#         if self.so_email_template_id:
#             ICPSudo.set_param("sale_tripple_approval.so_email_template_id", self.so_email_template_id)
# #       
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
