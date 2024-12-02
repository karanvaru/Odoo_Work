from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
from datetime import datetime,date,timedelta
from odoo.tools import float_compare

class ManufacturingInherit(models.Model):
    _inherit = 'mrp.production'
    open_days = fields.Char(string='Open Days',compute="compute_open_days")

    @api.multi
    def action_cancel(self):
        """ Cancels production order, unfinished stock moves and set procurement
        orders in exception """
        if any(workorder.state == 'progress' for workorder in self.mapped('workorder_ids')):
            raise UserError(_('You can not cancel production order, a work order is still in progress.'))
        documents = {}
        for production in self:
            for move_raw_id in production.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                iterate_key = self._get_document_iterate_key(move_raw_id)
                if iterate_key:
                    document = self.env['stock.picking']._log_activity_get_documents(
                        {move_raw_id: (move_raw_id.product_uom_qty, 0)}, iterate_key, 'UP')
                    for key, value in document.items():
                        if documents.get(key):
                            documents[key] += [value]
                        else:
                            documents[key] = [value]
            production.workorder_ids.filtered(lambda x: x.state != 'cancel').action_cancel()
            finish_moves = production.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            raw_moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            (finish_moves | raw_moves)._action_cancel()
            picking_ids = production.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            picking_ids.action_cancel()
        self.write({'state': 'cancel', 'is_locked': True})
        if documents:
            filtered_documents = {}
            for (parent, responsible), rendering_context in documents.items():
                if not parent or parent._name == 'stock.picking' and parent.state == 'cancel' or parent == self:
                    continue
                filtered_documents[(parent, responsible)] = rendering_context
            self._log_manufacture_exception(filtered_documents, cancel=True)

        self.date_finished = datetime.today()
        return True

    def compute_open_days(self):
            for record in self:
                if record['date_finished']:
                    record['open_days'] = str((record['date_finished'] - record['create_date']).days) + " Days"
                else:
                    record['open_days'] = str((datetime.today() - record['create_date']).days) + " Days"

                record['open_days'] = record['open_days'].split(',')[0]
                if record['open_days'] == '0:00:00':
                    record['open_days'] = '0 Days'


class ManufacturingWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    open_days = fields.Char(string='Open Days', compute="work_order_open_days")


    def work_order_open_days(self):
        print("Manufacturing")
        print("The current date is ", datetime.now())

        @api.multi
        def action_cancel(self):
            self.date_finished = datetime.today()
            return self.write({'state': 'cancel'})

        for rec in self:
            if rec.date_finished:
                rec.open_days = str((rec.date_finished - rec.create_date).days) + " Days"
            else:
                rec.open_days = str((datetime.today() - rec.create_date).days) + "Days"

