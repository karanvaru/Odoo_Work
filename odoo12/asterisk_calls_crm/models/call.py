import json
import logging
from odoo import models, fields, api, _

logger = logging.getLogger(__name__)


class CrmCall(models.Model):
    _name = 'asterisk_calls.call'
    _inherit = 'asterisk_calls.call'

    lead = fields.Many2one('crm.lead', ondelete='set null', string='CRM')

    @api.model
    def create(self, vals):
        call = super(CrmCall, self).create(vals)
        # Check if lead auto creation is set.
        logger.info('%s', vals)
        try:
            incoming_call = not bool(call.src_user)
            if not vals.get('lead'):
                if self.env['asterisk_common.settings'].get_param(
                        'auto_create_leads_from_calls') and incoming_call:
                    # Check for call state
                    only_missed = self.env[
                        'asterisk_common.settings'].get_param(
                        'auto_create_leads_missed_calls_only')
                    if only_missed and vals.get('disposition') == 'ANSWERED':
                        logger.debug('CALLS CRM ONLY MISSED MODE.')
                        return call
                    sales_person = self.env[
                        'asterisk_common.settings'].get_param(
                        'auto_create_leads_sales_person')
                    logger.debug(
                        'ASTERISK CALLS CRM CREATE LEAD FROM CALL')
                    lead = self.env['crm.lead'].create({
                        'name': vals.get('clid'),
                        'type': 'lead',
                        'phone': vals.get('src'),
                        'user_id': sales_person.id if sales_person else False})
                    call.write({'lead': lead.id})
        except Exception:
            logger.exception('CRM CREATE CALL ERROR')
        finally:
            return call

    @api.model
    def update_cdr_values(self, original_vals):
        vals = super(CrmCall, self).update_cdr_values(original_vals)
        dst = original_vals['dst']
        src = original_vals['src']
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
            logger.debug('FOUND LEAD %s FROM ORIGINATED CALL DATA.', res_id)
            vals.update({'lead': res_id})
            lead = self.env['crm.lead'].browse(res_id)
        # Search by numbers
        elif vals.get('src_user'):
            # For outgoing calls search dst
            lead = self.env['crm.lead'].get_lead_by_number(dst)
            if lead:
                logger.debug('LEAD FOUND BY DST %s', dst)
                vals.update({'lead': lead.id})
            else:
                logger.debug('LEAD NOT FOUND BY DST %s', dst)
        elif vals.get('dst_user'):
            # For incoming calls search src
            lead = self.env['crm.lead'].get_lead_by_number(src)
            if lead:
                logger.debug('LEAD FOUND BY SRC %s', src)
                vals.update({'lead': lead.id})
            else:
                logger.debug('LEAD NOT FOUND BY SRC %s', src)
        else:
            # If there is no dst or src users it can be incoming call to Queue.
            lead = self.env['crm.lead'].get_lead_by_number(src)
            if lead:
                logger.debug('LEAD FOUND BY SRC %s', src)
                vals.update({'lead': lead.id})
            else:
                logger.debug('LEAD NOT FOUND BY SRC %s', src)
        if lead:
            vals['partner'] = lead.partner_id and lead.partner_id.id
        return vals

    def create_opportunity(self):
        self.ensure_one()
        return {
            'res_model': 'crm.lead',
            'name': _('Create Opportunity'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env['ir.model.data'].xmlid_to_res_id(
                'crm.crm_case_form_view_oppor'),
            'context': {
                'default_phone': self.dst if self.src_user else self.src,
                'default_name': self.partner.name if self.partner else self.clid,
                'default_partner_id': self.partner.id if self.partner else False,
                'default_type': 'opportunity',
                'create_call_lead': self.id,
            },
        }
