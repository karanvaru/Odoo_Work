from datetime import datetime, timedelta
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Channel(models.Model):
    _name = 'asterisk_calls.channel'
    _rec_name = 'channel'
    _description = 'Active Call'

    partner = fields.Many2one('res.partner', ondelete='set null')
    src_user = fields.Many2one('res.users', string=_('From'),
                               ondelete='set null')
    dst_user = fields.Many2one('res.users', string=_('To'),
                               ondelete='set null')
    is_muted = fields.Boolean(string='Muted')
    callerid = fields.Char(compute='_get_callerid', string=_('Caller ID'))
    connected_line = fields.Char(compute='_get_connected_line')
    duration = fields.Char(compute='_get_duration')
    # Asterisk fields
    channel = fields.Char(index=True)
    channel_short = fields.Char(compute='_get_channel_short',
                                string=_('Channel'))
    uniqueid = fields.Char(size=150, index=True)
    linkedid = fields.Char(size=150, index=True)
    context = fields.Char(size=80)
    connected_line_num = fields.Char(size=80)
    connected_line_name = fields.Char(size=80)
    state = fields.Char(size=80)
    state_desc = fields.Char(size=256, string=_('State'))
    exten = fields.Char(size=32)
    callerid_num = fields.Char(size=32)
    callerid_name = fields.Char(size=32)
    system_name = fields.Char(size=32)
    accountcode = fields.Char(size=80)
    priority = fields.Char(size=4)
    timestamp = fields.Char(size=20)
    app = fields.Char(size=32, string='Application')
    app_data = fields.Char(size=512, string='Application Data')
    language = fields.Char(sise=2)
    event = fields.Char(size=64)
    # Security rule
    is_user_channel = fields.Boolean(compute='_is_user_channel', store=True)

    def _get_callerid(self):
        for rec in self:
            if rec.callerid_num and 'unknown' not in rec.callerid_num and \
                    'unknown' not in rec.callerid_name:
                rec.callerid = u'{} <{}>'.format(rec.callerid_name,
                                                 rec.callerid_num)
            elif rec.callerid_num and 'unknown' in rec.callerid_name and \
                    'unknown' not in rec.callerid_num:
                rec.callerid = '<{}>'.format(rec.callerid_num)
            else:
                rec.callerid = ''

    def _get_channel_short(self):
        for rec in self:
            rec.channel_short = '-'.join(rec.channel.split('-')[:-1])

    def _get_connected_line(self):
        for rec in self:

            if rec.connected_line_num and 'unknown' \
                    not in rec.connected_line_num and \
                    'unknown' not in rec.connected_line_name:
                rec.connected_line = u'{} <{}>'.format(rec.connected_line_name,
                                                       rec.connected_line_num)
            elif rec.connected_line_num and 'unknown' in \
                    rec.connected_line_name and \
                    'unknown' not in rec.connected_line_num:
                rec.connected_line = '<{}>'.format(rec.connected_line_num)
            else:
                rec.connected_line = ''

    def _get_duration(self):
        for rec in self:
            if isinstance(rec.create_date, datetime):
                create_date = rec.create_date
            else:
                create_date = datetime.strptime(rec.create_date,
                                                '%Y-%m-%d %H:%M:%S')
            rec.duration = str(datetime.now() - create_date).split('.')[0]

    @api.depends('channel')
    def _is_user_channel(self):
        # True if channel is defined as user channel
        for rec in self:
            rec.is_user_channel = bool(
                self.env['asterisk_common.user_channel'].search_count(
                    [('channel', '=', rec.channel_short)]))

    @api.model
    def update_channel_values(self, original_values):
        logger.debug('UPDATE CHANNEL VALUES: %s',
                     json.dumps(original_values, indent=2))
        values = {}
        # Find source user by caller id
        channel_short = '-'.join(original_values.get(
            'channel').split('-')[:-1])
        linkedid = original_values.get('linkedid')
        uniqueid = original_values.get('uniqueid')
        system_name = original_values.get('system_name')
        callerid_num = original_values.get('callerid_num')
        exten = original_values.get('exten')
        connected_line_num = original_values.get('connected_line_num')
        user_by_channel = self.env[
            'asterisk_common.user'].get_res_user_id_by_channel(
            channel_short, system_name)
        user_by_exten = self.env[
            'asterisk_common.user'].get_res_user_id_by_exten(
            exten, system_name)
        user_by_connected = self.env[
            'asterisk_common.user'].get_res_user_id_by_exten(
            connected_line_num, system_name)
        partner_by_exten = self.env[
            'res.partner'].get_partner_by_number(exten)['id']
        partner_by_callerid = self.env[
            'res.partner'].get_partner_by_number(callerid_num)['id']
        partner_by_connected = self.env[
            'res.partner'].get_partner_by_number(connected_line_num)['id']
        # First try get call originated data
        logger.debug('USER_BY_EXTEN: %s, USER_BY_CHANNEL: %s, USER BY CONNECTED: %s',
                     user_by_exten, user_by_channel, user_by_connected)
        logger.debug(
            'PARTNER_BY_EXTEN: %s, PARTNER_BY_CLID: %s, PARTNER_BY_CONNECTED: %s',
            partner_by_exten, partner_by_callerid, partner_by_connected)
        originate_data = self.env['kv_cache.cache'].get(
            original_values.get('uniqueid'), tag='originated_call',
            serialize='json')
        # We took channel data from cache so if it's one of multiple originated
        # channels this is a good place to hangup the rest channels.
        if original_values.get('state_desc') == 'Up' and originate_data and \
                originate_data.get('originate_channels') and \
                len(originate_data['originate_channels']) > 1:
            # More channels are originating.
            other_channels = set(
                originate_data['originate_channels'].keys()) - set([channel_short])
            for other_channel in other_channels:
                # Send hangup request
                data = {
                    'command': 'nameko_rpc',
                    'service': '{}_ami'.format(system_name),
                    'method': 'send_action',
                    'args': [{
                        'Action': 'Hangup',
                        'Channel': originate_data['originate_channels'][other_channel]['channel_id']
                    }],
                    'pass_back': {'uid': self.env.user.id},
                }
                self.env['remote_agent.agent'].send_agent(system_name, data)

        if uniqueid == linkedid:
            # 1-st case: user click2dial originated call, we have also partner.
            if originate_data:
                logger.debug('USER %s CLICK2DIAL ORIGINATED CALL',
                             originate_data)
                if originate_data and originate_data.get('uid'):
                    # We have originated user
                    logger.debug('ORIGINATED_CALL_DATA: %s', json.dumps(
                        originate_data, indent=2))
                    values['src_user'] = originate_data.get('uid')
                    if originate_data.get('model') == 'res.partner' and \
                            originate_data.get('res_id'):
                        logger.debug('CHANNEL PARTNER GOT FROM ORIGINATE DATA')
                        values['partner'] = originate_data.get('res_id')

            # 2-nd case: inter user call
            elif user_by_channel and user_by_exten:
                logger.debug('INTERNAL CALL FROM %s TO %s',
                             user_by_channel, user_by_exten)
                values['src_user'] = user_by_channel
                values['dst_user'] = user_by_exten
                values['partner'] = partner_by_connected

            # 3-rd case: external outgoing call
            elif user_by_channel:
                values['src_user'] = user_by_channel
                values['partner'] = partner_by_exten or partner_by_callerid
                logger.debug('CHANNEL EXTERNAL OUTGOING CALL FROM %s TO %s',
                             user_by_channel, partner_by_exten)

            # 4-rd case: external incoming call to user
            elif user_by_exten:
                # Get partner from callerid number
                values['dst_user'] = user_by_exten
                values['partner'] = partner_by_callerid or partner_by_connected
                logger.debug('CHANNEL EXTERNAL INCOMING CALL FROM %s TO %s',
                             user_by_exten,
                             partner_by_callerid or partner_by_connected)

            # 5-rd case: external incoming call not connected to users.
            else:
                values['partner'] = partner_by_callerid

        else:
            logger.debug('CHANNEL LINKEDID != UNIQUEID')
            linked_channels = self.search([('uniqueid', '=', linkedid)])
            for chan in linked_channels:
                if chan.src_user and not values.get('src_user'):
                    logger.debug('SETTING SRC USER FROM LINKED CHANNEL')
                    values['src_user'] = chan.src_user.id
                if chan.dst_user and not values.get('dst_user'):
                    logger.debug('SETTING DST USER FROM LINKED CHANNEL')
                    values['dst_user'] = chan.dst_user.id
                if chan.partner and not values.get('partner'):
                    logger.debug('SETTING PARTNER FROM LINKED CHANNEL')
                    values['partner'] = chan.partner.id
            # External call from trunk to user
            if not values.get('dst_user') and user_by_channel:
                logger.debug('CHANNEL EXTERNAL CALL TO USER %s BY CHANNEL %s',
                             user_by_channel, channel_short)
                values['dst_user'] = user_by_channel
            elif not values.get('src_user') and user_by_connected:
                values['src_user'] = user_by_connected
                logger.debug('CHANNEL USER %s BY CONNECTED NUM %s',
                             user_by_connected, connected_line_num)
        return values

    @api.model
    def new_channel(self, event, skip_check=False):
        values = event
        if not skip_check:
            channel = self.env['asterisk_calls.channel'].search(
                [('uniqueid', '=', values.get('Uniqueid'))])
            if channel:
                logger.debug('CHANNEL %s UPDATE BEFORE new_channel',
                             values.get('Channel'))
                return False
        data = {
            'channel': values.pop('Channel', ''),
            'uniqueid': values.pop('Uniqueid', ''),
            'linkedid': values.pop('Linkedid', ''),
            'context': values.pop('Context', ''),
            'connected_line_num': values.pop('ConnectedLineNum', ''),
            'connected_line_name': values.pop('ConnectedLineName', ''),
            'state': values.pop('ChannelState', ''),
            'state_desc': values.pop('ChannelStateDesc', ''),
            'exten': values.pop('Exten', ''),
            'callerid_num': values.pop('CallerIDNum', ''),
            'callerid_name': values.pop('CallerIDName', ''),
            'accountcode': values.pop('AccountCode', ''),
            'priority': values.pop('Priority', ''),
            'timestamp': values.pop('Timestamp', ''),
            'system_name': values.pop('SystemName', 'asterisk'),
            'language': values.pop('Language', ''),
            'event': values.pop('Event', ''),
        }
        # Update channel dst / src users, partner
        updated_data = self.update_channel_values(data)
        data.update(updated_data)
        logger.debug('CREATING CHANNEL %s.', data['channel'])
        channel = self.env['asterisk_calls.channel'].create(data)
        logger.debug('NEW CHANNEL %s UPDATED DATA: %s',
                     channel.channel_short, updated_data)
        self.env.cr.commit()
        caller = channel.partner.name or channel.src_user.name or \
            channel.callerid or channel.connected_line
        if channel.dst_user and caller:
            asterisk_user = channel.dst_user.asterisk_users.filtered(
                lambda x: x.system_name == channel.system_name)
            channel.notify_user(
                asterisk_user, 'Incoming call from {}'.format(caller))
        channel.reload_channels()
        return True

    @api.model
    def reload_channels(self):
        auto_reload = self.env[
            'asterisk_common.settings'].get_param('auto_reload_channels')
        self.env['bus.bus'].sendone('asterisk_calls_channels', json.dumps({
            'event': 'update_channel',
            'dst': self.exten,
            'system_name': self.system_name,
            'channel': self.channel_short,
            'partner_id': self.partner.id,
            'auto_reload': auto_reload}))

    @api.model
    def update_channel_state(self, event):
        get = event.get
        # Find the channel
        channel = self.env['asterisk_calls.channel'].search([
            ('uniqueid', '=', get('Uniqueid'))], limit=1)
        if not channel:
            logger.debug('CREATE CHANNEL {} FOR STATE UPDATE.'.format(
                get('Channel')))
            return self.new_channel(event, skip_check=True)
        data = {
            'channel': get('Channel'),
            'uniqueid': get('Uniqueid'),
            'linkedid': get('Linkedid'),
            'context': get('Context'),
            'connected_line_num': get('ConnectedLineNum'),
            'connected_line_name': get('ConnectedLineName'),
            'state': get('ChannelState'),
            'state_desc': get('ChannelStateDesc'),
            'exten': get('Exten'),
            'callerid_num': get('CallerIDNum'),
            'callerid_name': get('CallerIDName'),
            'accountcode': get('AccountCode'),
            'priority': get('Priority'),
            'timestamp': get('Timestamp'),
            'system_name': get('SystemName', 'asterisk'),
            'language': get('Language'),
            'event': get('Event'),
        }
        # Update channel dst / src users, partner
        new_data = self.update_channel_values(data)
        logger.debug('UPDATE CHANNEL %s UPDATED DATA: %s',
                     channel.channel_short, new_data)
        data.update(new_data)
        logger.debug('UPDATE CHANNEL %s.', data['channel'])
        # Check if partner is updated from new data
        if not channel.partner and new_data.get('partner'):
            notify = True
        else:
            notify = False
        # Update channel
        channel.write(data)
        self.env.cr.commit()
        if notify:
            caller = channel.partner.name or channel.src_user.name or \
                channel.callerid or channel.connected_line
            if channel.dst_user:
                asterisk_user = channel.dst_user.asterisk_users.filtered(
                    lambda x: x.system_name == channel.system_name)
                channel.notify_user(asterisk_user,
                                    'Incoming call from {}'.format(caller))
        channel.reload_channels()
        return True

    @api.model
    def hangup_channel(self, event):
        # Agent's RPC
        uniqueid = event.get('Uniqueid')
        channel = event.get('Channel')
        found = self.env['asterisk_calls.channel'].search(
            [('uniqueid', '=', uniqueid)])        
        if not found:
            logger.info('Channel {} not found for hangup.'.format(uniqueid))
            return False
        logger.debug('Found %s channel(s) %s', len(found), channel)
        # Sometimes more then one channel can exist.
        # Remove them all but use one for values.
        system_name = found[0].system_name
        # Notify users, sometimes there is more then one chahnel, take the 1-st
        for user in [found[0].src_user, found[0].dst_user]:
            if user:
                asterisk_user = user.asterisk_users.filtered(
                    lambda x: x.system_name == found[0].system_name)
                found[0].notify_user(
                    asterisk_user,
                    'Call hangup, cause {}'.format(event['Cause-txt']),
                    is_sticky=False)
        found.unlink()
        self.env.cr.commit()
        auto_reload = self.env[
            'asterisk_common.settings'].get_param('auto_reload_channels')
        self.env['bus.bus'].sendone('asterisk_calls_channels', json.dumps({
            'event': 'hangup_channel',
            'system_name': found[0].system_name,
            'auto_reload': auto_reload}))
        return True

    @api.model
    def update_monitor_filename(self, event):
        if event.get('Variable') == 'MIXMONITOR_FILENAME':
            file_path = event['Value']
            uniqueid = event['Uniqueid']
            channels = self.search([('uniqueid', '=', uniqueid)], limit=1)
            for chan in channels:
                self.env['kv_cache.cache'].put(
                    uniqueid, file_path, tag='MIXMONITOR_FILENAME')
            return True
        return False

    def pickup(self):
        self.ensure_one()
        asterisk_user = self.env.user.asterisk_users.filtered(
            lambda x: x.system_name == self.system_name)
        if not asterisk_user:
            raise ValidationError(
                _('PBX user is not configured!'))
        for channel in asterisk_user.channels:
            self.env['remote_agent.agent'].send_agent(
                self.system_name,
                {'command': 'nameko_rpc',
                 'service': '{}_ami'.format(self.system_name),
                 'method': 'send_action',
                 'status_notify_uid': self.env.uid,
                 'pass_back': {'uid': self.env.user.id},
                 'args': [{
                     'Action': 'Redirect',
                     'Channel': self.channel,
                     'Context': asterisk_user.originate_context,
                     'Priority': '1',
                     'Exten': asterisk_user.exten}]})

    def _spy(self, option):
        self.ensure_one()
        asterisk_user = self.env.user.asterisk_users.filtered(
            lambda x: x.system_name == self.system_name)
        if not asterisk_user:
            raise ValidationError(
                _('PBX user is not configured!'))
        if option == 'q':
            callerid = 'Spy'
        elif option == 'qw':
            callerid = 'Whisper'
        elif option == 'qB':
            callerid = 'Barge'
        else:
            callerid = 'Unknown'
        originated = False
        for user_channel in asterisk_user.channels:
            if not user_channel.originate_enabled:
                logger.info('User %s channel %s not enabled to originate.',
                            self.env.user.id, user_channel.channel)
                continue
            self.env['remote_agent.agent'].send_agent(
                self.system_name,
                {'command': 'nameko_rpc',
                 'service': '{}_ami'.format(self.system_name),
                 'method': 'send_action',
                 'status_notify_uid': self.env.uid,
                 'pass_back': {'uid': self.env.user.id},
                 'args': [{
                     'Action': 'Originate',
                     'Callerid': '{} <1234567890>'.format(callerid, self.exten),
                     'Channel': user_channel.channel,
                     'Application': 'ChanSpy',
                     'Data': '{},{}'.format(self.channel, option),
                     'Variable': asterisk_user._get_originate_vars()
                 }]})
            originated = True
        if not originated:
            raise ValidationError(_('User has not channels to originate!'))

    def listen(self):
        self._spy('q')

    def whisper(self):
        self._spy('qw')

    def barge(self):
        self._spy('qB')

    def _mute(self, state):
        self.ensure_one()
        self.is_muted = True if state == 'off' else False
        self.env['remote_agent.agent'].send_agent(
            self.system_name,
            {'command': 'nameko_rpc',
             'service': '{}_ami'.format(self.system_name),
             'method': 'send_action',
             'status_notify_uid': self.env.uid,
             'pass_back': {'uid': self.env.user.id},
             'args': [{
                 'Action': 'MuteAudio',
                 'Channel': self.channel,
                 'Direction': 'out',
                 'State': state}]})

    def mute(self):
        self._mute('off')

    def unmute(self):
        self._mute('on')

    def hangup_button(self):
        self.ensure_one()
        self.env['remote_agent.agent'].send_agent(
            self.system_name,
            {'command': 'nameko_rpc',
             'service': '{}_ami'.format(self.system_name),
             'method': 'send_action',
             'status_notify_uid': self.env.uid,             
             'pass_back': {'uid': self.env.user.id},
             'args': [{
                 'Action': 'Hangup',
                 'Channel': self.channel,
                 'Cause': '16'}],
             'uid': self.env.user.id})
        self.unlink()
        return {
            'type': 'ir.actions.act_window',
            'target': 'main',
            'res_model': 'asterisk_calls.channel',
            'name': _('Active Calls'),
            'view_mode': 'tree,form',
        }

    @api.model
    def cleanup(self, hours=24):
        # Remove calls created previous day
        yesterday = (datetime.now() - timedelta(
            hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        self.env['asterisk_calls.channel'].search(
                [('create_date', '<', yesterday)]).unlink()

    @api.model
    def dial_end(self, event):
        logger.debug('DIAL END EVENT: %s', event)
        data = {
            'channel': event.get('Channel', ''),
            'exten': event.get('Exten', ''),
            'callerid_num': event.get('DestCallerIDNum', ''),
            'connected_line_num': event.get('DestConnectedLineNum', ''),
            'unique': event.get('DestUniqueid', ''),
            'linkedid': event.get('DestLinkedid', ''),
        }
        res = self.update_channel_values(data)
        uid = res.get('dst_user') or res.get('src_user')
        if uid:
            dial_status = event.get('DialStatus').lower().capitalize()
            asterisk_user = self.env['asterisk_common.user'].search([
                ('user', '=', uid),
                ('system_name', '=', event['SystemName'])
            ])
            self.notify_user(asterisk_user, dial_status, is_sticky=False)
        return True

    def notify_user(self, asterisk_user, message, is_sticky=None):
        res_user = asterisk_user.user
        # Make a savepoint so that is kv cache fails we do not spoil the cursor
        with self.env.cr.savepoint():
            if asterisk_user.call_popup_is_enabled:
                tag = 'channel_notify_user_{}'.format(res_user.id)
                if is_sticky is None:
                    is_sticky = asterisk_user.call_popup_is_sticky
                # Check if user already received this status message
                already_notified = self.env['kv_cache.cache'].get(
                    message, tag=tag)
                if already_notified:
                    # Yes already notified so just return.
                    logger.debug('CHANNEL RES_USER ALREADY NOTIFIED')
                    return
                # Store notification status in cache
                self.env['kv_cache.cache'].put(
                    message, '1', tag=tag, expire=60)
                # Send notification message
                self.env['res.users'].asterisk_notify(
                    message=_(message), uid=res_user.id, sticky=is_sticky)
                logger.debug('CHANNEL RES_USER NOTIFIED')
