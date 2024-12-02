# -*- coding: utf-8 -*-

import json
import logging
import requests

from dateutil.relativedelta import relativedelta
from werkzeug import urls

from odoo import fields
from odoo.exceptions import UserError, MissingError

_logger = logging.getLogger(__name__)


class GoogleDriveApiClient():
    GOOGLE_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'
    GOOGLE_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
    GOOGLE_API_BASE_URL = 'https://www.googleapis.com'
    TIMEOUT = 3600
    SCOPES = "https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file"

    def __init__(self, client_id, client_secret):
        """
        Init method
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.team_drive_id = None
        self.exprires_in = fields.Datetime.now() - relativedelta(seconds=120)

    def authorization_url(self, redirect_uri):
        """
        The method to return authorization url

        Args:
         * redirect_uri - redirect url to get response

        Returns:
         * url for authorization
        """
        params = urls.url_encode({
            "scope": self.SCOPES,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "response_type": "code",
            'access_type': 'offline', # IMPORTANT TO GET REFRESH TOKEN EACH TIME
            'prompt': 'consent', # IMPORTANT TO GET REFRESH TOKEN EACH TIME
        })
        auth_url = u"{}?{}".format(self.GOOGLE_AUTH_ENDPOINT, params)
        return auth_url

    def refresh_token(self, authorization_code, redirect_uri):
        """
        The method to receive refresh token

        Args:
         * authorization_code - code received from Google Drive API
         * redirect_uri - redirect url to get response

        Returns:
         * refresh_token
        """
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        params = {
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': "authorization_code",
        }
        response = requests.post(self.GOOGLE_TOKEN_ENDPOINT, data=params, headers=headers, timeout=self.TIMEOUT)
        content = response.json()
        token = content.get('refresh_token')
        return token

    def get_token_from_refresh_token(self, refresh_token, redirect_uri):
        """
        The method to receive access token from refresh token

        Args:
         * refresh_token - kept refresh token
         * redirect_uri - redirect url to get response

        Returns:
         * access_token
        """
        params = {
            'client_id': self.client_id,
            'refresh_token': refresh_token,
            'client_secret': self.client_secret,
            'grant_type': "refresh_token",
            'scope': self.SCOPES,
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        _logger.info("Start receiving Google Drive refresh token")
        response = requests.post(self.GOOGLE_TOKEN_ENDPOINT, data=params, headers=headers, timeout=self.TIMEOUT)
        content = response.json()
        _logger.info("Token from Google Drive refresh token response: {}".format(content))
        token = content.get('access_token')
        self.token = token
        self.exprires_in = fields.Datetime.now() + relativedelta(seconds=content.get('expires_in')-120)
        return token

    def _list_team_drives(self, name):
        """
        Method to receive list of team drives

        Args:
         * name - team drive name to search
        """
        url = "/drive/v3/teamdrives"
        params = {
            "q": "name = '{}'".format(name),
            "supportsTeamDrives": True,
            "useDomainAdminAccess": True,
        }
        res = self._request_gd(method="GET", params=params, url=url)
        response = res.json()
        return response

    def _get_file_metadata(self, drive_id):
        """
        The method to retrieve file metadata

        Args:
         * drive_id - Google Drive ID
        """
        url = "/drive/v3/files/{}".format(drive_id)
        params = {
            "fields": "id,name,webViewLink,webContentLink,mimeType,parents",
        }
        res = self._request_gd(method="GET", url=url, params=params)
        response = res and res.json() or False
        return response

    def _create_folder(self, name, parent):
        """
        The method to create file or folders

        Args:
         * drive_id - Google Drive ID
         * name - char - name of created item
         * parent - Google Drive Id of parent folder
        """
        url = "/drive/v3/files"
        if (not parent or parent == "root") and self.team_drive_id:
            parent = self.team_drive_id
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': parent and [parent] or [],
        }
        if self.team_drive_id:
            file_metadata.update({"teamDriveId": self.team_drive_id})
        data = json.dumps(file_metadata)
        params = {
            "uploadType": "multipart",
            "fields": "id,name,webViewLink,webContentLink,mimeType,parents",
        }
        res = self._request_gd(method="POST", url=url, params=params, data=data)
        response = res and res.json() or False
        return response

    def _move_or_update_file(self, drive_id, new_parent=False, new_name=False):
        """
        Method to update drive item

        Args:
         * drive_id - Google Drive ID of changed item
         * new_parent - new parent Google Drive ID
         * new_name
        """
        params = {"fields": "id,name,webViewLink,webContentLink,mimeType,parents",}
        file_metadata = {}
        if new_parent:
            fdata = self._get_file_metadata(drive_id=drive_id) # to get old parents
            old_parents = fdata.get("parents")
            params.update({
                "addParents": [new_parent],
                "removeParents": ",".join(old_parents),
            })
        if new_name:
            file_metadata.update({"name": new_name})
        if self.team_drive_id:
            file_metadata.update({"teamDriveId": self.team_drive_id})
        data = json.dumps(file_metadata)
        url = "/drive/v3/files/{}".format(drive_id)
        res = self._request_gd(method="PATCH", url=url, params=params, data=data)
        response = res and res.json() or False
        return response

    def _delete_file(self, drive_id):
        """
        Method to delete Drive Item

        Args:
         * drive_id - Google Drive ID of deleted item
        """
        url = "/drive/v3/files/{}".format(drive_id)
        res = self._request_gd(method="DELETE", url=url)
        return res

    def _list_children_items(self, drive_id):
        """
        Method to list children of this Drive Item

        Args:
         * drive_id - Google Drive ID
        """
        url = "/drive/v3/files"
        q="'{}' in parents".format(drive_id)
        params = {
            "q": q,
            "pageSize": 1000,
            "pageToken": None,
            "fields": "kind,nextPageToken,files(id,name,webViewLink,webContentLink)",
        }
        if self.team_drive_id:
            params.update({
                "corpora": "teamDrive",
                "includeTeamDriveItems": True,
            })
        res = self._request_gd(method="GET", url=url, params=params)
        response = res and res.json() or False
        items = response and response.get("files")
        while response.get("nextPageToken"):
            params.update({"pageToken": response.get("nextPageToken")})
            res = self._request_gd(method="GET", url=url, params=params)
            response = res and res.json() or False
            if response:
                items += response.get("files")
        return items

    def _upload_file(self, folder, file_name, mimetype, content, file_size):
        """
        The method to upload file

        Args:
         * folder
         * file_name
         * content
         * file_size
        """
        upload_session = self._generate_upload_session(
            folder=folder,
            file_name=file_name,
            mimetype=mimetype,
            file_size=file_size,
        )
        headers = {
            "Content-Length": str(file_size),
            "Content-Range": "bytes 0-{}/{}".format(file_size-1, file_size)
        }
        res = self._request_gd(method="POST", url=upload_session, data=content, headers=headers, content_type=mimetype,
                               timeout=self.TIMEOUT, full_url=True,)
        response = res and res.json() or False
        return response

    def _generate_upload_session(self, folder, file_name, mimetype, file_size):
        """
        The method to generate resumable upload

        Args:
         * folder
         * file_name
         * file_size
        """
        url = "/upload/drive/v3/files"
        file_metadata = {
            'name': file_name,
            'mimeType': mimetype,
            'parents': [folder],
        }
        if self.team_drive_id:
            file_metadata.update({"teamDriveId": self.team_drive_id})
        data = json.dumps(file_metadata)
        params = {
            "uploadType": "resumable",
            "fields": "id,name,webViewLink,webContentLink",
        }
        headers = {
            "X-Upload-Content-Length": str(file_size),
            "X-Upload-Content-Type": mimetype,
            "Content-Length": str(file_size),
        }
        res = self._request_gd(method="POST", url=url, params=params, data=data, headers=headers, timeout=self.TIMEOUT,)
        response = res and res.headers.get("Location") or False
        return response

    def _download_file(self, drive_id):
        """
        The method to get file content

        Args:
         * drive_id - Google Drive ID of downloaded item
        """
        res = False
        try:
            # for binary images
            url = "/drive/v3/files/{}".format(drive_id)
            params = {"alt": "media",}
            res = self._request_gd(method="GET", url=url, params=params, timeout=self.TIMEOUT,)
        except:
            # for google drive docs
            url = "/drive/v3/files/{}/export".format(drive_id)
            response = self._get_file_metadata(drive_id=drive_id)
            mime_type = response.get("mimeType")
            odoo_mimetype = self._correspond_gdrive_mimetypes(mime_type)
            if not odoo_mimetype:
                raise UserError("Unsupported format {}".format(mime_type))
            params = {"mimeType": odoo_mimetype}
            res = self._request_gd(method="GET", url=url, params=params, timeout=self.TIMEOUT,)
        response = res and res._content or False
        return response

    def _correspond_gdrive_mimetypes(self, mime_type):
        """
        Method to apply mime type to gdrive documents
        """
        res = False
        if mime_type in ["application/vnd.google-apps.spreadsheet"]:
            res = "application/x-vnd.oasis.opendocument.spreadsheet"
        elif mime_type in ["application/vnd.google-apps.document"]:
            res = "application/vnd.oasis.opendocument.text"
        elif mime_type in ["application/vnd.google-apps.presentation"]:
            res = "application/vnd.oasis.opendocument.presentation"
        elif mime_type in ["application/vnd.google-apps.drawing"]:
            res = "application/pdf"
        return res

    def _get_tracked_changes(self, startpage):
        """
        The method to receive track changes url and list of changes
        """
        if not startpage:
            url = "/drive/v3/changes/startPageToken"
            response = self._request_gd(method="GET", url=url, timeout=self.TIMEOUT,)
            startpage = response.get('startPageToken')
        nextPageToken = startpage
        changes = []
        url = "/drive/v3/changes"
        while startpage:
            params = {"pageToken": startpage}
            response = self._request_gd(method="GET", url=url, params=params, timeout=self.TIMEOUT,)
            changes += response.get("changes")
            startpage = response.get("nextPageToken")
            if response.get("newStartPageToken"):
                nextPageToken = response.get("newStartPageToken")
        return changes, nextPageToken

    def _request_gd(self, method, url, params={}, data={}, headers={}, content_type="application/json",
                    accept="application/json", full_url=False, **kwargs):
        """
        The method to execute request for Google Drive API

        Args:
         * method - REST API method for request
         * url - definite method of REST API (without API url)
         * params - dict of encoded request parameters
         * data - string
         * headers - request headers
         * content_type - type of data
         * accept - type of data
         * full_url - whether it is a full url, or need to add api endpoint

        Returns:
         * response
        """
        _headers = {
            "Accept": accept,
            "Content-Type": content_type,
            "Authorization": "Bearer " + self.token,
        }
        headers.update(_headers)
        params.update({"access_token": self.token,})
        r_url = full_url and url or self.GOOGLE_API_BASE_URL + url
        if self.team_drive_id:
            params.update({
                "supportsTeamDrives": True,
                "teamDriveId": self.team_drive_id,
            })
        if method.upper() in ('GET', 'DELETE'):
            res = requests.request(
                method,
                r_url,
                params=params,
                timeout=self.TIMEOUT,
            )
        elif method.upper() in ('POST', 'PATCH', 'PUT'):
            res = requests.request(
                method,
                r_url,
                params=params,
                data=data,
                headers=headers,
                timeout=self.TIMEOUT,
            )
        else:
            raise Exception(_(u'Method not supported {} not in [GET, POST, PUT, PATCH or DELETE]!'.format(method)))

        if res.status_code in (200, 201, 202):
            return res
        elif res.status_code in (204, 404):
            raise MissingError(res)
        else:
            raise UserError(res)
