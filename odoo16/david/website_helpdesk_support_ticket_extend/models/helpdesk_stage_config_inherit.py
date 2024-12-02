from odoo import api, fields, models


class HelpdeskStageConfigInherit(models.Model):
    _inherit = "helpdesk.stage.config"

    stage_type = fields.Selection(
        [('new', 'New'),
         ('assigned', 'Assigned'),
         ('work_in_progress', 'Work in Progress'),
         ('needs_more_info', 'Needs More Info'),
         ('needs_reply', 'Needs Reply'),
         ('reopened', 'Reopened'),
         ('solution_suggested', 'Solution Suggested'),
         ('pending_review', 'Pending Review'),
         ('closed', 'Closed'),
         ('to_invoice', 'To Invoice'),
         ],
        #        default='new',
        copy=False,
        string='Type',
    )
