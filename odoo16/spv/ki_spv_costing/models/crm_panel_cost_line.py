from odoo import api, fields, models, _


class ResPartnerInherit(models.Model):
    _name = "crm.panel.cost.line"

    crm_cost_id = fields.Many2one("crm.cost.sheet")
    no_of_module = fields.Float('Quantity')
    no_of_structure = fields.Float('No Of Structure')
    structure_type = fields.Float('Structure Type')
    height_of_structure = fields.Float('Height Of Structure')
    total_foundation = fields.Float('Total Foundation')
    height_in_mm = fields.Float('Height in MM')
    degree = fields.Float('Degree')
    rafter_length = fields.Float('Rafter Length')
    no_of_legs = fields.Float('No. Of Legs')
    cost_line_id = fields.Many2one("cost.template.wizard")
