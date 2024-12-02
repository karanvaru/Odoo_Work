import json
import logging
from odoo import models, fields, api, _

logger = logging.getLogger(__name__)


class CrmChannel(models.Model):
    _name = 'asterisk_calls.channel'
    _inherit = 'asterisk_calls.channel'

    lead = fields.Many2one('crm.lead', ondelete='set null',
                           string=_('CRM'))

    @api.model
    def update_channel_values(self, original_vals):
        vals = super(CrmChannel, self).update_channel_values(original_vals)
        src = original_vals['callerid_num']
        exten = original_vals['exten']
        connected_line_num = original_vals['connected_line_num']
        # Check if it is orginated call
        originate_data = self.env['kv_cache.cache'].get(
            original_vals.get('uniqueid'), tag='originated_call',
            serialize='json')
        if not originate_data:
            originate_data = self.env['kv_cache.cache'].get(
                original_vals.get('linkedid'), tag='originated_call',
                serialize='json')
            if originate_data:
                logger.debug('FOUND LEAD ORIGINATED CALL DATA FROM LINKEDID.')
        model = originate_data.get('model')
        res_id = originate_data.get('res_id')
        lead = None
        if model == 'crm.lead' and res_id:
            logger.debug('FOUND LEAD FROM ORIGINATED CALL DATA.')
            vals.update({'lead': res_id})
            lead = self.env['crm.lead'].browse(res_id)
        else:
            logger.debug('LEAD NOT FOUND BY ORIGINATED CALL DATA')
            lead = self.env['crm.lead'].get_lead_by_number(src)
            if lead:
                logger.debug('LEAD FOUND BY SRC %s', src)
            else:
                logger.debug('LEAD NOT FOUND BY SRC %s', src)
                lead = self.env['crm.lead'].get_lead_by_number(
                    connected_line_num)
                if lead:
                    logger.debug(
                        'LEAD FOUND BY CONNECTED LINE NUM %s',
                        connected_line_num)
                else:
                    logger.debug(
                        'LEAD NOT FOUND BY CONNECTED LINE NUM %s',
                        connected_line_num)
                    lead = self.env['crm.lead'].get_lead_by_number(exten)
                    if lead:
                        logger.debug('LEAD FOUND BY EXTEN %s', exten)
                    else:
                        logger.debug('LEAD NOT FOUND BY EXTEN %s', exten)
            if lead:
                vals.update({'lead': lead.id})
                logger.debug('FOUND LEAD %s', lead.id)
            else:
                if original_vals.get(
                        'uniqueid') != original_vals.get('linkedid'):
                    channel = self.env['asterisk_calls.channel'].search(
                        [('uniqueid', '=', original_vals.get('linkedid'))])
                    if channel and channel.lead:
                        # Copy lead from linked channel
                        vals.update({'lead': channel.lead.id})
                # Try to get lead from linked channel
        # Set lead's partner if not partner is set.
        if lead and not vals.get('partner'):
            vals['partner'] = lead.partner_id.id        
        return vals

    def reload_channels(self):
        self.ensure_one()
        # Add lead and view ids to the message
        auto_reload = self.env[
            'asterisk_common.settings'].get_param('auto_reload_channels')
        #view_id = self.env['ir.model.data'].sudo(True).xmlid_to_res_id(
        #    'crm.crm_lead_view_form')
        # Correct form seem to open without lead view id.
        view_id = False
        self.env['bus.bus'].sendone('asterisk_calls_channels', json.dumps({
                                    'event': 'update_channel',
                                    'dst': self.exten,
                                    'system_name': self.system_name,
                                    'channel': self.channel_short,
                                    'partner_id': self.partner.id,
                                    'auto_reload': auto_reload,
                                    'lead_id': self.lead.id,
                                    'view_id': view_id}))

    def open_opportunity(self):
        self.ensure_one()
        return {
            'res_model': 'crm.lead',
            'res_id': self.lead.id,
            'name': _('Create Opportunity'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env['ir.model.data'].xmlid_to_res_id(
                'crm.crm_lead_view_form'),
        }
