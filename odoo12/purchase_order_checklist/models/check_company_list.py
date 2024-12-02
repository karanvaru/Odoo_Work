#coding: utf-8

from odoo import _, api, fields, models

class check_company_list(models.Model):
    """
    A model to avoid changing checklist in a company form (and related security troubles)
    We use it instead of res.config.settings to apply properly editable trees
    """
    _name = "check.company.list"
    _description = "Check List"

    @api.multi
    @api.depends("company_id.name")
    def _compute_name(self):
        """
        Compute method for name
        """
        start_name = _("Checklist for the company")
        for checklist in self:
            checklist.name = u"{} {}".format(start_name, checklist.company_id.name)

    @api.multi
    def _inverse_check_line_ids(self):
        """
        Inverse method for check_line_ids
        """
        for checklist in self:
            checklist.check_line_ids.write({"company_id": checklist.company_id.id})

    @api.multi
    def _inverse_no_stages_ids(self):
        """
        Inverse method for no_stages_ids
        """
        for checklist in self:
            checklist.no_stages_ids.write({"company_no_id": checklist.company_id.id})

    name = fields.Char(
        string="Name",
        compute=_compute_name,
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    check_line_ids = fields.One2many(
        "purchase.check.item",
        "check_company_list_id",
        string="Check Lists",
        copy=True,
        inverse=_inverse_check_line_ids,
    )
    no_stages_ids = fields.One2many(
        "purchase.check.item",
        "check_no_company_list_id",
        string="""Determine the states, the transfer to which does not require filling in the check lists at the current
        stage""",
        copy=True,
        inverse=_inverse_no_stages_ids,
    )

    _sql_constraints = [
        (
            'company_id_uniq',
            'unique(company_id)',
            _('The checklist should be unique per company!'),
        )
    ]
