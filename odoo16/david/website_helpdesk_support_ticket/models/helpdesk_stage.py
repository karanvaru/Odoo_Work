# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

#not used odoo13
AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class HelpdeskStageConfig(models.Model):
    _name = "helpdesk.stage.config"
    _description = "Stage of case"
    _rec_name = 'name'
    _order = "sequence, name, id"
    _sql_constraints = [
        ('stage_uniq', 'UNIQUE(stage_type)', 'The Type must be unique !')
    ]

    @api.model
    def default_get(self, fields):
        """ Hack :  when going from the pipeline, creating a stage with a sales team in
            context should not create a stage for the current sales team only
        """
        ctx = dict(self.env.context)
        if ctx.get('default_team_id') and not ctx.get('crm_team_mono'):
            ctx.pop('default_team_id')
        return super(HelpdeskStageConfig, self.with_context(ctx)).default_get(fields)
    
    name = fields.Char(
        'Stage Name',
        required=True,
        translate=True
    )
    sequence = fields.Integer(
        'Sequence',
        default=1,
        help="Used to order stages. Lower is better."
    )
#    probability = fields.Float(
#        'Probability (%)',
#        required=True,
#        default=10.0,
#        help="This percentage depicts the default/average probability of the Case for this stage to be a success"
#    )
    #on_change = fields.Boolean(
     #   'Change Probability Automatically',
      #  help="Setting this stage will change the probability automatically on the opportunity."
    #)
    requirements = fields.Text(
        'Requirements', 
        help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name."
    )
    team_id = fields.Many2one(
        'support.team',
        string='Support Team',
        ondelete='set null',
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.'
    )
    legend_priority = fields.Text(
        'Priority Management Explanation',
        translate=True,
        help='Explanation text to help users using the star and priority mechanism on stages or issues that are in this stage.'
    )
    fold = fields.Boolean(
        'Folded in Helpdesk',
        help='This stage is folded in the kanban view when there are no records in that stage to display.'
    )
    stage_type = fields.Selection(
        [('new','New'),
         ('assigned','Assigned'),
         ('work_in_progress','Work in Progress'),
         ('needs_more_info','Needs More Info'),
         ('needs_reply','Needs Reply'),
         ('reopened','Reopened'),
         ('solution_suggested','Solution Suggested'),
         ('closed','Closed')],
#        default='new',
        copy=False,
        string='Type',
    )
