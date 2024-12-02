# -*- coding: utf-8 -*-

import logging
import werkzeug

from odoo.http import Controller, route, request

_logger = logging.getLogger(__name__)


class google_drive_token(Controller):

    @route('/google_drive_token', type='http', auth='user', website='False')
    def login_to_gdrive(self, **kwargs):
        """
        Controller that handles incoming token from Google Drive

        Methods:
         * create_gdrive_session of google.drive.client
         * search_drive_id of google.drive.client

        Returns:
         * configs view
        """
        code = kwargs.get("code")
        ctx = request.env.context.copy()
        new_ctx = request.env["ir.attachment"]._return_client_context()
        ctx.update(new_ctx)
        request.env['google.drive.client'].with_context(ctx).create_gdrive_session(code=code)
        request.env['google.drive.client'].with_context(ctx).search_drive_id()
        config_action = request.env.ref('cloud_base.cloud_config_action')
        url = "/web#view_type=form&model=res.config.settings&action={}".format(
            config_action and config_action.id or ''
        )
        return werkzeug.utils.redirect(url)
