# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
# from odoo.addons.web.controllers.main import  content_disposition
from odoo.http import content_disposition

import base64


class Binary(http.Controller):

    @http.route('/web/binary/document', type='http', auth="public")
    def download_document(self, model, field, id, filename=None, **kw):
        """Download link for excel files stored as binary fields."""
        record = request.env[model].browse([int(id)])
        res = record.read([field])[0]
        filecontent = base64.b64decode(res.get(field) or '')
        if not filecontent:
            return request.not_found()
        else:
            if not filename:
                filename = '%s_%s' % (model.replace('.', '_'), id)
            return request.make_response(
                        filecontent,
                        [('Content-Type', 'application/octet-stream'),
                         ('Content-Disposition', content_disposition(filename))])
