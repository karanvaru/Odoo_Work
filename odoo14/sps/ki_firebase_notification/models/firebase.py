import datetime
import firebase_admin
from firebase_admin import credentials,messaging
from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class FirebaseNotification_(models.Model):
    _name = 'ki.firebase.notification'
    _description = "Firebase Notification"

    name = fields.Char(
        "Name",
        required=True
    )
    type = fields.Text(
        "Type",
        required=True
    )
    project_id = fields.Text(
        "Project ID",
        required=True
    )
    private_key_id = fields.Text(
        'Private Key ID',
        required=True
    )
    private_key = fields.Text(
        "Private Key",
        required=True
    )
    client_email = fields.Text(
        "Client Email",
        required=1
    )
    client_id = fields.Text(
        "Client ID",
        required=True
    )
    auth_uri = fields.Text(
        "Auth URI",
        required=True
    )
    token_uri = fields.Text(
        "Token URI",
        required=True
    )
    auth_provider_x509_cert_url = fields.Text(
        "Auth Provider URL",
        required=True
    )
    client_x509_cert_url = fields.Text(
        "Client URL",
        required=True
    )
    mobile_device_id = fields.Char(
        "Mobile Device ID"
    )
    body = fields.Char(
        "Body"
    )
    title = fields.Char(
        "Title"
    )
    state = fields.Selection(
        [
            ('inactive', 'In-Active'),
            ('active','Active')

        ],
        default = 'inactive'
    )

    def deactivate_firebase(self):
        self.ensure_one()
        try:
            new_app = firebase_admin.get_app(name='Smart Printer')
            if new_app:
                firebase_admin.delete_app(new_app)
        except:
            pass
        self.state = 'inactive'

    def config_firebase_certificate(self):
        self.ensure_one()
        firebase_json = {
            "type": "%s" % self.type,
            "project_id": "%s" % self.project_id,
            "private_key_id": "%s" % self.private_key_id,
            "private_key": (self.private_key.splitlines()[0]).replace('\\n','\n'),
            "client_email": "%s" % self.client_email,
            "client_id": "%s" % self.client_id,
            "auth_uri": "%s" % self.auth_uri,
            "token_uri": "%s" % self.token_uri,
            "auth_provider_x509_cert_url": "%s" % self.auth_provider_x509_cert_url,
            "client_x509_cert_url": "%s" % self.client_x509_cert_url
        }
        try:
            new_app = firebase_admin.get_app(name='Smart Printer')
            if new_app:
                firebase_admin.delete_app(new_app)
        except:
            pass
        try:
            cred = credentials.Certificate(firebase_json)
            new_app = firebase_admin.initialize_app(cred,name='Smart Printer')
        except Exception as e:
            raise ValidationError(_(e))
        self.state='active'
        return new_app

    def send_push_notification(self, mobile_device_id, body="", title="", order_id="", action=""):
        self.ensure_one()
        try:
            mobile_device_id = str(mobile_device_id)
            body = str(body)
            title = str(title)
            action = str(action)
        except:
            raise ValidationError(_("Pass Vaild Data"))

        notif_message = messaging.Message(
            data={
                'orderId': '%s' % (str(order_id)),
                'notificationType': 'order'
            },
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=36),
                priority='high',
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body,
                    sound="notif_sound.wav",
                    priority='high',
                    # icon='stock_ticker_update',
                    # color='#f45342'
                ),
            ),
            token=mobile_device_id,
        )
        self.state='active'

        try:
            new_app = firebase_admin.get_app(name='Smart Printer')
        except:
            if self.state == 'active':
                new_app = self.config_firebase_certificate()
        if new_app:
            try:
                return messaging.send(notif_message, False, new_app)
            except:
                return "No Valid Device"
        return False

    def action_test_notif(self):
        self.send_push_notification(self.mobile_device_id,self.body,self.title)

    @api.constrains('name')
    def check_firebase_length(self):
        for rec in self:
            firebase_ids = self.env['ki.firebase.notification'].sudo().search([])
            if len(firebase_ids) > 1:
                raise ValidationError('You have already Created one Record')