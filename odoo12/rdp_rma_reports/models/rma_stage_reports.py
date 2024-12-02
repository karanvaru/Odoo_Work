# from time import strptime
# from odoo import api, fields, models, _
# from datetime import datetime
# from odoo.exceptions import AccessError

# class ProductSendAndRequest(models.Model):
#     _inherit = "product.details"

#     draft_stage_open_days = fields.Char('Draft Open Days',compute='compute_rma_stage_open_days')
#     part_request_stage_open_days = fields.Char('Part Request Open Days',compute='compute_rma_stage_open_days')
#     request_accepted_stage_open_days = fields.Char('Request Accepted Open Days',compute='compute_rma_stage_open_days')
#     purchase_request_stage_open_days = fields.Char('Purchase Request Open Days',compute='compute_rma_stage_open_days')
#     dispatched_stage_open_days = fields.Char('Dispatched Open Days',compute='compute_rma_stage_open_days')
#     part_reached_stage_open_days = fields.Char('Reached To CX Open Days',compute='compute_rma_stage_open_days')
#     repair_started_stage_open_days = fields.Char('Repair Started Open Days',compute='compute_rma_stage_open_days')
#     repaired_stage_open_days = fields.Char('Repaired Open Days',compute='compute_rma_stage_open_days')
#     pickup_initiated_stage_open_days = fields.Char('Pickup Initiated Open Days',compute='compute_rma_stage_open_days')
#     return_picked_stage_open_days = fields.Char('Return Picked Open Days',compute='compute_rma_stage_open_days')
#     closed_stage_open_days = fields.Char('Closed Open Days',compute='compute_rma_stage_open_days')
#     cancel_stage_open_days = fields.Char('Cancelled Open Days',compute='compute_rma_stage_open_days')

#     @api.multi 
#     def compute_rma_stage_open_days(self):
#         for rec in self:
#             temp_date = datetime.today()
#             temp_date_final = datetime.strftime(temp_date, '%Y-%m-%d %H:%M:%S')
#             current_date = datetime.strptime(temp_date_final, '%Y-%m-%d %H:%M:%S')
#             if rec.state == 'draft':
#                 draft = datetime.strftime(rec.draft_in, '%Y-%m-%d %H:%M:%S')
#                 draft_final = datetime.strptime(draft, '%Y-%m-%d %H:%M:%S')
#                 rec.draft_stage_open_days = (current_date - draft_final)
#             if rec.state == 'part_request':
#                 if rec.part_request_in:
#                     part_request = datetime.strftime(rec.part_request_in, '%Y-%m-%d %H:%M:%S')
#                     part_request_final = datetime.strptime(part_request, '%Y-%m-%d %H:%M:%S')
#                     rec.part_request_stage_open_days = (current_date - part_request_final)
#             if rec.state == 'request_accept':
#                 if rec.request_accept_in:
#                     request_accept = datetime.strftime(rec.request_accept_in, '%Y-%m-%d %H:%M:%S')
#                     request_accept_final = datetime.strptime(request_accept, '%Y-%m-%d %H:%M:%S')
#                     rec.request_accepted_stage_open_days = (current_date - request_accept_final)
#             if rec.state == 'purchase_request':
#                 if rec.purchase_request_in:
#                     purchase_request = datetime.strftime(rec.purchase_request_in, '%Y-%m-%d %H:%M:%S')
#                     purchase_request_final = datetime.strptime(purchase_request, '%Y-%m-%d %H:%M:%S')
#                     rec.purchase_request_stage_open_days = (current_date - purchase_request_final)
#             if rec.state == 'part_dispatched':
#                 if rec.part_dispatched_in:
#                     part_dispatched = datetime.strftime(rec.part_dispatched_in, '%Y-%m-%d %H:%M:%S')
#                     part_dispatched_final = datetime.strptime(part_dispatched, '%Y-%m-%d %H:%M:%S')
#                     rec.dispatched_stage_open_days = (current_date - part_dispatched_final)
#             if rec.state == 'part_reached':
#                 if rec.part_reached_in:
#                     part_reached = datetime.strftime(rec.part_reached_in, '%Y-%m-%d %H:%M:%S')
#                     part_reached_final = datetime.strptime(part_reached, '%Y-%m-%d %H:%M:%S')
#                     rec.part_reached_stage_open_days = (current_date - part_reached_final)
#             if rec.state == 'repair_started':
#                 if rec.repair_started_in:
#                     repair_started = datetime.strftime(rec.repair_started_in, '%Y-%m-%d %H:%M:%S')
#                     repair_started_final = datetime.strptime(repair_started, '%Y-%m-%d %H:%M:%S')
#                     rec.repair_started_stage_open_days = (current_date - repair_started_final)
#             if rec.state == 'repaired':
#                 if rec.repaired_in:
#                     repaired = datetime.strftime(rec.repaired_in, '%Y-%m-%d %H:%M:%S')
#                     repaired_final = datetime.strptime(repaired, '%Y-%m-%d %H:%M:%S')
#                     rec.repaired_stage_open_days = (current_date - repaired_final)
#             if rec.state == 'request_for_part_pickup':
#                 if rec.request_for_part_pickup_in:
#                     request_for_part_pickup = datetime.strftime(rec.request_for_part_pickup_in, '%Y-%m-%d %H:%M:%S')
#                     request_for_part_pickup_final = datetime.strptime(request_for_part_pickup, '%Y-%m-%d %H:%M:%S')
#                     rec.pickup_initiated_stage_open_days = (current_date - request_for_part_pickup_final)
#             if rec.state == 'in_transit':
#                 if rec.in_transit_in:
#                     in_transit = datetime.strftime(rec.in_transit_in, '%Y-%m-%d %H:%M:%S')
#                     in_transit_final = datetime.strptime(in_transit, '%Y-%m-%d %H:%M:%S')
#                     rec.return_picked_stage_open_days = (current_date - in_transit_final)
#             if rec.state == 'closed':
#                 if rec.closed_in:
#                     closed = datetime.strftime(rec.closed_in, '%Y-%m-%d %H:%M:%S')
#                     closed_final = datetime.strptime(closed, '%Y-%m-%d %H:%M:%S')
#                     rec.closed_stage_open_days = (current_date - closed_final)
#             if rec.state == 'cancel':
#                 if rec.cancel_in:
#                     cancel = datetime.strftime(rec.cancel_in, '%Y-%m-%d %H:%M:%S')
#                     cancel_final = datetime.strptime(cancel, '%Y-%m-%d %H:%M:%S')
#                     rec.cancel_stage_open_days = (current_date - cancel_final)


    