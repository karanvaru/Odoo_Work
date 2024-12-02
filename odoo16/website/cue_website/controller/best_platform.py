# from odoo import http
# 
# 
# class BestPlatform(http.Controller):
# 
#     @http.route('/platform_category/', auth="public", type="json", methods=['POST'])
#     def best_platform_category(self):
#         platform_category = (http.request.env['product.category'].sudo().search_read([], ['image', 'name']))
#         return platform_category

