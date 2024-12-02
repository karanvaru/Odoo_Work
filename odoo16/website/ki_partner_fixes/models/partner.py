
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountMoveInherit(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        if 'city' in vals and vals['city']:
            city = self.env['res.city'].sudo().search([('name', 'ilike', vals['city'])], limit=1)
            if city:
              vals.update({'city_id': city.id})
              if city.state_id:
                  vals.update({'state_id': city.state_id.id})
            else:
                raise ValidationError(
                    _('Please enter valid city!')
                )
                
        return super(AccountMoveInherit, self).create(vals)

    def write(self, vals):
        if 'city' in vals and vals['city']:
            city = self.env['res.city'].sudo().search([('name', 'ilike', vals['city'])], limit=1)
            if city:
              vals.update({'city_id': city.id})
              if city.state_id:
                  vals.update({'state_id': city.state_id.id})
            else:
                raise ValidationError(
                    _('Please enter valid city!')
                )
        return super(AccountMoveInherit, self).write(vals)

    @api.constrains('mobile')
    def _check_mobile_uniq(self):
        for partner in self:
            if partner.mobile:
                exist_partner = self.search_count([('mobile', 'ilike',  partner.mobile)])
                if exist_partner > 1:
                    raise ValidationError(
                        _("Contact with same mobile number is exists in system"))
    
    @api.model_create_multi
    def create(self, vals_list):
        if not self._context.get('import_file', False):
            return super(AccountMoveInherit, self).create(vals_list)
        new_vals_list = []
        partners = self.browse()
        for val in vals_list:
            if val.get('mobile'):
                exist_partner = self.search([('mobile', 'ilike',  val['mobile'])], limit=1)
                if exist_partner:
                    exist_partner.update(val)
                    partners += exist_partner
                else:
                    new_vals_list.append(val)
            else:
                new_vals_list.append(val)
        if new_vals_list:
            return super(AccountMoveInherit, self).create(new_vals_list)
        else:
            return partners
