from odoo import http
from odoo.http import request


class CueProductSearch(http.Controller):

    @http.route('/cue_product_search/', auth="public", type="json", methods=['POST', 'GET'])
    def cue_product_search(self):
        main_list = []
        template_ids = http.request.env['product.template'].sudo().search([('name', 'ilike', 'Cue Bridge')])
        
        product_name = []
        attribute_ids = template_ids.mapped('attribute_line_ids').mapped('attribute_id')

        for attribute in attribute_ids:
            sub_list = []
            sub_list.append([attribute])
            for product_tmpl in template_ids:
                for attribute_line in product_tmpl.attribute_line_ids.filtered(lambda i: i.attribute_id == attribute):
                    val_list= []
                    for attr_value in attribute_line.value_ids:
                        val_list.append(attr_value)
                    sub_list.append(val_list)
            main_list.append(sub_list)

        for template in template_ids:
            product_name.append(template.name)

        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_cue_tech_specs", {
                'product_name': product_name,
                'main_list': main_list
            })
        }
