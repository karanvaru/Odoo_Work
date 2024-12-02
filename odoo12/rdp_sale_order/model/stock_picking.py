from odoo import fields, models, api, _
from datetime import datetime, date


class StockPicking(models.Model):
     _inherit = "stock.picking"
     
     ready_op = fields.Char(string="Ready OP", compute="compute_ready_op")
               
     
     @api.depends('date_ready', 'date_done')
     def compute_ready_op(self):
          for rec in self:
               if rec.date_done and rec.date_ready:
                    ready_date = rec.date_ready
                    done_date = rec.date_done
                    if isinstance(ready_date, str):
                         ready_date = datetime.strptime(ready_date, "%Y-%m-%d %H:%M:%S")
                    if isinstance(done_date, str):
                         done_date = datetime.strptime(done_date, "%Y-%m-%d %H:%M:%S")
                    rec.ready_op = str((done_date - ready_date).days) + " Days"
               elif rec.date_ready:
                    today = datetime.today()
                    ready_date = rec.date_ready
                    if isinstance(ready_date, str):
                         ready_date = datetime.strptime(ready_date, "%Y-%m-%d %H:%M:%S")
                    rec.ready_op = str((today - ready_date).days) + " Days"
               else:
                    rec.ready_op = ""