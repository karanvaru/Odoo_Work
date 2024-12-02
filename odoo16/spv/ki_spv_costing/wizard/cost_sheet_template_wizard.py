from odoo import api, fields, models, _


class CostTemplateWizard(models.Model):
    _name = "cost.template.wizard"

    cost_panel_line_ids = fields.One2many("crm.panel.cost.line", "cost_line_id")

    @api.model
    def default_get(self, fields):
        res = super(CostTemplateWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        wizard_line = self.env['crm.cost.sheet.line'].browse(active_id)
        res['cost_panel_line_ids'] = wizard_line.crm_cost_sheet_id.crm_panel_cost_line_ids
        return res

    def action_confirm(self):
        active_id = self._context.get('active_id')
        wizard_line = self.env['crm.cost.sheet.line'].browse(active_id)
        wizard_line.crm_cost_sheet_id.crm_panel_cost_line_ids = [(6, 0, self.cost_panel_line_ids.ids)]
        if wizard_line:
            if wizard_line.product_id:
                if str(wizard_line.product_id.panel_type) == "solar_panel":
                    total = 0
                    total_no_of_structure = 0
                    total_structure_type = 0
                    total_height_of_structure = 0
                    total_total_foundation = 0
                    total_height_in_mm = 0
                    total_degree = 0
                    total_rafter_length = 0
                    total_no_of_legs = 0
                    for line in self.cost_panel_line_ids:
                        total += line.no_of_module
                        total_no_of_structure += line.no_of_structure
                        total_structure_type += line.structure_type
                        total_height_of_structure += line.height_of_structure
                        total_total_foundation += line.total_foundation
                        total_height_in_mm += line.height_in_mm
                        total_degree += line.degree
                        total_rafter_length += line.rafter_length
                        total_no_of_legs += line.no_of_legs
                    wizard_line.quantity = total
                    no_of_structure = total_no_of_structure
                    structure_type = total_structure_type
                    height_of_structure = total_height_of_structure
                    total_foundation = total_total_foundation
                    height_in_mm = total_height_in_mm
                    degree = total_degree
                    rafter_length = total_rafter_length
                    rafter_no_of_legs = total_no_of_legs
