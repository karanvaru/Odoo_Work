from odoo import http
from odoo.http import request


class PurchaseDashboard(http.Controller):


    @http.route('/purchase_dashboard/', auth="public", type="json", methods=['POST'])
    def purchase_dashboard(self):
        
        request._cr.execute("""
            SELECT
                COUNT(*) as count,
                state,
                SUM(price_total) as amount_total
            FROM
                purchase_order_line
            GROUP BY
                state
        """)
        
        query_result = request._cr.dictfetchall()

        counts = {}
        for result in query_result:
            print ("result _______________",result)
        
        
        product_category_image = request.env['res.partner'].search([], limit=10)
        purchase_order_lines = request.env['purchase.order.line'].search([], limit=10)
        top_products_by_quantity_dict = {}
        top_products_by_amount_dict = {}
        top_partners_dict = {}

        for line in purchase_order_lines:
            if line.product_id not in top_products_by_quantity_dict:
                top_products_by_quantity_dict[line.product_id] = line.product_qty
            else:
                top_products_by_quantity_dict[line.product_id] += line.product_qty

            if line.product_id not in top_products_by_amount_dict:
                top_products_by_amount_dict[line.product_id] = line.price_subtotal
            else:
                top_products_by_amount_dict[line.product_id] += line.price_subtotal


            if line.partner_id not in top_partners_dict:
                top_partners_dict[line.partner_id] = line.price_subtotal
            else:
                top_partners_dict[line.partner_id] += line.price_subtotal

        return {
            'message': request.env['ir.ui.view']._render_template("ki_dashboard_purchase.template_dashboard_customer", {
                'partners': product_category_image,
                'total_orders': 1000000,
                'total_pending_orders': 2000000,
                'total_new_orders': 3000000,
                'top_products_by_quantity': top_products_by_quantity_dict,
                'top_products_by_amount': top_products_by_amount_dict,
                'top_partners': top_partners_dict
            })
        }
