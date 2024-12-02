import base64
from datetime import datetime, timedelta
import io
import json
import logging
import pytz
import time
import wave
from odoo import models, fields, api, _, release
from odoo.exceptions import ValidationError

try:
    import lameenc
    LAMEENC = True
except ImportError:
    LAMEENC = False

logger = logging.getLogger(__name__)


DISPOSITION_TYPES = (
    ('NO ANSWER', 'No answer'),
    ('FAILED', 'Failed'),
    ('BUSY', 'Busy'),
    ('ANSWERED', 'Answered'),
    ('CONGESTION', 'Congestion'),
)


class Call(models.Model):
    _name = 'asterisk_calls.call'
    _inherit = ['mail.thread']
    _description = 'Call Log'
    _order = 'id desc'
    _rec_name = 'id'

    tags = fields.Many2many('asterisk_calls.tag',
                            relation='asterisk_calls_call_tag',
                            column1='tag', column2='call')
    tags_list = fields.Char(compute=lambda self: self._get_tags_list(),
                            string=_('Tags'))
    partner = fields.Many2one('res.partner', ondelete='set null',
                              tracking=True)
    partner_company = fields.Many2one(related='partner.parent_id')
    src_user = fields.Many2one('res.users', ondelete='set null', readonly=True,
                               string=_('From User'))
    dst_user = fields.Many2one('res.users', ondelete='set null', readonly=True,
                               string=_('To User'))
    notes = fields.Text(tracking=True)
    notes_short = fields.Char(compute='_get_notes_short', string=_('Notes'))
    in_library = fields.Boolean()
    is_private = fields.Boolean(string=_('Private'),
                                help=_('Only call party will have access.'))
    channel_short = fields.Char(
        compute='_get_channel_short', string=_('Channel'))
    dstchannel_short = fields.Char(
        compute='_get_dstchannel_short', string=_('Dest channel'))
    # Recordings
    recording_filename = fields.Char(readonly=True, index=True)
    recording_data = fields.Binary(readonly=True, string=_('Download'))
    recording_attachment = fields.Binary(attachment=True, string=_('Download'))
    recording_widget = fields.Char(compute='_get_recording_widget',
                                   string='Recording')
    recording_icon = fields.Char(compute='_get_recording_icon', string='R')
    # Asterisk fields
    accountcode = fields.Char(size=20, string='Account code', index=True,
                              readonly=True)
    src = fields.Char(size=80, string='Source', index=True, readonly=True)
    dst = fields.Char(size=80, string='Destination', index=True, readonly=True)
    dcontext = fields.Char(size=80, string='Destination context',
                           readonly=True)
    clid = fields.Char(size=80, string='Caller ID', index=True, readonly=True)
    channel = fields.Char(size=80, string='Channel', index=True, readonly=True)
    dstchannel = fields.Char(size=80, string='Destination channel', index=True,
                             readonly=True)
    lastapp = fields.Char(size=80, string='Last app', readonly=True)
    lastdata = fields.Char(size=80, string='Last data', readonly=True)
    started = fields.Datetime(index=True, readonly=True)
    answered = fields.Datetime(index=True, readonly=True)
    ended = fields.Datetime(index=True, readonly=True)
    duration = fields.Integer(string='Call Duration', index=True,
                              readonly=True)
    duration_human = fields.Char(
        string=_('Call Duration'),
        compute=lambda self: self._compute_duration_human())
    billsec = fields.Integer(string='Talk Time', index=True, readonly=True)
    billsec_human = fields.Char(
        string=_('Talk Time'),
        compute=lambda self: self._compute_billsec_human())
    disposition = fields.Char(size=45, string='Disposition',
                              index=True, readonly=True)
    amaflags = fields.Char(size=20, string='AMA flags', readonly=True)
    userfield = fields.Char(size=255, string='Userfield', readonly=True)
    uniqueid = fields.Char(size=150, string='Unique ID', index=True,
                           readonly=True)
    peeraccount = fields.Char(size=80, string='Peer account',
                              index=True, readonly=True)
    linkedid = fields.Char(size=150, string='Linked ID', readonly=True)
    sequence = fields.Integer(string='Sequence', readonly=True)
    system_name = fields.Char(size=32)
    # QoS
    # Our side
    ssrc = fields.Char(string=_('Our Synchronization source'), readonly=True)
    rxcount = fields.Integer(string='Received Packets', readonly=True)
    rxjitter = fields.Float(string='Our Jitter', readonly=True)
    # Their side
    themssrc = fields.Char(string=_('Their Synchronization source'),
                           readonly=True)
    lp = fields.Integer(string=_('Local Lost Packets'), readonly=True)
    rlp = fields.Integer(string=_('Remote Lost Packets'), readonly=True)
    txjitter = fields.Float(string='Their Jitter', readonly=True)
    txcount = fields.Integer(string='Transmitted Packets', readonly=True)
    rtt = fields.Float(string=_('Round Trip Time'), readonly=True)
    is_qos_bad = fields.Html(compute='_is_qos_bad', string='QoS')

    def write(self, vals):
        for rec in self:
            if not rec.partner and vals.get('partner'):
                # Let set partner phone
                super(Call, self).write(vals)
                # Guess number
                if rec.dst and rec.src_user:
                    number = rec.dst
                elif rec.src and rec.dst_user:
                    number = rec.src
                else:
                    # Cannot guess number
                    continue
                # Check if number is already present
                # Odoo 10
                if release.version[:2] == '10':
                    if number in [rec.partner.phone, rec.partner.mobile,
                                  rec.partner.fax]:
                        continue
                # For Odoo 11 & 12
                elif number in [rec.partner.phone, rec.partner.mobile]:
                    continue
                # Fill partner phones
                if not rec.partner.phone:
                    rec.partner.phone = number
                elif not rec.partner.mobile:
                    rec.partner.mobile = number
                elif release.version[:2] == '10' and not rec.partner.fax:
                    rec.partner.fax = number
                else:
                    # No free slots for new number, so do nothing
                    continue
            else:
                # Just update partner
                super(Call, self).write(vals)
        return True

    def toggle_library(self):
        self.ensure_one()
        if not (self.env.user.has_group(
                'asterisk_common.group_asterisk_admin')
                or self.env.user == self.dst_user
                or self.env.user == self.src_user):
            raise ValidationError(
                _('You must be admin or one part of the call to change it!'))
        self.in_library = not self.in_library

    @api.constrains('in_library', 'is_private')
    def check_lib_conditions(self):
        self.ensure_one()
        if self.in_library and self.is_private:
            raise ValidationError(
                _('You cannot add priviate call to the Library!'))

    def _get_tags_list(self):
        for rec in self:
            rec.tags_list = u', '.join([k.name for k in rec.tags])

    def _get_channel_short(self):
        for rec in self:
            rec.channel_short = '-'.join(rec.channel.split('-')[:-1])

    def _get_dstchannel_short(self):
        for rec in self:
            rec.dstchannel_short = '-'.join(rec.dstchannel.split('-')[:-1])

    def _get_recording_icon(self):
        for rec in self:
            if rec.recording_filename:
                if release.version[:2] > '10':
                    rec.recording_icon = '<span class="fa fa-file-sound-o"/>'
                else:
                    rec.recording_icon = _('Yes')
            else:
                rec.recording_icon = ''

    def _get_notes_short(self):
        for rec in self:
            if not rec.notes:
                rec.notes_short = ''
            elif len(rec.notes) <= 40:
                rec.notes_short = rec.notes
            else:
                rec.notes_short = u'{}...'.format(rec.notes[:40])

    def _compute_billsec_human(self):
        for rec in self:
            rec.billsec_human = str(timedelta(seconds=rec.billsec))

    def _compute_duration_human(self):
        for rec in self:
            rec.duration_human = str(timedelta(seconds=rec.duration))

    def open_form(self):
        self.ensure_one()
        return {
            'res_model': 'asterisk_calls.call',
            'res_id': self.id,
            'name': _('Call Log'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }

    def open_partner_form(self):
        self.ensure_one()
        return {
            'res_model': 'res.partner',
            'res_id': self.partner.id,
            'name': _('Partner'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {
                'default_phone': self.dst if self.src_user else self.src,
                'create_call_partner': self.id,
            },
        }

    @api.model
    def update_cdr_values(self, original_vals):
        vals = {}
        src = original_vals.get('src')
        dst = original_vals.get('dst')
        system_name = original_vals.get('system_name')
        dst_channel_short = '-'.join(original_vals.get(
            'dstchannel', '').split('-')[:-1])
        src_channel_short = '-'.join(original_vals.get(
            'channel', '').split('-')[:-1])
        # Get src user by channel
        ast_src_user_id = self.env[
            'asterisk_common.user'].get_res_user_id_by_channel(
            src_channel_short, system_name)
        if not ast_src_user_id:
            # Try to get src user by extension
            ast_src_user_id = self.env[
                'asterisk_common.user'].get_res_user_id_by_exten(
                src, system_name)
        if ast_src_user_id:
            vals['src_user'] = ast_src_user_id
        # Get dst user by channel
        ast_dst_user_id = self.env[
            'asterisk_common.user'].get_res_user_id_by_channel(
            dst_channel_short, system_name)
        if not ast_dst_user_id:
            ast_dst_user_id = self.env[
                'asterisk_common.user'].get_res_user_id_by_exten(
                dst, system_name)
        if ast_dst_user_id:
            vals['dst_user'] = ast_dst_user_id
        # Now get partner, first check if it's originated from click2call.
        originate_data = self.env['kv_cache.cache'].get(
            original_vals.get('uniqueid'), tag='originated_call',
            serialize='json')
        logger.debug('ORIGINATED_CALL_DATA: %s', json.dumps(
            originate_data, indent=2))
        if originate_data.get('model') == 'res.partner' and \
                originate_data.get('res_id'):
            vals['partner'] = originate_data['res_id']
            logger.debug('FOUND PARTNER BY ORIGINATE DATA.')
        elif ast_src_user_id:
            # Get partner for destination as call is from user
            partner_info = self.env[
                'res.partner'].get_partner_by_number(dst)
            vals['partner'] = partner_info['id']
        elif ast_dst_user_id:
            # Get partner for source as call is to user
            partner_info = self.env['res.partner'].get_partner_by_number(src)
            vals['partner'] = partner_info['id']
        else:
            # No users in the call - assume this is incoming call
            partner_info = self.env['res.partner'].get_partner_by_number(src)
            vals['partner'] = partner_info['id']
        return vals

    @api.model
    def create_cdr(self, event):
        def get(val):
            res = event.get(val)
            if res is None:
                return ''
            else:
                return res
        data = {
            'accountcode': get('AccountCode'),
            'src': get('Source'),
            'dst': get('Destination'),
            'dcontext': get('DestinationContext'),
            'clid': get('CallerID'),
            'channel': get('Channel'),
            'dstchannel': get('DestinationChannel'),
            'lastapp': get('LastApplication'),
            'lastdata': get('LastData'),
            'started': get('StartTime') or False,
            'answered': get('AnswerTime') or False,
            'ended': get('EndTime') or False,
            'duration': get('Duration'),
            'billsec': get('BillableSeconds'),
            'disposition': get('Disposition'),
            'amaflags': get('AMAFlags'),
            'uniqueid': get('UniqueID') or get('Uniqueid'),
            'linkedid': get('Linkedid'),
            'userfield': get('UserField'),
            'system_name': get('SystemName'),
        }
        try:
            data.update(self.update_cdr_values(data))
        except Exception:
            logger.exception('[ODOO_ERROR]')
        self.with_context(tracking_disable=True).create(data)
        return True

    @api.model
    def create(self, vals):
        # Update timezone
        if self.env.user.tz:
            try:
                server_tz = pytz.timezone(self.env.user.tz)
                convert_fields = ['started', 'answered', 'ended']
                for field in convert_fields:
                    if field in vals and vals[field]:
                        dt_no_tz = fields.Datetime.from_string(vals[field])
                        dt_server_tz = server_tz.localize(dt_no_tz,
                                                          is_dst=None)
                        dt_utc = dt_server_tz.astimezone(pytz.utc)
                        vals[field] = fields.Datetime.to_string(dt_utc)
            except Exception:
                logger.exception('Error adjusting timezone for Call')
        _call = super(Call, self).create(vals)
        call = _call.sudo(True)  # Multi company hack
        # Subscribe users if any
        subscribe_list = [
            k.partner_id.id for k in [call.dst_user, call.src_user] if k]
        if subscribe_list:
            call.message_subscribe(partner_ids=subscribe_list)
        # Call notification
        try:
            _call.register_call()
        except Exception:
            logger.exception('Register call error:')
        return _call

    def register_call(self):
        self.ensure_one()
        # Agent does not have access to res.users.
        call = self.sudo()
        # Missed calls to users
        asterisk_user = call.dst_user.asterisk_users.filtered(
            lambda x: x.system_name == call.system_name)
        if call.disposition != 'ANSWERED' and call.dst_user and \
                asterisk_user.missed_calls_notify:
            call_from = call.src
            if call.partner:
                call_from = call.partner.name
            elif call.src_user:
                call_from = call.src_user.name
            call.message_post(
                subject=_('Missed call notification'),
                body=_('You have a missed call from {}').format(
                    call_from),
                partner_ids=[call.dst_user.partner_id.id],
            )
        if call.partner:
            if call.disposition != 'ANSWERED':
                # Missed call
                if call.dst_user:
                    message = _('Missed call ({}) to {}.').format(
                        call.disposition.lower(), call.dst_user.name)
                elif call.src_user:
                    message = _('Missed call ({}) from {}.').format(
                        call.disposition.lower(), call.src_user.name)
                else:
                    message = _('Missed call ({}) from {} to {}.').format(
                        call.disposition.lower(), call.src, call.dst)
            else:
                # Answered call
                if call.dst_user:
                    message = _('Answered call to {}.').format(
                        call.dst_user.name)
                elif call.src_user:
                    message = _('Answered call from {}.').format(
                        call.src_user.name)
                else:
                    message = _('Answered call from {} to {}.').format(
                        call.src, call.dst)
            self.env['mail.message'].sudo().create({
                'subject': '',
                'body': message,
                'model': 'res.partner',
                'res_id': call.partner.id,
                'message_type': 'comment',
                'subtype_id': self.env[
                    'ir.model.data'].xmlid_to_res_id(
                    'mail.mt_note'),
                'email_from': self.env.user.partner_id.email,
            })

    @api.model
    def delete_calls(self):
        # Archive call history
        days = self.env[
            'asterisk_common.settings'].get_param('calls_keep_days')
        expire_date = datetime.utcnow() - timedelta(days=int(days))
        expired_calls_ids = self.env['asterisk_calls.call']._search([
            ('ended', '<=', expire_date.strftime('%Y-%m-%d %H:%M:%S'))
        ])
        logger.info('Expired {} calls'.format(len(expired_calls_ids)))
        try:
            for call_id in expired_calls_ids:
                call = self.browse(call_id)
                call.unlink()
                self.env.cr.commit()
        except Exception as e:
            # Log exception and go ahead
            logger.exception(e)
        finally:
            self.env['ir.attachment']._file_gc()
        # Archive recordings
        rec_days = self.env[
            'asterisk_common.settings'].get_param('recordings_keep_days')
        rec_expire_date = datetime.utcnow() - timedelta(days=int(rec_days))
        rec_expired_calls_ids = self.env['asterisk_calls.call']._search([
            ('ended', '<=', rec_expire_date.strftime('%Y-%m-%d %H:%M:%S')),
            ('recording_filename', '!=', False)
        ])
        logger.info('Expired {} recordings'.format(len(rec_expired_calls_ids)))
        try:
            for rec_call_id in rec_expired_calls_ids:
                rec_call = self.browse(rec_call_id)
                rec_call.write({
                    'recording_data': False,
                    'recording_filename': False,
                    'recording_attachment': False,
                })
                self.env.cr.commit()
        except Exception as e:
            # Log exception and go ahead
            logger.exception(e)
        finally:
            self.env['ir.attachment']._file_gc()

    def _get_recording_widget(self):
        recording_storage = self.env[
            'asterisk_common.settings'].sudo().get_param('recording_storage')
        if recording_storage == 'db':
            recording_source = 'recording_data'
        else:
            recording_source = 'recording_attachment'
        for rec in self:
            rec.recording_widget = '<audio id="sound_file" preload="auto" ' \
                'controls="controls"> ' \
                '<source src="/web/content?model=asterisk_calls.call&' \
                'id={recording_id}&filename={filename}&field={source}&' \
                'filename_field=recording_filename&download=True" />' \
                '</audio>'.format(
                    recording_id=rec.id,
                    filename=rec.recording_filename,
                    source=recording_source)

    def _is_qos_bad(self):
        for rec in self:
            rec.is_qos_bad = '<span class="fa fa-warning"/>' if (
                rec.lp > 2 or rec.rlp > 2) else False

    @api.model
    def update_qos(self, values):
        values = values[0]
        uniqueid = values.get('uniqueid')
        linkedid = values.get('linkedid')
        # TODO Probably we need to optimize db query on millions of records.
        cdrs = self.env['asterisk_calls.call'].search([
            ('started', '>', (datetime.now() - timedelta(
                seconds=120)).strftime('%Y-%m-%d %H:%M:%S')),
            ('uniqueid', '=', uniqueid),
            ('linkedid', '=', linkedid),
        ])
        if not cdrs:
            logger.info('Omitting QoS, CDR not found, uniqueid {}!'.format(
                uniqueid))
            return False
        else:
            logger.debug('Found CDR for QoS.')
            cdr = cdrs[0]
            cdr.write({
                'ssrc': values.get('ssrc'),
                'themssrc': values.get('themssrc'),
                'lp': int(values.get('lp', '0')),
                'rlp': int(values.get('rlp', '0')),
                'rxjitter': float(values.get('rxjitter', '0')),
                'txjitter': float(values.get('txjitter', '0')),
                'rxcount': int(values.get('rxcount', '0')),
                'txcount': int(values.get('txcount', '0')),
                'rtt': float(values.get('rtt', '0')),
            })
            # Notify QoS channel if QoS is bad
            if cdr.lp >= 0 or cdr.rlp >= 0:
                channel = self.sudo(True).env.ref('asterisk_calls.qos_channel')
                if channel:
                    fields = []
                    fields.append('UniqueID: {}'.format(cdr.uniqueid))
                    fields.append('lp: {}'.format(cdr.lp))
                    fields.append('rlp: {}'.format(cdr.rlp))
                    if cdr.partner:
                        fields.append('partner: {}'.format(cdr.partner.name))
                    if cdr.src_user:
                        fields.append('from: {}'.format(cdr.src_user.name))
                    if cdr.dst_user:
                        fields.append('to: {}'.format(cdr.dst_user.name))
                    channel[0].message_post(
                        body=', '.join(fields),
                        subject=_('Bad QoS'),
                        subtype='mail.mt_comment',
                        model='asterisk_calls.call',
                        res_id=cdr.id,
                    )
            return True

    @api.model
    def save_call_recording(self, event):
        data = event
        unique_id = data.get('Uniqueid')
        logger.debug('Save call recording for call ID {}.'.format(unique_id))
        # Check if we have MIXMONITOR event.
        file_path = self.env['kv_cache.cache'].get(
            unique_id, tag='MIXMONITOR_FILENAME', clean=True)
        if not file_path:
            logger.debug('Recording was not activated for call ID %s',
                         unique_id)
            return False
        # This is called a few seconds after call Hangup, so filter calls
        # by time first.
        recently = datetime.utcnow() - timedelta(seconds=60)
        rec = self.env['asterisk_calls.call'].search([
            ('create_date', '>=', recently.strftime('%Y-%m-%d %H:%M:%S')),
            ('uniqueid', '=', unique_id)],
            limit=1)
        if not rec:
            logger.debug('CDR not found by id {}.'.format(unique_id))
            return False
        if not rec.disposition == 'ANSWERED':
            logger.debug('RECORDING ACTIVATED BUT CALL WAS NOT ANSWERED')
            return False
        logger.debug('Found CDR for call id {}.'.format(unique_id))
        system = data.get('SystemName', 'asterisk')
        self.env['remote_agent.agent'].send_agent(
            system, {
                'command': 'nameko_rpc',
                'service': '{}_files'.format(system),
                'method': 'get_file',
                'callback_model': 'asterisk_calls.call',
                'callback_method': 'call_recording_data',
                'args': [file_path],
                'pass_back': {
                    'file_path': file_path,
                    'call_id': rec.id,
                }
            })
        return True

    @staticmethod
    def _wav_to_mp3(file_data, bit_rate, quality):
        started = time.time()
        wav_data = wave.open(file_data)
        num_channels = wav_data.getnchannels()
        sample_rate = wav_data.getframerate()
        num_frames = wav_data.getnframes()
        pcm_data = wav_data.readframes(num_frames)
        logger.debug('Encoding Wave file. Number of channels: '
                    '{}. Sample rate: {}, Number of frames: {}'.format(
                        num_channels, sample_rate, num_frames
                    ))
        wav_data.close()

        encoder = lameenc.Encoder()
        encoder.set_bit_rate(bit_rate)
        encoder.set_in_sample_rate(sample_rate)
        encoder.set_channels(num_channels)
        encoder.set_quality(quality)  # 2-highest, 7-fastest
        mp3_data = encoder.encode(pcm_data)
        mp3_data += encoder.flush()
        logger.info('Recording convert .wav -> .mp3 took %.2f seconds.',
                    time.time() - started)
        return mp3_data

    @api.model
    def call_recording_data(self, data):
        call_id = data.get('pass_back', {}).get('call_id')
        logger.debug('Call recording data for ID %s', call_id)
        input_data = data.get('result', {}).get('file_data')
        if data.get('error'):
            msg = data['error'].get('message', data['error'])
            logger.error('Call recording data error: %s', msg)
            return False
        call = self.env['asterisk_calls.call'].browse(call_id)
        mp3_encode = self.env['asterisk_common.settings'].get_param(
            'use_mp3_encoder')
        if LAMEENC and mp3_encode:
            bit_rate = int(self.env['asterisk_common.settings'].get_param(
                'mp3_encoder_bitrate', default=96))
            quality = int(self.env['asterisk_common.settings'].get_param(
                'mp3_encoder_quality', default=4))
            decoded_input = base64.b64decode(input_data)
            output_data = base64.b64encode(
                self._wav_to_mp3(io.BytesIO(decoded_input), bit_rate, quality))
            extension = 'mp3'
        else:
            output_data = input_data
            extension = 'wav'
        if self.env['asterisk_common.settings'].get_param(
                'recording_storage') == 'db':
            call.write({
                'recording_data': output_data,
                'recording_filename': '{}.{}'.format(call.uniqueid, extension)})
        else:
            call.write({
                'recording_attachment': output_data,
                'recording_filename': '{}.{}'.format(call.uniqueid, extension)})
        # Delete recording from the Asterisk server
        if self.env['asterisk_common.settings'].get_param('delete_recordings'):
            logger.debug('CALL DELETE RECORDING %s',
                         data.get('pass_back', {}).get('file_path'))
            self.env['remote_agent.agent'].send_agent(
                self.env.user.remote_agent.system_name, {
                    'command': 'nameko_rpc',
                    'service': '{}_files'.format(
                        self.env.user.remote_agent.system_name),
                    'method': 'delete_file',
                    'delay': 10,  # Remove the file in 10 seconds after.
                    'args': [data.get('pass_back', {}).get('file_path')],
                })
        try:
            call.sudo().register_call_recording()
        except Exception:
            logger.exception('Register call recording error:')
        return True

    def register_call_recording(self):
        self.ensure_one()
        # TEMPORARY LINK INSTEAD OF <AUDIO>
        recording_storage = self.env[
            'asterisk_common.settings'].sudo().get_param('recording_storage')
        if recording_storage == 'db':
            recording_source = 'recording_data'
        else:
            recording_source = 'recording_attachment'
        message = '<a href="/web/content?model=asterisk_calls.call&' \
                'id={}&filename={}&field={}&' \
                'filename_field=recording_filename&download=True">' \
                'Download call recording</a>'.format(
                    self.id, self.recording_filename, recording_source)
        if self.partner:
            self.env['mail.message'].sudo().create({
                'subject': '',
                # 'body': self.recording_widget,
                'body': message,
                'model': 'res.partner',
                'res_id': self.partner.id,
                'message_type': 'comment',
                'subtype_id': self.env[
                    'ir.model.data'].xmlid_to_res_id(
                    'mail.mt_note'),
                'email_from': self.env.user.partner_id.email,
            })
