from odoo import fields,models,api,_


class ScmCategory(models.Model):
    _name = "scm.category"

    name = fields.Char(string="Category Name")