from odoo import api, fields, models, _
import re


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''
        if partner.customer_vendor_number_custom:
            name = partner.name + '[' + partner.customer_vendor_number_custom + ']' or ''

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                types = dict(self._fields['type']._description_selection(self.env))
                name = types[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = re.sub(r'\s+\n', '\n', name)
        if self._context.get('partner_show_db_id'):
            name = "%s (%s)" % (name, partner.id)
        if self._context.get('address_inline'):
            splitted_names = name.split("\n")
            name = ", ".join([n for n in splitted_names if n.strip()])
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name.strip()

    # def name_get(self):
    #     result = []
    #     for partner in self:
    #         name = partner._get_name()
    #         # res.append((partner.id, name))
    #         if partner.customer_vendor_number_custom:
    #             name = partner.name + '[' + partner.customer_vendor_number_custom + ']' + partner._get_name()
    #         result.append((partner.id, name))
    #     return result

    def set_number_contact(self):
        for rec in self:
            country_code = rec.country_id.code
            if not rec.customer_vendor_number_custom:
                if rec.company_type == 'company':
                    # if country_code:
                    #     rec.customer_vendor_number_custom = country_code + ' - ' + self.env['ir.sequence'].next_by_code(
                    #         'customer.vendor.company.custom') or _('New')
                    # else:
                        rec.customer_vendor_number_custom = self.env['ir.sequence'].next_by_code(
                            'customer.vendor.company.custom') or _('New')

                elif rec.company_type == 'person' and rec.parent_id:
                    parent_id = rec.parent_id
                    # brw_parent = rec.browse(parent_id)
                    if parent_id.customer_vendor_number_custom:
                        number_custom = parent_id.customer_vendor_number_custom + ' - CONTACT/'
                        # if country_code:
                        #     rec.customer_vendor_number_custom = country_code + ' - ' + number_custom + str(
                        #         len(parent_id.child_ids.ids) + 1)
                        # else:
                        rec.customer_vendor_number_custom = number_custom + str(
                            len(parent_id.child_ids.ids) + 1)
                elif rec.company_type == 'person' and not rec.parent_id:
                    # if country_code:
                    #     rec.customer_vendor_number_custom = country_code + ' - ' + self.env['ir.sequence'].next_by_code(
                    #         'customer.vendor.individual.custom') or _('New')
                    # else:
                        rec.customer_vendor_number_custom = self.env['ir.sequence'].next_by_code(
                            'customer.vendor.individual.custom') or _('New')

    def set_country_code_contact(self):
        for rec in self:
            if rec.customer_vendor_number_custom:
                if rec.country_id.code:
                    country_code = rec.country_id.code
                    if rec.company_type == 'company':
                        rec.customer_vendor_number_custom = country_code + ' -' + rec.customer_vendor_number_custom
                    elif rec.company_type == 'person' and rec.parent_id:
                        parent_id = rec.parent_id
                        if parent_id.customer_vendor_number_custom:
                            number_custom = parent_id.customer_vendor_number_custom + ' - CONTACT/'
                            rec.customer_vendor_number_custom = country_code + ' -' + number_custom + rec.customer_vendor_number_custom
                    elif rec.company_type == 'person' and not rec.parent_id:
                        rec.customer_vendor_number_custom = country_code + ' - ' + rec.customer_vendor_number_custom

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        country_code = res.country_id.code
        if country_code:
            res.update({
                'customer_vendor_number_custom': country_code + ' - ' + res.customer_vendor_number_custom
            })

        return res
