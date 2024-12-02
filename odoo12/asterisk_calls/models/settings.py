import logging
from odoo import fields, models, api, tools, _
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


# Compatibility for upgrade
class OldCallsSettings(models.Model):
    _name = 'asterisk_calls.settings'


class CallsSettings(models.Model):
    _inherit = 'asterisk_common.settings'

    calls_keep_days = fields.Char(
        string=_('History Keep Days'),
        default='90',
        required=True,
        help=_('Calls older then set value will be removed.'))
    recordings_keep_days = fields.Char(
        string=_('Recordings Keep Days'),
        default='90',
        required=True,
        help=_('Recordings older then set value will be removed.'))
    auto_reload_channels = fields.Boolean(
        default=True,
        help=_('Automatically refresh active channels view'))
    recording_storage = fields.Selection(
        [('db', _('Database')), ('filestore', _('Files'))],
        default='filestore', required=True)
    delete_recordings = fields.Boolean(
        default=True,
        help='Keep recordings on Asterisk after upload to Odoo.')
    use_mp3_encoder = fields.Boolean(
        default=False, string=_("Encode call recordings to MP3"),
        help=_("If checked, call recordings will be encoded using MP3"
               "Requires lameenc Python package installed to work."))
    mp3_encoder_bitrate = fields.Selection(
        selection=[('48', '48kbps'),
                   ('64', '64kbps'),
                   ('96', '96kbps'),
                   ('128', '128 kbps')],
        required=False)
    mp3_encoder_quality = fields.Selection(
        selection=[('2', 'Best Quality'),
                   ('4', 'Average quality'),
                   ('7', 'Worst Quality')],
        required=False)
    is_widget_enabled = fields.Boolean(string='Calls Widget', default=True)

    def sync_recording_storage(self):
        count = 0
        try:
            for rec_id in self.env['asterisk_calls.call']._search(
                    [('recording_filename', '!=', False)]):
                rec = self.env['asterisk_calls.call'].browse(rec_id)
                if self.recording_storage == 'db' and not rec.recording_data:
                    rec.write({
                        'recording_data': rec.recording_attachment,
                        'recording_attachment': False})
                    count += 1
                    self.env.cr.commit()
                    logger.info('Call ID %s recording moved to %s',
                                rec_id, self.recording_storage)

                elif (self.recording_storage == 'filestore'
                      and not rec.recording_attachment):
                    rec.write({
                        'recording_attachment': rec.recording_data,
                        'recording_data': False})
                    count += 1
                    self.env.cr.commit()
                    logger.info('Call ID %s recording moved to %s',
                                rec_id, self.recording_storage)
        except Exception as e:
            # Remove attachments
            logger.info('Sync recordings error: %s', str(e))
        finally:
            logger.info('Moved %s recordings', count)
            self.env['ir.attachment']._file_gc()

    @api.constrains('use_mp3_encoder')
    def _check_lameenc(self):
        try:
            import lameenc
        except ImportError:
            for rec in self:
                if rec.use_mp3_encoder:
                    raise ValidationError(
                        "Please install lameenc to enable MP3 encoding"
                        "(pip3 install lameenc).")

    @api.onchange('use_mp3_encoder')
    def on_change_mp3_encoder(self):
        for rec in self:
            if rec.use_mp3_encoder:
                rec.mp3_encoder_bitrate = '96'
                rec.mp3_encoder_quality = '4'

    @api.model
    def check_widget_enabled(self):
        # Used by calls popup widget
        widget_enabled = self.sudo().get_param('is_widget_enabled')
        has_group = self.env.user.has_group(
            'asterisk_common.group_asterisk_user')
        return all([widget_enabled, has_group])
