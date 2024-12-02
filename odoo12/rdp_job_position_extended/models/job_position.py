from odoo import api, fields, models, _

class JobPosition(models.Model):
    _inherit = 'hr.job'

    desc = fields.Html(string="Career Path")
    kras = fields.Html(string="KRAs")
    kpis = fields.Html(string="KPIs")
    reference_links = fields.Html(string="Reference Links")
    salary_range = fields.Char('Salary Range')