from odoo import fields, models, api, _



class ForceDonePickingWizard(models.TransientModel):
    _name = 'force.done.picking.wizard'

    force_done = fields.Boolean(
        string="Force Done",
    )

    def picking_done(self):
        print("_______________________________")