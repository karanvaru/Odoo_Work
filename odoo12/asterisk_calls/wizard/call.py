import logging
from odoo import fields, models, api, _
from odoo.addons.asterisk_calls.models.call import DISPOSITION_TYPES

logger = logging.getLogger(__name__)


class CallsWizard(models.TransientModel):
    _name = 'asterisk_calls.call_wizard'
    _description = 'Call History Wizard'

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True,
                               default=lambda self: fields.Datetime.now())
    from_user = fields.Many2one('res.users')
    to_user = fields.Many2one('res.users')
    to_partner = fields.Many2one('res.partner')
    from_partner = fields.Many2one('res.partner')
    call_disposition = fields.Selection(selection=DISPOSITION_TYPES,
                                        string=_('Disposition'))
    # Fields
    src = fields.Boolean(default=True, string=_("Source"))
    dst = fields.Boolean(default=True, string=_("Destination"))
    src_user = fields.Boolean(string=_("From User"))
    dst_user = fields.Boolean(string=_("To User"))
    partner = fields.Boolean(default=True, string=_("Partner"))
    clid = fields.Boolean(default=True, string=_("Caller ID"))
    started = fields.Boolean(default=True)
    ended = fields.Boolean()
    duration = fields.Boolean(string=_("Call Duration"))
    billsec = fields.Boolean(default=True, string=_("Talk Duration"))
    disposition = fields.Boolean(default=True)

    def submit(self):
        self.ensure_one()
        calls = self.env['asterisk_calls.call'].search([
                                        ('started', '>=', self.start_date),
                                        ('started', '<=', self.end_date)])
        if self.from_user:
            calls = calls.filtered(lambda r: r.src_user == self.from_user)
        if self.to_user:
            calls = calls.filtered(lambda r: r.dst_user == self.to_user)
        if self.to_partner:
            calls = calls.filtered(
                lambda r: r.partner == self.to_partner and not r.dst_user)
        if self.from_partner:
            calls = calls.filtered(
                lambda r: r.partner == self.from_partner and not r.src_user)
        if self.call_disposition:
            calls = calls.filtered(
                lambda r: r.disposition == self.call_disposition)
        data = {
            'ids': [k.id for k in calls],
            'title': _('Calls from {} to {}').format(
                                            self.start_date, self.end_date),
            'fields': {
                'src': self.src,
                'dst': self.dst,
                'src_user': self.src_user,
                'dst_user': self.dst_user,
                'partner': self.partner,
                'clid': self.clid,
                'started': self.started,
                'ended': self.ended,
                'duration': self.duration,
                'billsec': self.billsec,
                'disposition': self.disposition,
                }
        }
        return self.env.ref(
            'asterisk_calls.calls_report_action').report_action(self,
                                                                data=data)
