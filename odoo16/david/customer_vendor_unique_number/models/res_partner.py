# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'

    customer_vendor_number_custom = fields.Char(
        string='Number',
        readonly=True,
        copy=False,
    )
  
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('company_type') == 'company':
                vals['customer_vendor_number_custom'] = self.env['ir.sequence'].next_by_code('customer.vendor.company.custom') or _('New')
            elif vals.get('company_type') == 'person' and vals.get('parent_id'):
                parent_id = vals.get('parent_id')
                brw_parent = self.browse(parent_id)
                if brw_parent.customer_vendor_number_custom: #change 03/07/2020
                    number_custom = brw_parent.customer_vendor_number_custom +' - CONTACT/'
                    vals['customer_vendor_number_custom'] = number_custom + str(len(brw_parent.child_ids.ids) + 1)
            elif vals.get('company_type') == 'person' and not vals.get('parent_id'):
                vals['customer_vendor_number_custom'] = self.env['ir.sequence'].next_by_code('customer.vendor.individual.custom') or _('New')
        return super(Partner, self).create(vals_list)

    def write(self, vals):
        if vals.get('parent_id'):
            parent_id = vals.get('parent_id')
            brw_parent = self.browse(parent_id)
            number_custom = str(brw_parent.customer_vendor_number_custom) +' - CONTACT/'
            if not brw_parent.child_ids:
                vals['customer_vendor_number_custom'] = number_custom + str(len(brw_parent.child_ids.ids))
            else:
                vals['customer_vendor_number_custom'] = number_custom + str(len(brw_parent.child_ids.ids) + 1)
        elif vals.get('company_type') == 'company':
            vals['customer_vendor_number_custom'] = self.env['ir.sequence'].next_by_code('customer.vendor.company.custom') or _('New')
        elif vals.get('company_type') == 'person' or 'parent_id' in vals and not vals.get('parent_id'):
            vals['customer_vendor_number_custom'] = self.env['ir.sequence'].next_by_code('customer.vendor.individual.custom') or _('New')
        return super(Partner, self).write(vals)


   