import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RepairInherited(models.Model): 
    _inherit = 'repair.order'

    repair_closing_date = fields.Date(string='Repair Closing Date', readonly='True')

    @api.one
    def action_repair_end(self):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        if self.filtered(lambda repair: repair.state != 'under_repair'):
            raise UserError(_("Repair must be under repair in order to end reparation."))
        for repair in self:
            repair.write({'repaired': True})
            vals = {'state': 'done'}
            vals['move_id'] = repair.action_repair_done().get(repair.id)
            if not repair.invoiced and repair.invoice_method == 'after_repair':
                vals['state'] = '2binvoiced'
            repair.write(vals)
        self.repair_closing_date = datetime.date.today()
        self.state = 'done'
        return True
        

