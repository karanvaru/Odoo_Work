import base64
import werkzeug

import odoo.http as http
from odoo.http import request
from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class HelpdeskWebExtention(HelpdeskTicketController):
    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        url_params = request.httprequest.args.to_dict()
        product_number = str(url_params.get('ProductNumber', 0))
        products = http.request.env["product.product"].search(
            [("active", "=", True), ('default_code', '=', product_number)]
        )
        categories = http.request.env["helpdesk.ticket.category"].search(
            [("active", "=", True)]
        )
        email = http.request.env.user.email
        name = http.request.env.user.name
        return http.request.render(
            "helpdesk_mgmt.portal_create_ticket",
            {"categories": categories, "email": email, "name": name, 'products': products},
        )

    @http.route("/submitted/ticket", type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        vals = {
            "product_id": int(kw.get("product")),
            "company_id": http.request.env.user.company_id.id,
            "category_id": kw.get("category"),
            "description": kw.get("description"),
            "name": kw.get("subject"),
            "attachment_ids": False,
            "channel_id": request.env["helpdesk.ticket.channel"].sudo().search([("name", "=", "Web")]).id,
        }

        new_ticket = request.env["helpdesk.ticket"].sudo().create(vals)
        if new_ticket:
            new_ticket._onchange_contract_id()

        new_ticket.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        if kw.get("attachment"):
            for c_file in request.httprequest.files.getlist("attachment"):
                data = c_file.read()
                if c_file.filename:
                    request.env["ir.attachment"].sudo().create(
                        {
                            "name": c_file.filename,
                            "datas": base64.b64encode(data),
                            "res_model": "helpdesk.ticket",
                            "res_id": new_ticket.id,
                        }
                    )
        return werkzeug.utils.redirect("/my/tickets")

    # @http.route("/login/ticket", type="http", auth="public", website=True, csrf=True)
    # def guest_new_ticket(self, **kw):
    #     pro_id = request.env["contract.contract"].search('product_id', '=', kw.product_id)
    #     if pro_id:
    #         value = {
    #             "product_id": kw.get("product"),
    #             "company_id": http.request.env.user.company_id.id,
    #             "category_id": kw.get("category"),
    #             "description": kw.get("description"),
    #             "name": kw.get("subject"),
    #             "attachment_ids": False,
    #             "channel_id": request.env["helpdesk.ticket.channel"].sudo().search([("name", "=", "Web")]).id,
    #             "partner_id": request.env.user.partner_id.id,
    #             "partner_name": request.env.user.partner_id.name,
    #             "partner_email": request.env.user.partner_id.email,
    #         }
    #
    #         new_ticket = request.env["helpdesk.ticket"].sudo().create(value)
    #         new_ticket.message_subscribe(partner_ids=request.env.user.partner_id.ids)
    #         if kw.get("attachment"):
    #             for a_file in request.httprequest.files.getlist("attachment"):
    #                 data = a_file.read()
    #                 if a_file.filename:
    #                     request.env["ir.attachment"].sudo().create(
    #                         {
    #                             "name": a_file.filename,
    #                             "datas": base64.b64encode(data),
    #                             "res_model": "helpdesk.ticket",
    #                             "res_id": new_ticket.id,
    #                         }
    #                     )
    #     return werkzeug.utils.redirect("/my/tickets")
