# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PARAMS = (
    ('googledrive_client_id', str, ''),
    ('googledrive_client_secret', str, ''),
    ('googledrive_redirect_uri', str, 'http://localhost:8069/google_drive_token'),
    ('googleteam_drive', safe_eval, False),
    ('googledrive_drive', str, 'My Drive'),
)


class res_config_settings(models.TransientModel):
    """
    To-do:
     * Whether to convert some extensions to Google Extensions
    """
    _inherit = "res.config.settings"

    googledrive_client_secret = fields.Char(
        string="App Secret Key",
    )
    googledrive_client_id = fields.Char(
        string="App Client ID",
    )
    googledrive_redirect_uri = fields.Char(
        string="Redirect URL",
        default='http://localhost:8069/google_drive_token',
        help="The same redirect url should be within your Google Drive app settings"
    )
    googleteam_drive = fields.Boolean(
        string="Team Drive",
        help="""
            Check, if sync should be done for the team Drive.
            In that case the folder Odoo would be created within a chosen Team Drive
        """
    )
    googledrive_drive = fields.Char(
        string="Google Drive",
        help="""
            Select Team Google where attachments are synced drive.
            Make sure your user has full rights for this GDrive
        """
    )

    @api.model
    def get_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        res = super(res_config_settings, self).get_values()
        values = {}
        for field_name, getter, default in PARAMS:
            values[field_name] = getter(str(Config.get_param(field_name, default)))
        res.update(values)
        return res

    @api.model
    def set_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        super(res_config_settings, self).set_values()
        for field_name, _, _ in PARAMS:
            value = getattr(self, field_name)
            Config.set_param(field_name, str(value))

    @api.multi
    def action_login_gdrive(self):
        """
        The action to log in Google Account and confirm permissions

        Methods:
         * get_auth_url of GoogleDrive client

        Returns:
         * Updated config page if test is fine

        Raises:
         * UserError if test doesn't work
        """
        auth_url = self.env["google.drive.client"].get_auth_url()
        res = {
            'name': 'Google Drive',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': auth_url
        }
        return res

    @api.multi
    def action_reset(self):
        """
        The method to remove all data and objects related to owncloud

        Methods:
         * _return_config_action

        Returns:
         * Refreshed configs
        """
        res = super(res_config_settings, self).action_reset()
        params, _, _ = zip(*PARAMS)
        params += ('google_drive_session', 'google_drive_root_dir_id', 'google_delta_url')
        self._cr.execute('DELETE FROM ir_config_parameter WHERE key IN %s', (params,))
        return res
