from odoo import http
from odoo.http import request

class ElearningSnippet(http.Controller):
    @http.route(['/latest_elearning_courses'], type="json", auth="public", website=True, methods=['POST'])
    def all_courses(self):
        blogs = http.request.env['blog.post'].search([])
        data = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in blogs:
            data.append({
                'id': record.id,
                'name': record.name,
                'url': base_url + record.website_url,
            })
        return data