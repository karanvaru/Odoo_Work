# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models
from odoo.osv.expression import OR


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _compute_duplicates_count(self):
        """
        Compute method for duplicates_count

        Methods:
         * _construct_domain
         * search_count
        """
        company_id = self.env.user.company_id.sudo()
        only_companies = company_id.search_duplicates_for_companies_only
        extra_domain = only_companies and [('parent_id', '=', False)] or []
        fields = company_id.duplicate_fields_partner_soft
        for record in self:
            if only_companies and record.parent_id:
                continue
            else:
                domain = record._construct_domain(fields=fields, char_operator="ilike", extra_domain=extra_domain)
                if domain:
                    record.duplicates_count = self.search_count(domain)

    @api.model
    def search_duplicates_count(self, operator, value):
        """
        Search method for duplicates_count
        Introduced since the field is not stored
        """
        partners = self.search([])
        potential_dupplicates = []
        for partner in partners:
            if partner.duplicates_count > 0:
                potential_dupplicates.append(partner.id)
        return [('id', 'in', potential_dupplicates)]

    duplicates_count = fields.Integer(
        string='Duplicates Count',
        compute=_compute_duplicates_count,
        search='search_duplicates_count',
    )

    @api.model
    def create(self, values):
        """
        Overwrite to force 'write' in 'create'
        """
        partner_id = super(res_partner, self).create(values)
        partner_id.write({})
        return partner_id

    @api.multi
    def write(self, vals):
        """
        Overwrite to check for rigid duplicates and raise UserError in such a case

        Methods:
         * _return_duplicated_records

        Raises:
         * UserError if duplicates have been found
        """
        for record in self:
            partner_id = super(res_partner, record).write(vals)
            duplicate_partners = record._return_duplicated_records(fields_names="duplicate_fields_partner")
            if len(duplicate_partners) == 0:
                continue
            else:
                duplicate_partners_recordset = self.browse(duplicate_partners)
                warning = _('Duplicates were found: \n')
                for duplicate in duplicate_partners_recordset:
                    fields = self.env.user.company_id.sudo().duplicate_fields_partner
                    duplicated_fields = "; ".join(["{} - {}".format(field.name, record[field.name])
                                        for field in fields if record[field.name]
                                        and record[field.name] == duplicate[field.name]])
                    warning += '"[ID {}] {} {} {} \n'.format(
                        duplicate.id,
                        duplicate.name,
                        _(' by fields: '),
                        duplicated_fields
                    )
                raise exceptions.UserError(warning)
        return True

    @api.multi
    def _construct_domain(self, fields, char_operator='=', extra_domain=[]):
        """
        The method to construct domain for a given record by given fields

        Args:
         * fields - ir.model.fields recordset
         * char_operator - whether to use 'ilike' or '=' operator for char fields
         * extra_domain - whether domain needs extra leaves

        Returns:
         * list of leaves (reverse polish notation) or False

        Extra info:
         * we do not check field type for relations and so on, since we rely upon xml fields domain
         * expected singleton
        """
        self.ensure_one()
        domain = False
        fields_domain = []
        for field in fields:
            if self[field.name]:
                if field.ttype == 'many2one':
                    fields_domain = OR([fields_domain, [(field.name, 'in', self[field.name].ids)]])
                elif field.ttype == 'char':
                    fields_domain = OR([fields_domain, [(field.name, char_operator, self[field.name])]])
                else:
                    fields_domain = OR([fields_domain, [(field.name, '=', self[field.name])]])
        if fields_domain:
            domain = fields_domain + extra_domain + [('id', '!=', self.id)] \
                     + ["|", ("company_id", "=", False), ('company_id', '=', self.company_id.id)]
        return domain

    @api.multi
    def _return_duplicated_records(self, fields_names, char_operator="="):
        """
        The method to find duplciated records by domain

        Args:
         * fields_names - name of settings fields (criteria to search duplicates)
         * char_operator - whether to use 'ilike' or '=' operator for char fields

        Methods:
         * _construct_domain
         * _search

        Returns:
         * list of ids

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        company_id = self.env.user.company_id.sudo()
        only_companies = company_id.search_duplicates_for_companies_only
        records = []
        if not (only_companies and self.parent_id):
            extra_domain = only_companies and [('parent_id', '=', False)] or []
            fields = company_id[fields_names]
            domain = self._construct_domain(fields=fields, char_operator=char_operator, extra_domain=extra_domain)
            if domain:
                records = self._search(domain)
        return records

    @api.multi
    def open_duplicates(self):
        """
        The method to open tree of potential duplicates

        Methods:
         * _return_duplicated_records

        Extra info:
         * Expected singleton

        Returns:
         * action to open partners duplicates list
        """
        self.ensure_one()
        duplicates = self._return_duplicated_records(
            fields_names="duplicate_fields_partner_soft",
            char_operator="ilike"
        )
        return {
            'name': 'Duplicates',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'res.partner',
            'domain': [('id', 'in', duplicates + self.ids)],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
