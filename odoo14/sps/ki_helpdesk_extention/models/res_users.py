import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _send_push_notification(self, record_id, record_model=None):
        serverToken = 'AAAA7xtqFh8:APA91bEAJuW-6ji8n6gj8yKKY49ZXFKLIwyiiQTBjAKG8gnu9UOIUfQ73TL8OE-UMZqwD4bbpVdLUCC9PyEhqljv5kDhiX8JfnEleiHHHWeUN3hhcuIGNJIR-Ayiqq0HWTnTZw46XfBZ'
        deviceToken = 'cceRCInZS8KEjBzI2B3q3I:APA91bHbfuYtb6xAlE5_sDQxxnaIuotdx_UN3-dIoAsXH3VUOXhCdQnYnIlmH7RIGOCif451r__7CoWVMm94lk7Z1gg2Oq2dZujtqKtVCJkzElyAygCUwMe572aO-p8_mypihSLDhj9D'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

        body = {
            'notification': {
                'title': 'Sending push form python script',
                'body': 'Message from FIREBASE....................'
            },
            'to': deviceToken,
            'priority': 'high',
        }
        response = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers = headers,
            data=json.dumps(body)
        )
        print(response.status_code)
        print(response.json())