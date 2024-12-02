from datetime import timedelta
import logging
import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


logger = logging.getLogger(__name__)


class CallsReport(models.AbstractModel):
    _name = 'report.asterisk_calls.calls_report'
    _description = 'Call Report'

    def _get_report_values(self, docids, data=None):
        if not data:
            # Call from context menu
            data = {}
            docs = self.env['asterisk_calls.call'].browse(docids)
            fields = {
                'src': True,
                'dst': True,
                'src_user': False,
                'dst_user': False,
                'partner': True,
                'clid': True,
                'started': True,
                'ended': False,
                'billsec': True,
                'duration': False,
                'disposition': True,
            }
        else:
            docs = self.env['asterisk_calls.call'].browse(data['ids'])
            fields = data.get('fields')
        docargs = {
            'doc_ids': [k.id for k in docs],
            'doc_model': 'asterisk_calls.call',
            'docs': docs,
            'time': time,
            'title': data.get('title'),
            'fields': fields,
            'total_calls': len(docs),
            'total_duration': str(
                timedelta(seconds=sum(docs.mapped('duration')))),
            'total_billsec': str(
                timedelta(seconds=sum(docs.mapped('billsec')))),

        }
        return docargs
