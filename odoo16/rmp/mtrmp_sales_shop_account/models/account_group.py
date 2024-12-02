# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Account(models.Model):
    _inherit = "account.account"

    group_id = fields.Many2one(readonly=False)


class AccountGroup(models.Model):
    _inherit = "account.group"

    parent_id = fields.Many2one(readonly=False)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


    def _adapt_parent_account_group(self):
        """Ensure consistency of the hierarchy of account groups.

        Find and set the most specific parent for each group.
        The most specific is the one with the longest prefixes and with the starting
        prefix being smaller than the child prefixes and the ending prefix being greater.
        """
        if not self:
            return
        self.env['account.group'].flush(self.env['account.group']._fields)
        query = """
            WITH relation AS (
       SELECT DISTINCT FIRST_VALUE(parent.id) OVER (PARTITION BY child.id ORDER BY child.id, char_length(parent.code_prefix_start) DESC) AS parent_id,
                       child.id AS child_id
                  FROM account_group parent
                  JOIN account_group child
                    ON char_length(parent.code_prefix_start) < char_length(child.code_prefix_start)
                   AND parent.code_prefix_start <= LEFT(child.code_prefix_start, char_length(parent.code_prefix_start))
                   AND parent.code_prefix_end >= LEFT(child.code_prefix_end, char_length(parent.code_prefix_end))
                   AND parent.id != child.id
                   AND parent.company_id = child.company_id
                 WHERE child.company_id IN %(company_ids)s
            )
            UPDATE account_group child
               SET parent_id = relation.parent_id
              FROM relation
             WHERE child.id = relation.child_id;
        """
        self.env.cr.execute(query, {'company_ids': tuple(self.company_id.ids)})
        self.env['account.group'].invalidate_cache(fnames=['parent_id'])
        #         self.env['account.group'].search([('company_id', 'in', self.company_id.ids)])._parent_store_update()
        self._parent_store_update()
        
        
    def _adapt_accounts_for_account_groups(self, account_ids=None):
        return True

