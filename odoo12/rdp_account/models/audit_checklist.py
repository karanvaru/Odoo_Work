from odoo import models, fields, api
from odoo.exceptions import AccessError

class AuditCheckList(models.Model):
    _name = 'audit.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Create Audit Checklist"

    name = fields.Char(string='Name', required= True,track_visibility='always')
    description = fields.Char(string='Description',track_visibility='always')
    journal_rel = fields.Many2one('account.journal')
    journal_ids = fields.Many2many('account.journal','journal_rel',string='Journals',required= True,track_visibility='always')
       #,compute="compute_journal_type")
                                    # domain=lambda self:self.compute_journal_type())
                                   #,compute="compute_journal_type")
    journal_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous')], string='Journal Type', store = True, required= True,track_visibility='always')
    
    # ===Dayan========================08.09.2022=========================Dayan===============
    groups_ids = fields.Many2many('res.groups', string="User Groups",track_visibility='always')
    reset = fields.Boolean('Not Saved',track_visibility='always')

    @api.onchange('journal_type')
    def compute_journal_type(self):
        for rec in self:
            jr_object = self.env['account.journal'].search([('type','=',rec.journal_type)])
            if jr_object:
               rec.journal_ids = False
               rec.journal_ids = jr_object.ids
            else:
               rec.journal_ids = False


# @api.depends('journal_type')
    # def compute_journal_type(self):
    #     data = []
    #     for rec in self:
    #         jr_object = self.env['account.journal'].search([('type','=',rec.journal_type)])
    #         print("jr_objectjr_objectjr_objectjr_objectjr_object",jr_object)
    #         return [('id', 'in',jr_object.ids)]
            # if jr_object:
             #   rec.journal_ids = jr_object.ids
            ##else:
             #   rec.journal_ids = False

            # if rec.journal_type == 



















