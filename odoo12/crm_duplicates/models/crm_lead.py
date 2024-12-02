# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models
from odoo.osv.expression import OR


class crm_lead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    def _compute_duplicates_count(self):
        """
        Compute method for duplicates_count

        Methods:
         * _construct_domain
         * search_count
        """
        company_id = self.env.user.company_id.sudo()
        fields = company_id.duplicate_fields_lead_soft
        for record in self:
            domain = record._construct_domain(fields=fields, char_operator="ilike")
            if domain:
                record.duplicates_count = self.search_count(domain)

    @api.model
    def search_duplicates_count(self, operator, value):
        """
        Search method for duplicates_count
        Introduced since the field is not stored
        """
        leads = self.search([])
        potential_dupplicates = []
        for lead in leads:
            if lead.duplicates_count > 0:
                potential_dupplicates.append(lead.id)
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
        lead_id = super(crm_lead, self).create(values)
        lead_id.write({})
        return lead_id

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
            lead_id = super(crm_lead, record).write(vals)
            duplicate_leads = record._return_duplicated_records(fields_names="duplicate_fields_lead")
            if len(duplicate_leads) == 0:
                continue
            else:
                duplicate_leads_recordset = self.browse(duplicate_leads)
                warning = _('Duplicates were found: \n')
                for duplicate in duplicate_leads_recordset:
                    fields = self.env.user.company_id.sudo().duplicate_fields_lead
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
    def _construct_domain(self, fields, char_operator='='):
        """
        The method to construct domain for a given record by given fields

        Args:
         * fields - ir.model.fields recordset
         * char_operator - whether to use 'ilike' or '=' operator for char fields

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
            domain = fields_domain + [('id', '!=', self.id)] \
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
        fields = company_id[fields_names]
        domain = self._construct_domain(fields=fields, char_operator=char_operator)
        records = []
        if domain:
            records = self._search(domain)
        return records

    @api.multi
    def merge_opportunity(self, user_id=False, team_id=False):
        """
        Overwrite to pass context and let merge duplicats
        """
        context = {
            'inhibit_duplication_warning': True,
        }
        return super(crm_lead, self.with_context(context)).merge_opportunity(user_id=user_id, team_id=team_id)

    @api.multi
    def open_duplicates(self):
        """
        The method to open tree of potential duplicates

        Methods:
         * _return_duplicated_records

        Extra info:
         * Expected singleton

        Returns:
         * action to open leads' duplicates list
        """
        self.ensure_one()
        duplicates = self._return_duplicated_records(
            fields_names="duplicate_fields_lead_soft",
            char_operator="ilike"
        )
        return {
                'name': 'Duplicates',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'crm.lead',
                'domain': str([('id', 'in', duplicates + self.ids)]),
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'context': {
                    'form_view_ref': 'crm_duplicates.crm_case_form_view_oppor',
                },
        }
