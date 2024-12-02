from odoo import http
from odoo.http import request


class ProductTagCategory(http.Controller):

    @http.route('/product_tag_custom/', auth="public", type="json", methods=['POST'])
    def product_tag_custom(self):
        # product_tag_id1 = (http.request.env['product.tag'].sudo().search_read([], ['name','product_tag_categ_id']))
        # print("++aaaaaaaaaaaaaproduct_tag_id1",product_tag_id1)
        product_tag_ids = http.request.env['product.tag'].sudo().search([])
        print("aaaaaaaaaaaaaaaaaaaaaaproduct_tag_ida",product_tag_ids)
        # categ_list = []
        categ_dict = {}
        for rec in product_tag_ids:
            if rec.product_tag_categ_id not in categ_dict:
                categ_dict[rec.product_tag_categ_id] = []
            categ_dict[rec.product_tag_categ_id].append(rec)

        # for rec in product_tag_id:
        #     if rec.product_tag_categ_id.name not in categ_dict:
        #         categ_dict[rec.product_tag_categ_id.name] = []
        #     categ_dict[rec.product_tag_categ_id.name].append(rec.name)
        # categ_list.append(categ_dict)
        print("+++++++++++categ_dict+++++++",categ_dict)
        product_tag_categ_ids = http.request.env['product.tag.category'].sudo().search([])

        return {
            'message': request.env['ir.ui.view']._render_template("cue_website.template_helpme_options", {
                'categories': categ_dict
            })
        }

        return categ_dict
