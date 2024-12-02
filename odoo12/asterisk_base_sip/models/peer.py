# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import random
import re
import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from psycopg2 import OperationalError
try:
    import humanize
    HUMANIZE = True
except ImportError:
    HUMANIZE = False
from odoo.addons.asterisk_base.utils import remove_empty_lines
from odoo.addons.asterisk_base.utils import get_default_server


logger = logging.getLogger(__name__)

DEFAULT_SECRET_LENGTH = 10
PEER_TYPES = [
    ('user', 'User'),
    ('trunk', 'Trunk'),
]
CHANNEL_TYPES = [
    ('sip', 'SIP'),
    ('pjsip', 'PJSIP'),
]
YESNO_VALUES = [('yes', 'Yes'), ('no', 'No')]
RE_CALLERID = re.compile(r'^(.+) <([0-9]+)>$')


class SipPeer(models.Model):
    _name = 'asterisk_base_sip.peer'
    _description = 'Asterisk SIP Peer'
    _order = 'name'

    server = fields.Many2one(comodel_name='asterisk_base.server',
                             required=True,
                             default=get_default_server)
    template = fields.Many2one(comodel_name='asterisk_base_sip.peer_template',
                               ondelete='set null')
                               # TODO:
                               #ondelete='restrict')
    extension = fields.Many2one('asterisk_base.extension')
    extension_name = fields.Char(compute='_get_extension_name')
    exten = fields.Char(related='extension.number', string='Service Extension',
                        readonly=False, store=True)
    user = fields.Many2one('asterisk_common.user')
    route_groups = fields.Many2many(
        'asterisk_base_sip.route_group',
        relation='asterisk_base_sip_peer_route_groups')
    user_route_groups = fields.Many2many(
        related='user.route_groups', readonly=True)
    list_route_groups = fields.Many2many(
        'asterisk_base_sip.route_group', store=True,
        compute='_get_list_route_groups')
    name = fields.Char(required=True, string='SIP Name')
    note = fields.Char()
    channel_type = fields.Selection(
        CHANNEL_TYPES, required=True,
        default=lambda x: x._get_default_channel_type())
    channel_name = fields.Char(
        string='Channel', compute='_get_channel_name', store=True)
    peer_type = fields.Selection(
        string='Type', selection=PEER_TYPES, index=True)
    peer_statuses = fields.One2many(
        comodel_name='asterisk_base_sip.peer_status', inverse_name='peer')
    peer_status_count = fields.Integer(
        compute='_get_peer_status_count', string='Events')
    only_changed = fields.Boolean(default=True,
                                  string="Show Only Changed Settings")
    # Asterisk fields
    accountcode = fields.Char(compute='_get_accountcode')
    amaflags = fields.Char(size=40)
    callgroup = fields.Char(size=40)
    callerid = fields.Char(size=80, string='Caller ID')
    # By default it is yes so we have a default no
    canreinvite = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   size=3, string='Can reinvite', default='no')
    #context_id = fields.Many2one('asterisk.conf.extensions', ondelete='restrict')
    context = fields.Char(index=True, size=40)
    defaultip = fields.Char(size=15, string='Default IP')
    dtmfmode = fields.Selection(
        size=10, string='DTMF mode',
        selection=[('auto', 'Auto'),
                   ('inband', 'Inband'),
                   ('rfc2833', 'RFC2833'),
                   ('info', 'Info'),
                   ('shortinfo', 'Short Info')])
    fromuser = fields.Char(size=80, string='From user')
    fromdomain = fields.Char(size=80, string='From domain')
    host = fields.Char(size=40)
    outboundproxy = fields.Char(size=80)
    insecure = fields.Selection(selection=[(x,x) for x in ('port', 'invite', 'port,invite')],
        help="""Port - Allow matching of peer by IP address without matching port number.
        Invite - Do not require authentication of incoming INVITEs.
        Port,Invite - Both (Not so rarely enabled for Trunks).""")
    language = fields.Char(size=2)
    mailbox = fields.Char(size=50)
    md5secret = fields.Char(size=80)
    nat = fields.Selection(
        selection=[('no', 'No'), ('force_rport', 'Force rport'),
                   ('comedia', 'Comedia'),
                   ('auto_force_rport', 'Auto force rport'),
                   ('auto_comedia', 'Auto comedia'),
                   ('force_rport,comedia', 'Force rport, comedia')],
        size=64, string='NAT')
    permit = fields.Char(size=95, default='0.0.0.0/0.0.0.0', required=True)
    deny = fields.Char(size=95, default='0.0.0.0/0.0.0.0', required=True)
    mask = fields.Char(size=95)
    pickupgroup = fields.Char(size=10)
    port = fields.Char()
    qualify = fields.Char(size=5)
    srvlookup = fields.Selection(YESNO_VALUES, string='SRV Lookup')
    restrictcid = fields.Char(size=1)
    rtptimeout = fields.Char(string='RTP timeout')
    rtpholdtimeout = fields.Char(string='RTP hold timeout')
    secret = fields.Char(size=80, default=lambda x: x.generate_secret(),
                         string='SIP Secret',
                         groups="asterisk_common.group_asterisk_admin")
    remotesecret = fields.Char(size=40, help='The password we use to '
        'authenticate to them. Specify only when different from Secret.')
    type = fields.Selection(selection=[('user', 'User'), ('peer', 'Peer'),
        ('friend', 'Friend')], required=True, default='friend')
    disallow = fields.Char(size=100, string="Disallow Codecs")
    allow = fields.Char(size=100, default='all', string="Allow Codecs")
    musiconhold = fields.Char(size=100, string='Music on hold')
    regcontext = fields.Char(size=80)
    cancallforward = fields.Char(size=3, default='yes')
    lastms = fields.Char()
    defaultuser = fields.Char(size=80, string='Default user')
    subscribecontext = fields.Char(size=80)
    regserver = fields.Char(size=80)
    callbackextension = fields.Char(size=250)
    transport = fields.Char()
    icesupport = fields.Selection(YESNO_VALUES)
    avpf = fields.Selection(YESNO_VALUES)
    force_avp = fields.Selection(YESNO_VALUES)
    dtlscipher = fields.Char()
    dtlsenable = fields.Selection(YESNO_VALUES)
    dtlsautogeneratecert = fields.Selection(YESNO_VALUES)
    dtlsverify = fields.Selection([
        ('yes', 'Yes'), ('no', 'No'),
        ('fingerprint', 'Fingerprint'), ('certificate', 'Certificate')])
    dtlscertfile = fields.Char()
    dtlsfingerprint = fields.Selection([('sha-1', 'sha-1'), ('sha-256', 'sha-256')])
    dtlscafile = fields.Char()
    dtlssetup = fields.Char()
    rtcp_mux = fields.Selection(YESNO_VALUES)
    directmedia = fields.Selection(selection=[(x,x) for x in
        ('yes', 'no', 'nonat', 'update')])
    trustrpid = fields.Selection(selection=YESNO_VALUES,
        help="If Remote-Party-ID should be trusted")
    progressinband = fields.Selection(selection=[
        ('yes', 'Yes'),
        ('no', 'No'),
        ('never', 'Never')], help="If we should generate in-band ringing")
    promiscredir = fields.Selection(selection=YESNO_VALUES,
        help="If yes, allows 302 or REDIR to non-local SIP address")
    setvar = fields.Char(size=200,
        help="Channel variable to be set for all calls from or to this device")
    callcounter = fields.Selection(selection=YESNO_VALUES,
        help="Enable call counters on devices. Can be set for all in [general] section")
    busylevel = fields.Char(help="""If you set the busylevel,
        we will indicate busy when we have a number of calls that matches the busylevel threshold.""")
    allowoverlap = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No'), ('dtmf', 'DTMF')],
        help="RFC3578 overlap dialing support. (Default is yes)")
    allowsubscribe = fields.Selection(selection=YESNO_VALUES,
        help="Support for subscriptions. (Default is yes)")
    videosupport = fields.Selection(selection=YESNO_VALUES,
        help="""Support for SIP video.
        You MUST enable it in [general] section to turn this on per user.""")
    maxcallbitrate = fields.Char(help="Maximum bitrate for video calls (default 384 kb/s)")
    rfc2833compensate = fields.Selection(selection=YESNO_VALUES,
        help="""Compensate for pre-1.4 DTMF transmission from another Asterisk machine.
        You must have this turned on or DTMF reception will work improperly.""")
    session_timers = fields.Selection(selection=[(x,x) for x in ('originate', 'accept', 'refuse')],
        help="""Session-Timers feature operates in the following three modes:
        originate : Request and run session-timers always
        accept    : Run session-timers only when requested by other UA
        refuse    : Do not run session timers in any case
        The default mode of operation is 'accept'.""")
    t38pt_usertpsource = fields.Char(size=40,
        help="""Use the source IP address of RTP as the destination IP address for UDPTL packets
        if the nat option is enabled. If a single RTP packet is received Asterisk will know the
        external IP address of the remote device. If port forwarding is done at the client side
        then UDPTL will flow to the remote device.""")
    regexten = fields.Char(size=40,
        help = """When device registers, create this extension in context set with 'regcontext' general option
        By default peer's name is used""")
    sendrpid = fields.Selection(selection=YESNO_VALUES)
    timert1 = fields.Char(help="""SIP T1 timer. Defaults to 500 ms
        or the measured round-trip time to a peer (qualify=yes).""")
    timerb = fields.Char(
        help = """Call setup timer. If a provisional response is not received
        in this amount of time, the call will autocongest
        Defaults to 64*timert1""")
    qualifyfreq = fields.Char(
        help = """How often to check for the host to be up in seconds.
        Set to low value if you use low timeout for NAT of UDP sessions.
        Default: 60""")
    contactpermit = fields.Char(size=95, help = "IP address filters for registrations")
    contactdeny = fields.Char(size=95, help = "IP address filters for registrations")
    contactacl = fields.Char(size=95, help = "IP address filters for registrations")
    usereqphone = fields.Selection(selection=YESNO_VALUES,
        help="If yes, ';user=phone' is added to uri that contains a valid phone number")
    textsupport = fields.Selection(selection=YESNO_VALUES,
        help="Support for ITU-T T.140 realtime text. The default value is 'no'.")
    faxdetect = fields.Selection(selection=YESNO_VALUES)
    buggymwi = fields.Selection(selection=YESNO_VALUES)
    callingpres = fields.Selection(selection=[(x, x) for x in
                ('allowed_not_screened', 'allowed_passed_screen',
                 'allowed_failed_screen', 'allowed',
                 'prohib_not_screened', 'prohib_passed_screen',
                 'prohib_failed_screen', 'prohib')])
    mohinterpret = fields.Char(size=40)
    mohsuggest = fields.Char(size=40)
    parkinglot = fields.Char(size=40,
                             help='Sets the default parking lot for call '
                                  'parking. Parkinglots are configured '
                                  'in features.conf')
    subscribemwi = fields.Selection(selection=YESNO_VALUES,
                                    help='Only send notifications if this '
                                         'phone subscribes for mailbox '
                                         'notification')
    vmexten = fields.Char(size=40,
                          help='dialplan extension to reach mailbox sets the '
                               'Message-Account in the MWI notify message '
                               'defaults to global vmexten which defaults '
                               'to "asterisk')
    autoframing = fields.Selection(YESNO_VALUES,
        help = """Set packetization based on the remote endpoint's (ptime) preferences.
        Defaults to no.""")
    rtpkeepalive = fields.Char(help="""Integer. Send keepalives in the RTP stream to keep NAT open.
        Default is off - zero.""")
    g726nonstandard = fields.Selection(selection=YESNO_VALUES,
        help = """If the peer negotiates G726-32 audio, use AAL2 packing
        order instead of RFC3551 packing order (this is required
        for Sipura and Grandstream ATAs, among others). This is
        contrary to the RFC3551 specification, the peer _should_
        be negotiating AAL2-G726-32 instead :-(""")
    ignoresdpversion = fields.Selection(
        selection=YESNO_VALUES,
        help='By default, Asterisk will honor the session version '
        'number in SDP packets and will only modify the SDP '
        'session if the version number changes. This option will '
        'force asterisk to ignore the SDP session version number '
        'and treat all SDP data as new data.  This is required '
        'for devices that send us non standard SDP packets '
        '(observed with Microsoft OCS). By default this option is off.')
    allowtransfer = fields.Selection(
        selection=YESNO_VALUES,
        help = """Diable/Enable SIP transfers.
        The Dial() options 't' and 'T' are not related as to whether SIP transfers are allowed or not.""")
    supportpath = fields.Selection(selection=YESNO_VALUES,
        help = "This activates parsing and handling of Path header as defined in RFC 3327")
    ###########################################################################
    ########### PJSIP OPTIONS #################################################
    # Wizard options
    remote_hosts = fields.Char()
    outbound_proxy = fields.Char()
    accepts_auth = fields.Selection(YESNO_VALUES)
    accepts_registrations = fields.Selection(YESNO_VALUES)
    sends_auth = fields.Selection(YESNO_VALUES)
    sends_registrations = fields.Selection(YESNO_VALUES)
    sends_line_with_registrations = fields.Selection(YESNO_VALUES)
    has_phoneprov = fields.Selection(YESNO_VALUES)
    server_uri_pattern = fields.Char()
    client_uri_pattern = fields.Char()
    contact_pattern = fields.Char()
    has_hint = fields.Selection(YESNO_VALUES)
    hint_context = fields.Char()
    hint_exten = fields.Char()
    hint_application = fields.Char()
    # Auth
    inbound_auth_username = fields.Char(string='Username')
    inbound_auth_realm = fields.Char(string='Auth Realm')
    inbound_auth_password = fields.Char(string='Auth Password')
    inbound_auth_nonce_lifetime = fields.Char(stirng='Nonce Lifetype')
    inbound_auth_type = fields.Char(string='Auth Type')
    # Endpoint
    endpoint_allow = fields.Char(string='Allow')
    endpoint_callerid = fields.Char(string='Caller ID')
    endpoint_context = fields.Char(string='Context')
    endpoint_direct_media = fields.Char(string='Direct Media')
    endpoint_disable_direct_media_on_nat = fields.Char(
        string='Direct Media on NAT')
    endpoint_trust_id_inbound = fields.Char(string='Trust ID Inbound')
    endpoint_trust_id_outbound = fields.Char(string='Trust ID Outbound')
    endpoint_disallow = fields.Char(string='Disallow')
    endpoint_dtmf_mode = fields.Char(string='DTMF Mode')
    endpoint_use_avpf = fields.Char(string='Use AVPF')
    endpoint_send_diversion = fields.Char(string='Send Diversion')
    endpoint_language = fields.Char(string='Language')
    endpoint_dtls_auto_generate_cert = fields.Char(
        string='DTLS Auto Generate Cert')
    endpoint_allow_transfer = fields.Char(string='Allow Transfer')
    endpoint_send_pai = fields.Char(string='Send PAI')
    endpoint_rewrite_contact = fields.Char(string='Rewrite Contact')
    endpoint_send_rpid = fields.Char(string='Send RPID')
    endpoint_force_rport = fields.Char(string='Force RPORT')
    endpoint_ice_support = fields.Char(string='Ice Support')
    endpoint_device_state_busy_at = fields.Char(string='Device State Busy At')

    """
    endpoint_100rel
    endpoint_aggregate_mwi
    
    endpoint_allow_overlap
    endpoint_aors
    endpoint_auth
    
    endpoint_callerid_privacy
    endpoint_callerid_tag
    
    endpoint_direct_media_glare_mitigation
    endpoint_direct_media_method
    endpoint_trust_connected_line
    endpoint_connected_line_method
    endpoint_media_address
    endpoint_bind_rtp_to_media_address
    endpoint_identify_by
    endpoint_redirect_method
    endpoint_mailboxes
    endpoint_mwi_subscribe_replaces_unsolicited
    endpoint_voicemail_extension
    endpoint_outbound_auth
    endpoint_outbound_proxy
    
    endpoint_rtp_ipv6
    endpoint_rtp_symmetric
    
    
    
    endpoint_rpid_immediate
    endpoint_timers_min_se
    endpoint_timers
    endpoint_timers_sess_expires
    endpoint_transport
    endpoint_type
    endpoint_use_ptime
    
    endpoint_force_avp
    endpoint_media_use_received_transport
    endpoint_media_encryption
    endpoint_media_encryption_optimistic
    endpoint_g726_non_standard
    endpoint_inband_progress
    endpoint_call_group
    endpoint_pickup_group
    endpoint_named_call_group
    endpoint_named_pickup_group    
    endpoint_t38_udptl
    endpoint_t38_udptl_ec
    endpoint_t38_udptl_maxdatagram
    endpoint_fax_detect
    endpoint_fax_detect_timeout
    endpoint_t38_udptl_nat
    endpoint_t38_udptl_ipv6
    endpoint_tone_zone
    
    endpoint_one_touch_recording
    endpoint_record_on_feature
    endpoint_record_off_feature
    endpoint_rtp_engine
    
    endpoint_user_eq_phone
    endpoint_moh_passthrough
    endpoint_sdp_owner
    endpoint_sdp_session
    endpoint_tos_audio
    endpoint_tos_video
    endpoint_cos_audio
    endpoint_cos_video
    endpoint_allow_subscribe
    endpoint_sub_min_expiry
    endpoint_from_user
    endpoint_mwi_from_user
    endpoint_from_domain
    endpoint_dtls_verify
    endpoint_dtls_rekey
    
    endpoint_dtls_cert_file
    endpoint_dtls_private_key
    endpoint_dtls_cipher
    endpoint_dtls_ca_file
    endpoint_dtls_ca_path
    endpoint_dtls_setup
    endpoint_dtls_fingerprint
    endpoint_srtp_tag_32
    endpoint_set_var
    endpoint_message_context
    endpoint_accountcode
    endpoint_preferred_codec_only
    endpoint_rtp_keepalive
    endpoint_rtp_timeout
    endpoint_rtp_timeout_hold
    endpoint_acl
    endpoint_deny
    endpoint_permit
    endpoint_contact_acl
    endpoint_contact_deny
    endpoint_contact_permit
    endpoint_subscribe_context
    endpoint_contact_user
    endpoint_asymmetric_rtp_codec
    endpoint_rtcp_mux
    endpoint_refer_blind_progress
    endpoint_notify_early_inuse_ringing
    endpoint_max_audio_streams
    endpoint_max_video_streams
    endpoint_bundle
    endpoint_webrtc
    endpoint_incoming_mwi_mailbox
    endpoint_follow_early_media_fork
    endpoint_accept_multiple_sdp_answers
    endpoint_suppress_q850_reason_headers
    endpoint_ignore_183_without_sdp
    """

    #######################################################################
    # Status fields
    status = fields.Char(size=32)
    useragent = fields.Char(size=255, string='User agent')
    ipaddr = fields.Char(size=45, string='IP address')
    regport = fields.Char(string="Port")
    fullcontact = fields.Char(size=80, string='Full contact')
    regexpire = fields.Char(size=32)
    session_expire = fields.Char(size=32)
    last_registration = fields.Char(compute='_get_last_registration')

    # Override default copy method, solve peer name problem
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of peer {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of peer {}".format(self.name)
        else:
            new_name = u"Copy of peer {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(SipPeer, self).copy(default)

    _sql_constraints = [
        ('peer_uniq', 'UNIQUE(name,server,channel_type)',
            _('Peer name of this type is already define at this server!'))
    ]

    @api.model
    def create(self, vals):
        res = super(SipPeer, self).create(vals)
        if not res.context:
            res.context = 'sip-peer-{}'.format(res.id)
        # Check if we have a peer with service extension
        if res.exten:
            self.env['asterisk_base.extension'].create_extension_for_obj(
                res, exten_type='service')
        # Check if we have user
        if res.user:
            # Create a peer for user
            res.create_user_channel()
        if not self.env.context.get('no_build_conf'):
            self.build_conf()
        return res

    def create_user_channel(self):
        self.ensure_one()
        self.env['asterisk_common.user_channel'].with_context(
            from_peer=True).create({
                'asterisk_user': self.user.id,
                'sip_peer': self.id,
                'channel': self.channel_name,
            })
        if not self.env.context.get('no_build_conf'):
            self.env['asterisk_common.user'].build_conf()

    def unlink_user_channel(self):
        self.ensure_one()
        self.env['asterisk_common.user_channel'].with_context(
            from_peer=True).search(
                [('channel', '=', self.channel_name)]).unlink()
        if not self.env.context.get('no_build_conf'):
            self.env['asterisk_common.user'].build_conf()

    def write(self, vals):
        # Check to unlink user channel
        if 'user' in vals:
            # Remove channel and re-create it below
            for rec in self:
                if rec.user is not False:
                    rec.unlink_user_channel()
        if 'exten' in vals:
            for rec in self:
                if rec.extension is not False:
                    rec.extension.unlink()
        if 'name' in vals:
            # Reset registration values as Aserisk will not be able to update it.
            vals['status'] = False
            vals['useragent'] = False
            vals['fullcontact'] = False
            vals['regexpire'] = False
            vals['session_expire'] = False
            vals['ipaddr'] = False
            vals['regport'] = False
        # Call super
        res = super(SipPeer, self).write(vals)
        if 'context' in vals and not vals['context']:
            # Reset peer's context to routes
            for rec in self:
                rec.context = 'sip-peer-{}'.format(rec.id)
        # Now check to create user channel.
        if 'user' in vals:
            for rec in self:
                if rec.user:
                    rec.create_user_channel()
        if 'exten' in vals:
            for rec in self:
                if rec.exten:
                    model = self.env['asterisk_base.extension']
                    model.create_extension_for_obj(rec, exten_type='service')
        # Build conf.
        if not self.env.context.get('no_build_conf'):
            self.build_conf()
        return res

    def unlink(self):
        for rec in self:
            # Check if we have a user channel and remove it.
            if rec.user:
                rec.unlink_user_channel()
            if rec.extension:
                rec.extension.unlink()
        res = super(SipPeer, self).unlink()
        if res:
            self.build_conf()
        return res

    def _get_accountcode(self):
        for rec in self:
            # Set accountcode
            if rec.user:
                rec.accountcode = 'user-{}'.format(rec.user.id)
            else:
                rec.accountcode = 'channel-{}'.format(rec.id)

    def _get_extension_name(self):
        for rec in self:
            rec.extension_name = rec.channel_name

    @api.constrains('name')
    def _check_name(self):
        allowed_chars = string.ascii_letters + string.digits + '_-'
        for l in self.name:
            if l not in allowed_chars:
                raise ValidationError(_('Peer name must be only letters, '
                                        'digits, - or _'))

    @api.depends('name', 'channel_type')
    def _get_channel_name(self):
        for rec in self:
            rec.channel_name = '{}/{}'.format(rec.channel_type.upper(),
                                              rec.name)

    def _get_default_channel_type(self):
        if self.env.context.get('install_mode') or self.env.context.get(
                'module') == 'asterisk_base_sip':
            return 'sip'
        return self.env['asterisk_common.settings'].get_param(
            'default_sip_channel_type')

    @api.depends('peer_statuses')
    def _get_peer_status_count(self):
        for rec in self:
            rec.peer_status_count = self.env[
                'asterisk_base_sip.peer_status'].search_count([
                ('peer', '=', rec.id)])

    @api.onchange('server')
    def _reset_server_route_groups(self):
        if not self.server:
            self.route_groups = False
        else:
            is_type_default = 'is_{}_default'.format(self.peer_type)
            if not self.route_groups or self._origin.server != self.server:
                groups = self.env['asterisk_base_sip.route_group'].search(
                    [('server', '=', self.server.id),
                     (is_type_default, '=', True)])
                self.route_groups = groups
            return {'domain': {
                'route_groups': [('server', '=', self.server.id)]}}

    @api.onchange('user', 'exten')
    def set_callerid(self):
        rec = self
        # Set callerid when creating peers
        if rec.user and not rec.write_date:
            rec.callerid = '{} <{}>'.format(
                rec.user.name or '', rec.user.exten)

    @api.onchange('channel_type')
    def _onchange_channel_type(self):
        return {'domain': {
            'template': [('channel_type', '=', self.channel_type),
                         ('peer_type', '=', self.peer_type)]}}

    @api.onchange('template')
    def _onchange_template(self):
        if self.template:
            for rec in self.template.individual_options:
                if not getattr(self, rec.param, False):
                    setattr(self, rec.param, rec.value)

    def generate_secret(self, length=DEFAULT_SECRET_LENGTH):
        if self.env.context.get('default_peer_type') == 'trunk':
            return ''
        chars = string.ascii_letters + string.digits
        password = ''
        while True:
            password = ''.join(map(lambda x: random.choice(chars), range(length)))
            if filter(lambda c: c.isdigit(), password) and \
                    filter(lambda c: c.isalpha(), password):
                break
        return password

    def build_extension(self):
        # Render extension from template
        self.ensure_one()
        return self.env['ir.qweb'].with_context({'lang':'en_US'}).render(
            'asterisk_base_sip.extension', {'rec': self}).decode('utf-8')

    def build_conf(self):
        self.build_extensions_conf()
        self.build_sip_conf()
        self.build_pjsip_conf()

    def build_extensions_conf(self):
        conf_dict = {}
        for rec in self.search([], order='id'):
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = ''
            rendered = self.env['ir.qweb'].with_context(
                {'lang': 'en_US'}).render(
                    'asterisk_base_sip.peer_context', {'rec': rec})
            conf_dict[rec.server.id] += '{}'.format(
                rendered.decode('utf-8'))
        # Create conf files
        for server_id in conf_dict.keys():
            # First try to get existing conf
            conf = self.env['asterisk_base.conf'].get_or_create(
                server_id, 'extensions_odoo_sip_peer.conf')
            # Set conf content
            conf.content = '{}'.format(
                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')

    def build_sip_conf(self):
        # Build peers
        def build_peers_conf(records, conf_name):
            # Now create config data
            conf_dict = {}
            for rec in records:
                if not conf_dict.get(rec.server.id):
                    conf_dict[rec.server.id] = ''
                channel_vars = rec.setvar.split(';') if rec.setvar else []
                rendered = self.env['ir.qweb'].with_context(
                    {'lang': 'en_US'}).render(
                        'asterisk_base_sip.sip_peer', {
                            'rec': rec,
                            'channel_vars': channel_vars})
                conf_dict[rec.server.id] += '{}'.format(
                    rendered.decode('utf-8'))
            # Create conf files
            for server_id in conf_dict.keys():
                # First try to get existing conf
                conf = self.env['asterisk_base.conf'].get_or_create(
                    server_id, conf_name)
                # Set conf content
                conf.content = '{}'.format(
                    remove_empty_lines(conf_dict[server_id]))
                conf.include_from('sip.conf')
        # Clear conf files first (when we remove peers)
        for c in self.env['asterisk_base.conf'].search([
                ('name', 'in', [
                    'sip_odoo_user.conf', 'sip_odoo_trunk.conf'])]):
            c.with_context(conf_no_update=True).content = ''
        # Build conf for different PEER_TYPES
        for pt in PEER_TYPES:
            records = self.env['asterisk_base_sip.peer'].search([
                ('channel_type', '=', 'sip'), ('peer_type', '=', pt[0])])
            build_peers_conf(records, 'sip_odoo_{}.conf'.format(pt[0]))

    def build_pjsip_conf(self):
        # Clear conf files first (when we remove peers)
        for c in self.env['asterisk_base.conf'].search([
                ('name', '=', 'pjsip_wizard_odoo.conf')]):
            c.with_context(conf_no_update=True).content = ''
        conf_dict = {}
        records = self.env['asterisk_base_sip.peer'].search([
            ('channel_type', '=', 'pjsip')])
        for rec in records:
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = ''
            rendered = self.env['ir.qweb'].with_context({'lang':'en_US'}).render(
                'asterisk_base_sip.pjsip_peer', {
                    'rec': rec
                })
            conf_dict[rec.server.id] += '{}'.format(
                rendered.decode('utf-8'))
        # Create conf files
        for server_id in conf_dict.keys():
            # First try to get existing conf
            conf = self.env['asterisk_base.conf'].get_or_create(
                server_id, 'pjsip_wizard_odoo.conf')
            # Set conf content
            conf.content = '{}'.format(
                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('pjsip.conf')

    def reload(self):
        self.ensure_one()
        self.server.reload_action(module='chan_sip')

    def apply_button(self):
        self.ensure_one()
        self.sync()

    def apply(self):
        self.ensure_one()
        self.build_conf()
        self.server.apply_changes(notify_uid=self.env.user.id)

    def update_status_button(self):
        self.ensure_one()
        self.update_status_request(status_notify_uid=self.env.uid)

    def update_status_request(self, status_notify_uid=None):
        for rec in self:
            rec.server.agent.send({
                'command': 'nameko_rpc',
                'service': '{}_ami'.format(rec.server.system_name),
                'method': 'send_action',
                'args': ({'Action': 'SIPshowpeer', 'Peer': rec.name},),
                'callback_model': 'asterisk_base_sip.peer',
                'callback_method': 'update_status_response',
                'status_notify_uid': status_notify_uid,
                'pass_back': {
                    'res_id': rec.id, 'status_notify_uid': rec.env.uid},
            })

    @api.model
    def update_status_response(self, response):
        peer_id = response['pass_back']['res_id']
        get = response.get('result', {}).get
        try:
            peer = self.env['asterisk_base_sip.peer'].browse(peer_id)
            peer.with_context(no_build_conf=True).write({
                'status': get('Status'),
                'ipaddr': get('Address-IP'),
                'regport': get('Address-Port'),
                'fullcontact': get('Reg-Contact'),
                'useragent': get('SIP-Useragent'),
                'regexpire': get('RegExpire'),
                'session_expire': get('SIP-Sess-Expires'),
            })
        except OperationalError as e:
            if e.pgcode == '55P03':  # could not obtain the lock, forget.
                pass
            else:
                logger.exception('Could not browse peer %s', peer_id)
            return False
        finally:
            self.env['remote_agent.agent'].reload_view(
                uid=response.get('pass_back', {}).get('status_notify_uid'),
                model='asterisk_base_sip.peer')

    @api.depends('user', 'route_groups', 'user_route_groups')
    def _get_list_route_groups(self):
        for rec in self:
            rec.list_route_groups = rec.user_route_groups if rec.user \
                else rec.route_groups

    def _get_last_registration(self):
        for rec in self:
            # Get last registration
            status = self.env['asterisk_base_sip.peer_status'].search(
                [('peer', '=', rec.id)], limit=1, order='id desc')
            if not status:
                rec.last_registration = 'No registrations'
                continue
            try:
                if HUMANIZE:
                    to_translate = self.env.context.get('lang', 'en_US')
                    if to_translate != 'en_US':
                        humanize.i18n.activate(to_translate)
                    rec.last_registration = humanize.naturaltime(
                        fields.Datetime.from_string(status.create_date))
                else:
                    rec.last_registration = str(status.create_date).split('.')[0]
            except Exception:
                logger.exception('Translation error:')
                rec.last_registration = str(status.create_date)
