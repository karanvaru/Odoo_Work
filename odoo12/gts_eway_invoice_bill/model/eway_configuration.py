from odoo import fields, models, api, _
from odoo.exceptions import UserError

from datetime import datetime
import requests
import json
import base64
import urllib
import logging
_logger = logging.getLogger('Eway Bill')


class EwayConfiguration(models.Model):
    _name = 'eway.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True)
    eway_url_staging = fields.Char("Eway URL(Staging)", tracking=2,
                                   default='http://testapi.taxprogsp.co.in/ewaybillapi/dec/v1.03/')
    eway_url_live = fields.Char("Eway URL(Live)", tracking=2,
                                default='https://api.taxprogsp.co.in/v1.03/dec/')
    print_url_live = fields.Char("Eway Print URL(Live)", tracking=2,
                                 help="Eway Print URL", default='https://api.taxprogsp.co.in/aspapi/v1.0/')
    active = fields.Boolean("Active", default=True)
    active_production = fields.Boolean("Production?", default=False)
    asp_id = fields.Char("ASP ID", tracking=2)
    asp_password = fields.Char("Password", tracking=2)
    gstin_staging = fields.Char("GSTINL(Staging)", tracking=2)
    user_name_staging = fields.Char("User NameL(Staging)", tracking=2)
    ewb_password_staging = fields.Char("Ewb PasswordL(Staging)", tracking=2)
    access_token_staging = fields.Char("Access TokenL(Staging)", tracking=2)
    access_date_staging = fields.Datetime("Access DateL(Staging)", tracking=2)
    distance_key = fields.Char("Distance API Key")
    # gstin_live = fields.Char("GSTIN(Live)", tracking=2)
    # user_name_live = fields.Char("User Name(Live)", tracking=2)
    # ewb_password_live = fields.Char("Ewb Password(Live)", tracking=2)
    access_token_live = fields.Char("Access TokenL(Live)", tracking=2)
    access_date_live = fields.Datetime("Access DateL(Live)", tracking=2)

    @api.constrains('active')
    def validate_email(self):
        active_ids = self.env['eway.configuration'].search([])
        if not len(active_ids) == 1:
            raise UserError(_('Cannot Have Multiple active Configuration'))
        return True

    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active

    def toggle_production(self):
        for record in self:
            record.active_production = not record.active_production

    @api.onchange('active_production')
    def onchange_active_production(self):
        self.access_token = ''
        self.access_date = False

    def generate_token(self, url):
        _logger.info("generate_token URL: %s", url)
        resp = requests.get(url)
        _logger.info("generate_token Response: %s", resp.json())
        if resp.json().get('status') == '1':
            if self.active_production:
                self.access_token_live = resp.json().get('authtoken')
                self.access_date_live = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                self.access_token_staging = resp.json().get('authtoken')
                self.access_date_staging = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'test_connection' in self.env.context:
                self.env.user.notify_success(message='EwayBill Connection Successful !')
        else:
            if 'test_connection' in self.env.context:
                self.env.user.notify_danger(message=resp.json().get('error', {}).get('message'))

    def get_eway_base_url(self):
        if self.active_production:
            eway_url = self.eway_url_live
        else:
            eway_url = self.eway_url_staging
        return eway_url

    def get_eway_extra_url(self, warehouse, with_token=False):
        if self.active_production:
            print(warehouse.ewb_password_live)
            extra_url = 'aspid=' + self.asp_id + '&password=' + \
              self.asp_password + '&gstin=' + warehouse.gstin_live + '&username=' + warehouse.user_name_live + \
              '&ewbpwd=' + warehouse.ewb_password_live
            if self.access_token_live:
                if with_token:
                    extra_url += '&authtoken=' + self.access_token_live
        else:
            extra_url = 'aspid=' + self.asp_id + '&password=' + \
              self.asp_password + '&gstin=' + self.gstin_staging + '&username=' + self.user_name_staging + \
              '&ewbpwd=' + self.ewb_password_staging
            if with_token:
                extra_url += '&authtoken=' + self.access_token_staging
        return extra_url

    def handle_auth_token(self, warehouse=False):
        # if not warehouse:
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        eway_url = self.get_eway_base_url()
        url = eway_url + 'auth?action=ACCESSTOKEN' + '&' + self.get_eway_extra_url(warehouse)
        if self.active_production:
            access_date = self.access_date_live
        else:
            access_date = self.access_date_staging
        print('access_date..datetime.now()  ', access_date, datetime.now())
        if self.active_production:
            access_token = self.access_token_live
        else:
            access_token = self.access_token_staging
        if access_date:
            time1 = datetime.strptime(str(access_date), '%Y-%m-%d %H:%M:%S')
            time2 = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            diff = time2 - time1
            diff_seconds = diff.days * 24 * 60 * 60 + diff.seconds
            _logger.info("handle_auth_token Difference: %s", diff_seconds)
            if diff_seconds >= 21000:
                self.generate_token(url)
        _logger.info("handle_auth_token access_token: %s, access_date: %s", access_token, access_date)
        if not access_token:
            self.generate_token(url)
        return True

    def generate_eway(self, warehouse, data_base64=False, action_name=False):
        print(data_base64)
        eway_url = self.get_eway_base_url()
        self.handle_auth_token(warehouse)
        full_url = eway_url + 'ewayapi?action=' + action_name + '&' + self.get_eway_extra_url(warehouse, with_token=True)
        resp = requests.post(full_url, data=data_base64)
        return resp

    def get_eway_details(self, action_name, ewaybill_no, warehouse):
        eway_url = self.get_eway_base_url()
        self.handle_auth_token(warehouse)
        resp = requests.get(eway_url + 'ewayapi?action=' + action_name + '&' + self.get_eway_extra_url(warehouse, with_token=True)
                            + '&ewbNo=' + ewaybill_no)
        return resp

    def print_eway(self, action_name, response):
        full_print_url = self.print_url_live + action_name + '?aspid=' + self.asp_id +\
                             '&password=' + self.asp_password + '&gstin=' + '09AAFCT8324E1Z9'
        headers = {
            'Content-type': 'application/json'
        }
        resp = requests.post(full_print_url, data=json.dumps(response), headers=headers)
        return resp.content
