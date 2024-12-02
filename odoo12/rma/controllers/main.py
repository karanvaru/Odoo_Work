# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
import datetime
import base64
from odoo import SUPERUSER_ID
from odoo import http
from werkzeug import url_encode
import werkzeug
import logging
_logger = logging.getLogger(__name__)
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _
from odoo.http import Controller, request, route
from odoo.exceptions import AccessError
from odoo.addons.web.controllers.main import binary_content
from odoo.addons.mail.controllers.main import MailController
import odoo



class MailController(MailController):
    _cp_path = '/mail'

    @http.route('/mail/<string:res_model>/<int:res_id>/avatar/<int:partner_id>', type='http', auth='public')
    def avatar(self, res_model, res_id, partner_id):
        headers = [[('Content-Type', 'image/png')]]
        content = 'R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='  # default image is one white pixel
        if res_model in request.env:
            try:
                # if the current user has access to the document, get the partner avatar as sudo()
                request.env[res_model].browse(res_id).check_access_rule('read')
                if partner_id in request.env[res_model].browse(res_id).sudo().exists().message_ids.mapped('author_id').ids:
                    status, headers, content = binary_content(model='res.partner', id=partner_id, field='image_medium', default_mimetype='image/png', env=request.env(user=odoo.SUPERUSER_ID))
                    if not content:
                        content = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAAAAACPAi4CAAAACXZwQWcAAABAAAAAQADq8/hgAAAEWklEQVRYw9WX6XKjRhCAef8HiySQvGt5vfZuEselOUAcEpe4GdI9MAgQOjb5k3SVyzY1801PX9OtNf9StP80QJR5miRpXtb/AFCnvmMySgmhlJn2Mal+BSBSj1NCGeNSGAMOd0/iQYCI95TAXnm+FCr/I2ZYPwJILEJhPaGm7flBFIW+Z5sUvwEivguovG7pMR0cV2e+BbYArF3cBqQclKfEvryvSB2KaHa6BYhgDSP7ZN7gmUNQCf86wCdgcBaKq04/cTzAuwbA/czKb8VdZYMSI8IAEOJ+XjTiFkF4SDjOARIIHLiBK+4E/xHOIdEloMSAAwZx7hEOBKIquwA4lFPbR/3uEhzCqSUmgBiwrGgeIlQm5b0zO0CN3yKw34QgQC4JKZqrGAFC0MpWvuwJ3V6hWD3BI5wchoDaBAumzYQgmsrd7ewZx5bosHIAAAtQp4+nXUuA+2yXy9Xyi4OsIorjauBLZQWtd0Gqrt3EvCXQlb4BMZYfsPP7cr0gvS4FaNw6Qus0ovtez8DZcYyHt8Wmk9XWdF+Mjf570Ke4q46UgAgUCtX55mKl/wSbsD83hrEE0VGJ1RrEWHz2aaXuIAEe7b3SNG/601oSzL/W20/T2r2uDNACARvjWelZQTTaCiCg2vSR1bzrsFgSQMk8SbPi8FWX+0GFbX2OXMarDoAmOGfo+wpXt7cwj4Hv+1n+rSMYW3HOfS4TAgHZIDIVYG38wNzchyB+kj4ZUwB4npw6ABokmgA2qz9kfbIkoWDLzQSQ0tbw2gA20kA/nmyqCHG8nmqQd2prbSKQZAIwnk5B5PSE/EWfACCUZGFSgHQKeE6DsCcExfc5wKEDRLMaJHBwTwA/zFzhOLBBPGODoCfEyYUb0XVBB1AGHXvho/SVDsSjF15QrtMG1xlpsDbCrCewj7UxAWAJSjsAlJOuHI0AX9Mi8IMgsJnMC2MMOJA2f7RhXI8AG/2LVxZZVlQWmKElnAFiT5nMH62L67Mb3lTmbIzVK3Uc9r6GvJAEyMa6d0KXP1oXliqbRPPzN0NvBcrBAmSpr37wlrB8GeRS6zkJECZVNRKeuLfty1C+wc/zp7TD9jVQN7DUDq2vkUEzfAymIl9uZ5iL1B0U1Rw7surmc4SE/sUBE3KaDB8Wd1QS7hJQga4Kayow2aAsXiV0L458HE/jx9UbPi33CIf+ITwDSnxM/IcIcAGIrHzaH+BX8Ky4awdq41nBZYsjG4/kEQLjg9Q5A9A1jJ7u3CJEa1OzmuvSKgubwPA24IT7WT7fJ5YmEtwbASWO2AkP94871WpPOCc8vmYHaORhv5lf75VrV3bD+9nZIrUJamhXN9v9kMlu3wonYVlGe9msU1/cGTgKpx0YmO2fsrKq66rMk8Bh7dd99sDIk+xxxsE5icqhqfsLflkz1pkbukSCBzI5bqG0EGrPGvfK2FeGDseRi1I5eVFuB8WvDp51FvsH13Fcz4+y6n86Oz8kfwPMD02INEiadQAAAABJRU5ErkJggg=="
                    if status == 304:
                        return werkzeug.wrappers.Response(status=304)
            except AccessError:
                pass
        image_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)
        return response

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        rma_count =request.env['rma.rma'].sudo().search_count([('partner_id', '=', partner.id)])
        values.update({
            'rma_count': rma_count,
        })
        return values

    @http.route(['/my/rma/<int:rma>'], type='http', auth="user", website=True)
    def rma_followup(self, rma=None):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        rma_sudo = self._document_check_access('rma.rma', rma)
        attachment_ids = request.env['ir.attachment'].sudo().search([('res_model', '=', 'rma.rma'), ('res_id', '=', rma_sudo.id)])
        return request.render("rma.rma_followup", {
            'rma_record': rma_sudo,
            "attachment_objs" : attachment_ids,
            "report_type": "html",
            'page_name': 'rma',
        })

    @http.route(['/my/rma', '/my/rma/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_rma(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Rma = request.env['rma.rma']

        domain = [('partner_id.id', '=', partner.id)]
        archive_groups = self._get_archive_groups('rma.rma', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'create_date': {'label': _('Date'), 'order': 'create_date asc'},
            'name': {'label': _('Reference'), 'order': 'name asc'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'create_date'
        sort_order = searchbar_sortings[sortby]['order']

        # count for pager
        rma_count = Rma.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/rma",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=rma_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        rma = Rma.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'wk_rma': rma,
            'page_name': 'rma',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/rma',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("rma.wk_rma_records", values)

    @http.route(['/my/quotation/cancel/<int:order>'], type='http', auth="user", website=True)
    def cancel_quotation(self, order=None):
        if order:
            order_obj = request.env['sale.order'].sudo().browse(order)
            order_obj.write({"state" : "cancel"})
        return werkzeug.utils.redirect(request.httprequest.referrer)

    @http.route(['/my/quotation/reorder/<int:order>'], type='http', auth="user", website=True)
    def reorder_quotation(self, order=None):
        raise Warning ("Under Construction")

    @http.route(['/orderline/<int:order_line>'], type='http', auth="user", website=True)
    def rma_form_render(self, order_line=None):
        if order_line:
            raise Warning ("Under Construction")

    @http.route(['/return/rma/'], type='json', auth="user", methods=['POST'] , website=True)
    def rma_retun_product(self, order_line):
        cr, uid, context, env = request.cr, request.uid, request.context, request.env
        sale_order_line = env['sale.order.line']
        rma_reason = env['rma.reasons']
        return_type = env['rma.rma'].sudo().get_request_type()
        if order_line:
            sale_order_line_obj = sale_order_line.sudo().browse(order_line)

        reasons_objs = rma_reason.sudo().search([("is_enable_on_web","=",True)])
        return request.env.ref('rma.wk_product_return').render({
            'orderline': sale_order_line_obj,
            'return_reasons': reasons_objs,
            'return_type': return_type,
        }, engine='ir.qweb')


    @http.route(['/create/rma/'], type='http', auth="user", methods=['POST'] , website=True)
    def rma_retun_create(self, **post):
        cr, uid, context, env = request.cr, request.uid, request.context, request.env
        vals = {}

        vals["order_id"]= int(post.get("order_id"))
        vals["partner_id"] = int(post.get("partner_id"))
        vals["product_id"] = int(post.get("product_id"))
        vals["refund_qty"] = float(post.get("qty"))
        vals["orderline_id"] = int(post.get("ol_id"))
        vals["problem"] = str(post.get("problem"))
        vals["reason_id"] = int(post.get("reason")) if post.get("reason") else False
        vals["return_request_type"] = str(post.get("return_type"))
        vals["i_agree"] = True if str(post.get("i_agree")) == "on" else False
        x = env['rma.rma'].sudo().create(vals)
        return werkzeug.utils.redirect(request.httprequest.referrer)



    @http.route(['/rma/view/'], type='json', auth="user", methods=['POST'] , website=True)
    def rma_view(self, order_line):
        cr, uid, context, env = request.cr, request.uid, request.context, request.env

        sale_order_line = env['sale.order.line']
        if order_line:
            sale_order_line_obj = sale_order_line.sudo().browse(order_line)

        res_rma = request.env['rma.rma']
        partner = request.env.user.partner_id
        rma_obj = res_rma.sudo().search([
            ('orderline_id', '=', order_line)
        ])
        return request.env.ref('rma.wk_rma_view').render({
            'wk_rma': rma_obj,
            'order' : sale_order_line_obj.order_id.name,
        }, engine='ir.qweb')


    @http.route('/rma/file_upload', type='http', auth="public", methods=['POST'], website=True)
    def shop_file_upload(self, **post):
        if post.get('Upload-File'):
            data = {
                'attachments': []
            }
            orphan_attachment_ids = []
            for field_name, field_value in post.items():
                if hasattr(field_value, 'filename'):
                    field_name = field_name.rsplit('[', 1)[0]
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            rma_obj = request.env["rma.rma"].browse(int(post.get('rma_id'))) if post.get('rma_id') else False

            if rma_obj:
                for file in data['attachments']:
                    custom_field = None
                    attachment_value = {
                        'name': file.field_name if custom_field else file.filename,
                        'datas': base64.encodestring(file.read()),
                        'datas_fname': file.filename,
                        'res_model': 'rma.rma',
                        'res_id': rma_obj.id,
                    }
                    attachment_id = request.env[
                        'ir.attachment'].sudo().create(attachment_value)
                    orphan_attachment_ids.append(attachment_id.id)
                    if orphan_attachment_ids:
                        values = {
                            'body': _('<p>Attached files : </p>'),
                            'model': 'rma.rma',
                            'message_type': 'notification',
                            'no_auto_thread': False,
                            'res_id': rma_obj.id,
                            'attachment_ids': [(6, 0, orphan_attachment_ids)],
                        }
                        mail_id = request.env[
                            'mail.message'].create(values)
                    return werkzeug.utils.redirect(request.httprequest.referrer + "#rma-images?%s"% url_encode({'attachment_id':True if attachment_id else False}))
        return True

    @http.route('/rma/remove_upload', type='json', auth="public", website=True)
    def remove_file_upload(self, attachment_id, rma_id, **post):
        if attachment_id:
            cr, uid, context = request.cr, request.uid, request.context
            attachment_obj = request.env['ir.attachment'].sudo().browse(attachment_id)

            rma_obj = request.env["rma.rma"].browse(rma_id) if rma_id else False

            if attachment_obj:
                del_result = attachment_obj.sudo().unlink()
            if rma_obj:
                values = {
                    'body': _('<p>Attached removed.</p>'),
                    'model': 'rma.rma',
                    'message_type': 'comment',
                    'no_auto_thread': False,
                    'res_id': rma_obj.id,
                }
            if del_result:
                return del_result
        return False
