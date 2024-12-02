
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    date_ready = fields.Datetime(string="Ready Date")
    otd1 = fields.Char(string="OTD 1", store=True, compute='calculate_otd1')

    # @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id')
    # @api.one
    # def _compute_state(self):
    #     ''' State of a picking depends on the state of its related stock.move
    #     - Draft: only used for "planned pickings"
    #     - Waiting: if the picking is not ready to be sent so if
    #       - (a) no quantity could be reserved at all or if
    #       - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
    #     - Waiting another move: if the picking is waiting for another move
    #     - Ready: if the picking is ready to be sent so if:
    #       - (a) all quantities are reserved or if
    #       - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
    #     - Done: if the picking is done.
    #     - Cancelled: if the picking is cancelled
    #     '''
    #     if not self.move_lines:
    #         self.state = 'draft'
    #     elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
    #         self.state = 'draft'
    #     elif all(move.state == 'cancel' for move in self.move_lines):
    #         self.state = 'cancel'
    #     elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
    #         self.state = 'done'
    #     else:
    #         relevant_move_state = self.move_lines._get_relevant_state_among_moves()
    #         if relevant_move_state == 'partially_available':
    #             self.state = 'assigned'
                
    #         else:
    #             self.state = relevant_move_state

    @api.multi
    def do_unreserve(self):
        for picking in self:
            picking.move_lines._do_unreserve()
            picking.date_ready = None
            picking.package_level_ids.filtered(lambda p: not p.move_ids).unlink()


    @api.multi
    def action_assign(self):
        # import pdb
        # pdb.set_trace()
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.filtered(lambda picking: picking.state == 'draft').action_confirm
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError(_('Nothing to'
                              ' check the availability for.'))
        # If a package level is done when confirmed its location can be different than where it will be reserved.
        # So we remove the move lines created when confirmed to set quantity done to the new reserved ones.
        package_level_done = self.mapped('package_level_ids').filtered(
            lambda pl: pl.is_done and pl.state == 'confirmed')
        package_level_done.write({'is_done': False})
        moves._action_assign()
        package_level_done.write({'is_done': True})

        if self.state == 'assigned':
            print('===========================assigned==========================')
                # ====================================
            
            for record in self:
                if record.scheduled_date and record.date_ready:
                    record.otd1 = str((record.date_ready - record.scheduled_date).days) + " Days"
                else:
                    self.date_ready = datetime.today()
                    record.otd1 = str((record.date_ready - record.scheduled_date).days) + " Days"
                # =====================================
        return True

    # @api.depends('date_ready','create_date','scheduled_date')
    # def calculate_otd1(self):
    #     for record in self:
    #         if record.scheduled_date:
    #             if record.date_ready:
    #                 record.otd1 = str((record.date_ready - record.scheduled_date).days) + " Days"
    #             else:
    #                 record.date_ready = None
    #                 record.otd1 = str((datetime.today() - record.scheduled_date).days) + " Days"

    # @api.depends('date_ready','create_date','scheduled_date')
    # def calculate_otd1(self):
    #     for record in self:
    #         if record.scheduled_date :
    #             record.otd1 = str((record.scheduled_date - record.date_ready).days) + " Days"
                

    


 #
        # str_date = self.date_ready.strftime("%Y-%m-%d %H:%M:%S")
        # ready_date = datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
        # for record in self:
        #
        #     # if record.scheduled_date:
        #     #     otd1 = ready_date - record.scheduled_date
        #     #     record.update({'otd1': str(otd1)})