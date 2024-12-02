# -*- coding: utf-8 -*-

import base64
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


def mkdir(client, parent, name):
    """
    Create a folder on Google Drive

    Args:
     * client -  instance of GoogleDriveApiClient
     * parent - DriveItem object id (or False)
     * name - char - new folder name

    Methods:
     * create_folder_o of OnedriveApiClient

    Returns:
     * char - DriveItem id of created folder

    Extra info:
     * We do not care for the duplicated names, since the Google Drive cares for that
     * We do not remove illegal characters here, since they are removed already in sync.object and sync.model, while
       Odoo is always Odoo
    """
    parent = parent or 'root'
    res = client._create_folder(name=name, parent=parent)
    res_id = res.get("id")
    return res_id

class ir_attachment(models.Model):
    """
    Re-writting the model to introduce GoogleDrive specific methods
    """
    _inherit = "ir.attachment"

    cloud_key = fields.Char(string="GoogleDrive ID") #just to rename the field

    @api.model
    def _return_client_context(self):
        """
        The method to return necessary to client context (like session, root directory, etc.)

        Returns:
         * dict
        """
        with_context_dict = super(ir_attachment, self)._return_client_context()
        client = self.env['google.drive.client'].get_client()
        Config = self.env['ir.config_parameter'].sudo()
        if client:
            with_context_dict.update({"client": client,})
        else:
            mes = u"Google Drive Services are not available"
            with_context_dict.get("s_logger").error(mes)
            raise UserError(mes)
        return with_context_dict

    @api.model
    def _check_token_expiration(self):
        """
        The method to check whether token is already expired and if yes, refresh it
        """
        api_client = self._context.get("client")
        d_now = fields.Datetime.now()
        if not hasattr(api_client, "exprires_in") or api_client.exprires_in <= d_now:
            self._context.get("s_logger").warning(
                u"The previous refresh token is expired. Expires In: {}. Now: {}".format(
                    hasattr(api_client, "exprires_in") and api_client.exprires_in or False,
                    d_now,
                )
            )
            Config = self.env['ir.config_parameter'].sudo()
            redirect_uri = Config.get_param('googledrive_redirect_uri', '')
            refresh_token = Config.get_param('google_drive_session', '')
            api_client.get_token_from_refresh_token(refresh_token=refresh_token, redirect_uri=redirect_uri)

    @api.model
    def _find_or_create_root_directory(self):
        """
        Method to return root directory name and id (create if not yet)

        Methods:
         * get_drive_item_o of client
         * mkdir
         * _check_token_expiration()

        Returns:
         * key, name - name of folder and key in client
         * False if failed
        """
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            Config = self.env['ir.config_parameter'].sudo()
            res_id = Config.get_param('google_drive_root_dir_id', '')
            if res_id:
                try:
                    #in try, since the folder might be removed in meanwhile
                    res = client._get_file_metadata(drive_id=res_id)
                except:
                    res_id = False
                    self._context.get("s_logger").warning(
                        u"The root directory 'Odoo' has been removed from Google Drive. Creating a new one".format()
                    )
            if not res_id:
                res_id = mkdir(client, False, "Odoo")
                Config.set_param('google_drive_root_dir_id', res_id)
                self._context.get("s_logger").debug(u"The root directory 'Odoo' is created in Google Drive".format())
            res = res_id, "Odoo"
        except Exception as error:
            res = False, False
            self._context.get("s_logger").error(
                u"The root directory 'Odoo' can't be created in Google Drive. Reason: {}".format(error)
            )
        return res

    @api.model
    def _create_folder(self, folder_name, parent_folder_key, parent_folder_path):
        """
        Method to create folder in clouds

        Args:
         * folder_name - name of created folder
         * parent_folder_key - ID of parent folder in client
         * parent_folder_path - path of parent folder

        Methods:
         * mkdir
         * _check_token_expiration()

        Returns:
         * key, path or False, False if failed

        Extra info:
         * here we can't use folder_id as sync.model / sync.object, since as a parent root my serves
        """
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            res = mkdir(client, parent_folder_key, folder_name), folder_name
            self._context.get("s_logger").debug(u"The folder {} is created in Google Drive".format(folder_name))
        except Exception as error:
            res = False, False
            self._context.get("s_logger").error(
                u"The folder {} can't be created in Google Drive. Reason: {}".format(folder_name, error)
            )
        return res

    @api.multi
    def _get_folder(self, folder_id):
        """
        Method to get folder in clouds

        Args:
         * folder_id - sync.model or sync.object
         * False if failed

        Methods:
         * _get_file_metadata
         * _check_token_expiration()

        Returns:
         * dict of values including 'url'
        """
        self._check_token_expiration()
        res = False
        try:
            client = self._context.get("client")
            if folder_id.key:
                # 1
                res = client._get_file_metadata(drive_id=folder_id.key)
            if res:
                res = {
                    "res_id": res.get("id"),
                    "url": res.get("webViewLink"),
                    "filename": res.get("name"),
                    "path": res.get("name"),
                    "name": res.get("name"),
                    "webUrl": res.get("webViewLink"),
                }
        except Exception as error:
            res = False
            self._context.get("s_logger").error(
                u"The folder {} can't be found in Google Drive. Reason: {}".format(folder_id.name, error,)
            )
        return res

    @api.model
    def _update_folder(self, folder_id, new_folder_name):
        """
        Method to update folder in clouds

        Args:
         * folder_id - sync.model or sync.object object
         * new_folder_name - new name of folder

        Methods:
         * move_or_update_file of client
         * _check_token_expiration()

        Returns:
         * key, path or False, False if failed
        """
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            result = client._move_or_update_file(
                drive_id=folder_id.key,
                new_parent=False,
                new_name=new_folder_name,
            )
            res = result.get("id"), new_folder_name
            self._context.get("s_logger").debug(
                u"The folder {} is updated in Google Drive to {}".format(folder_id.name, new_folder_name)
            )
        except Exception as error:
            res = False, False
            self._context.get("s_logger").error(
                u"The folder {} can't be updated in Google Drive to {}. Reason: {}".format(
                    folder_id.name,
                    new_folder_name,
                    error,
                )
            )
        return res

    @api.model
    def _move_folder(self, folder_id, new_parent_key, new_parent_path):
        """
        Method to move folder in clouds to a different parent

        Args:
         * folder_id - sync.model or sync.object object
         * new_parent_key - new parent folder key
         * new_parent_path - new parent folder path

        Methods:
         * _move_or_update_file of client
         * _check_token_expiration()

        Returns:
         * key, path or False, False if failed
        """
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            result = client._move_or_update_file(
                drive_id=folder_id.key,
                new_parent=new_parent_key,
                new_name=False,
            )
            res = result.get("id"), folder_id.name
            self._context.get("s_logger").debug(
                u"The folder {} is moved in Google Drive to {}".format(
                    folder_id.name,
                    new_parent_path,
                )
            )
        except Exception as error:
            res = False, False
            self._context.get("s_logger").error(
                u"The folder {} can't be moved in Google Drive to {}. Reason: {}".format(
                    folder_id.name,
                    new_parent_path,
                    error,
                )
            )
        return res

    @api.model
    def _remove_folder(self, folder_id):
        """
        Method to move folder in clouds to a different parent
        1. "Item not found" error is fine, since nothing to unlink

        Args:
         * folder_id - sync.model or sync.object object

        Methods:
         * _delete_file of client
         * _check_token_expiration()

        Returns:
         * True or False if failed
        """
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            result = client._delete_file(drive_id=folder_id.key,)
            res = True
            self._context.get("s_logger").debug(u"The folder {} is deleted in Google Drive".format(folder_id.name,))
        except Exception as error:
            if type(error).__name__ == "MissingError":
                # 1
                res = True
                self._context.get("s_logger").warning(
                    u"The folder {} is not deleted in Google Drive since it has been already deleted before".format(
                        folder_id.name,
                    )
                )
            else:
                res = False
                self._context.get("s_logger").error(
                    u"The folder {} can't be deleted in Google Drive. Reason: {}".format(folder_id.name, error)
                )
        return res

    @api.model
    def _return_child_items(self, folder_id, key=False, path=False):
        """
        Method to return child items of this folder
         1. If folder was removed, all its children were removed as well

        Args:
         * folder_id - sync.model or sync.object object
         * key - key of a folder (used if no folder)
         * path -  path of a folder (used if no folder)

        Methods:
         * _list_children_items of client
         * _check_token_expiration()

        Returns:
         * list of of child dicts including name, id, webUrl, path
         * None if error
        """
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            drive_item_id = folder_id and folder_id.key or key
            items = client._list_children_items(drive_id=drive_item_id,)
            res = []
            for child in items:
                res += [{
                    "name": child.get("name"),
                    "path": child.get("name"),
                    "filename": child.get("name"),
                    "id": child.get("id"),
                    "webUrl": child.get("webViewLink"),
                    "url": child.get("webViewLink"),
                }]
        except Exception as error:
            if type(error).__name__ == "MissingError":
                # 1
                res = []
            else:
                res = None
                self._context.get("s_logger").error(
                    u"Failed to find a folder {} in Google Drive. Reason: {}".format(folder_id, error)
                )
        return res

    @api.multi
    def _send_attachment_to_cloud(self, folder_id):
        """
        Method to send attachment to cloud AND to receive item dict
         1. We are to the case of update from cloud

        Args:
         * folder_id - sync.object or sync.model object

        Methods:
         * _normalize_name - to remove illegal character
         * _get_file_metadata of client
         * upload_large_file_o of client
         * _check_token_expiration()

        Returns:
         * dict of res_id, url, name, path
         * False if method failed

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        self._check_token_expiration()
        res = False
        try:
            client = self._context.get("client")
            if self.cloud_key:
                # 1
                res = client._get_file_metadata(drive_id=self.cloud_key)
            else:
                name = self._normalize_name()
                content = base64.urlsafe_b64decode(self.datas)
                file_size = self.file_size
                res = client._upload_file(
                    folder=folder_id.key,
                    file_name=name,
                    mimetype=self.mimetype,
                    content=content,
                    file_size=file_size,
                )
                self._context.get("s_logger").debug(
                    u"The file {} is uploaded in Google Drive to {}".format(self.name, folder_id.name)
                )
            if res:
                res = {
                    "res_id": res.get("id"),
                    "url": res.get("webViewLink"),
                    "filename": res.get("name"),
                    "path": res.get("name"),
                }
        except Exception as error:
            res = False
            self._context.get("s_logger").error(
                u"The file {} ({}) can't be taken / uploaded in Google Drive. Reason: {}".format(
                    self.name, self.id, error
                )
            )
        return res

    @api.multi
    def _upload_attachment_from_cloud(self):
        """
        Method to upload a file from cloud

        Methods:
         * _download_file
         * _check_token_expiration()

        Returns:
         * binary
         * False if method failed
        """
        self.ensure_one()
        self._check_token_expiration()
        res = False
        try:
            client = self._context.get("client")
            result = client._download_file(drive_id=self.cloud_key)
            res = base64.b64encode(result)
        except Exception as error:
            res = False
            self._context.get("s_logger").error(u"Failed to download a file {},{} from Google Drive. Reason: {}".format(
                self.name, self.id, error,
            ))
        return res

    @api.multi
    def _move_attachment(self, folder_id):
        """
        Method an item to a different parent (Used only for stand alone attachments to move between models)

        Args:
         * folder_id - sync.model or sync.object object (although sync.object is not a case)

        Methods:
         * _move_or_update_file of client
         * _check_token_expiration()

        Returns:
         * key, path or False, False if failed

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            result = client._move_or_update_file(
                drive_id=self.cloud_key,
                new_parent=folder_id.key,
                new_name=False,
            )
            res = result.get("id"), result.get("name")
            self._context.get("s_logger").debug(
                u"The file {} ({}) is moved in Google Drive to the folder {}".format(self.name, self.id, folder_id.name)
            )
        except Exception as error:
            res = False, False
            self._context.get("s_logger").error(
                u"The file {} ({}) can't be moved in Google Drive. Reason: {}".format(self.name, self.id, error)
            )
        return res

    @api.multi
    def _remove_attachment_from_cloud(self):
        """
        The method to remove linked file from a cloud storage
        1. "Item not found" error is fine, since nothing to unlink

        Methods:
         * delete_file_o of client
         * _check_token_expiration()

        Returns:
         * res - char of 3 possible values
           ** "not_synced" - it wasn't a sync attachment
           ** "success"
           ** "failure"

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        self._check_token_expiration()
        try:
            client = self._context.get("client")
            if self.cloud_key:
                response = client._delete_file(drive_id=self.cloud_key)
                res = "success"
                self._context.get("s_logger").debug(
                    u"The file {} ({}) is deleted from Google Drive".format(self.name, self.id)
                )
            else:
                res = "not_synced"
        except Exception as error:
            if type(error).__name__ == "MissingError":
                res = "success"
                self._context.get("s_logger").warning(
                    u"The file {} ({}) is not deleted from Google Drive, since it has been removed already".format(
                        self.name,
                        self.id,
                    )
                )
            else:
                res = "failure"
                self._context.get("s_logger").error(
                    u"The file {} ({}) can't be deleted from Google Drive. Reason: {}".format(self.name, self.id, error,)
                )
        return res
