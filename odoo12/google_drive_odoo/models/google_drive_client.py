# -*- coding: utf-8 -*-

import logging

from odoo import models, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from .google_drive_api_client import GoogleDriveApiClient as Client

_logger = logging.getLogger(__name__)


class google_drive_client(models.AbstractModel):
    """
    The wrapper model for Python GoogleDrive library
    """
    _name = "google.drive.client"
    _description = "Google Drive Client"

    @api.multi
    def get_client(self, new_token_required=False):
        """
        Method to return instance of Google Drive API Client

        Args:
         * new_token_required - bool - whether we can retrieve a token from existng auth code

        Returns:
         * GoogleDrive instance if initiated
         * False otherwise
        """
        Config = self.env['ir.config_parameter'].sudo()
        client_id = Config.get_param('googledrive_client_id', '')
        client_secret = Config.get_param('googledrive_client_secret', '')
        redirect_uri = Config.get_param('googledrive_redirect_uri', '')
        refresh_token = Config.get_param('google_drive_session', '')
        team_drive = safe_eval(Config.get_param('googleteam_drive', 'False'))
        google_drive_id = team_drive and Config.get_param('google_drive_id', '') or None
        api_client = Client(client_id, client_secret)
        if refresh_token and not new_token_required:
            token = api_client.get_token_from_refresh_token(refresh_token=refresh_token, redirect_uri=redirect_uri)
            api_client.team_drive_id = google_drive_id
        return api_client

    @api.model
    def get_auth_url(self):
        """
        Get URL of authentification page
         1. Clean session, if new url is required

        Methods:
         * get_client
         * authorization_url of GoogleDriveApiClient instance

        Returns:
         * char - url of application to log in

        Extra info:
         * The response is received by the controller to /one_drive_token
         * Do not forget to configure backward url in Google Console App settings
        """
        Config = self.env['ir.config_parameter'].sudo()
        # 1
        Config.set_param('google_drive_session', '')
        gdrive_client = self.get_client(new_token_required=True)
        redirect_uri = Config.get_param('googledrive_redirect_uri', '')
        auth_url = gdrive_client.authorization_url(redirect_uri=redirect_uri)
        _logger.info('Auth url for Google Drive is retrieved: {}'.format(auth_url))
        return auth_url

    @api.model
    def create_gdrive_session(self, code=False):
        """
        Authenticates to Google Drive

        Args:
         * code - authorization code received

        Methods:
         * refresh_token - of Google Drive Api Client

        Extra info:
         * The structure of tokens/codes is: authorization_code > refresh_token > access_token
        """
        api_client = self._context.get("client")
        if code:
            Config = self.env['ir.config_parameter'].sudo()
            redirect_uri = Config.get_param('googledrive_redirect_uri', '')
            token = api_client.refresh_token(authorization_code=code, redirect_uri=redirect_uri)
            if not token:
                self._context.get("s_logger").error(u'Refresh token is not valid. Check app client secret')
                raise UserError("Can't authenticate to Google Drive: check client secret") 
            else:               
                Config.set_param('google_drive_session', token)
                access_token = api_client.get_token_from_refresh_token(refresh_token=token, redirect_uri=redirect_uri)
                Config.set_param('cloud_client_state', 'confirmed')
        else:
            self._context.get("s_logger").error(u'No valid Google Drive code or client provided. Code: {}'.format(code))
            raise UserError("Can't authenticate to Google Drive: make sure you grant all permissions")

    @api.model
    def search_drive_id(self):
        """
        Method to find drive_id in Google Drive of selected directory if it is a team drive or user drive instead

        Methods:
         * _list_team_drives

        Extra info:
         * team drive differs from individual only for optional params and file metadata. Look at -->
           https://stackoverflow.com/questions/45327769/how-can-i-create-a-folder-within-a-team-drive-with-the-google-api
        """
        api_client = self._context.get("client")
        Config = self.env['ir.config_parameter'].sudo()
        team_drive = safe_eval(Config.get_param('googleteam_drive', 'False'))
        if team_drive:
            try:
                drive_name = Config.get_param('googledrive_drive', '')
                drives = api_client._list_team_drives(name=drive_name)
                for prop in drives["teamDrives"]:
                    if prop['name'] == drive_name:
                        drive = prop['id']
                        break
                else:
                    error_mes = u"Team Google Drive {} is not found ".format(drive_name)
                    self._context.get("s_logger").error(error_mes)
                    raise UserError(error_mes)

                Config.set_param('google_drive_id', drive)
                self._context.get("s_logger").info(u"Set Google Drive to {}".format(drive))

            except Exception as error:
                error_mes = u"Team Google Drive is not found. Reason: {}".format(error)
                self._context.get("s_logger").error(error_mes)
                raise UserError(error_mes)
