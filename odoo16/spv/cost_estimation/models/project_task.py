# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = 'project.task'
    cost_items_ids = fields.One2many(related='project_id.cost_items_ids')
    cost_estimation_ids = fields.Many2one('cost.estimation', related='project_id.cost_estimation_ids', string='Cost Estimation')
    components_ids = fields.One2many('components.line', 'project_id')

    @api.model
    def create(self, vals):
        project = super(Project, self).create(vals)
        if project.sale_line_id.cost_line_id:
            project.sale_line_id.cost_line_id.write({'task_id': project.id})
        return project

    # @api.constrains('cost_estimation_ids','project_id')
    # def update_cost_items(self):
    #     self.cost_items_ids=[(5, 0, 0)]
    #     # product_list = [(5, 0, 0)]
    #     # for line in self.project_id.cost_estimation_ids.cost_estimation_line:
    #     #     product_list.append((0, 0, {'cost_item': line.cost_item.id,
    #     #                                 'total_cost_item_quantity':line.total_cost_item_quantity,
    #     #                                 'cost_item_description': line.cost_item_description,
    #     #                                 'cost_item_quant_sp': line.cost_item_quant_sp,
    #     #                                 'cost_item_unit_cost': line.cost_item_unit_cost,
    #     #                                 'cost_total_include_taxes':line.cost_total_include_taxes,
    #     #                                 'practical_amount':line.practical_amount,
    #     #                                 'taxes': line.taxes.ids,
    #     #                                 'task_id': self.id
    #     #                                 }))
    #
    #     self.cost_items_ids = self.cost_estimation_ids.cost_estimation_line
    #     print(self.cost_items_ids)
    #
    # #
    def action_request_materials(self):
        pass

    def action_material_request(self):
        pass


class ComponentsLine(models.Model):
    _name = 'components.line'
    _description = "Components Line"

    project_id = fields.Many2one('project.task')
    cost_items_id = fields.Many2one('cost.estimation', string="Cost Items", readonly=True)
    item_description_id = fields.Many2one('cost.estimation', string="Item Description", readonly=True)
    estimated_quantity = fields.Float(string="Estimated Quantity", readonly=True)
    actual_quantity = fields.Float(string="Actual Quantity", readonly=True)
