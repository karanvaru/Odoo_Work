# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = 'project.project'
    cost_items_ids = fields.One2many('cost.estimation.line', 'project_id')
    cost_estimation_ids = fields.Many2one('cost.estimation', string='Cost Estimation',readonly=True)

    @api.constrains('cost_estimation_ids')
    def update_cost_items(self):
        product_list = [(5, 0, 0)]
        self.cost_items_ids=self.cost_estimation_ids.cost_estimation_line
        # for line in self.cost_estimation_ids.cost_estimation_line:
        #     product_list.append((0, 0, {
        #                                 'salable_product':line.salable_product
        #                                 'cost_item': line.cost_item.id,
        #                                 'cost_item_description': line.cost_item_description,
        #                                 'cost_item_quant_sp': line.cost_item_quant_sp,
        #                                 'cost_item_unit_cost': line.cost_item_unit_cost,
        #                                 'taxes': line.taxes.ids,
        #                                 'project_id': self.id
        #                                 }))
        #
        #     self.cost_items_ids=product_list

