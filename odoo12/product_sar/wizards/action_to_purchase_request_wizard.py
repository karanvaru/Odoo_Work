from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class ActionToPurchaseRequest(models.TransientModel):
    _name = "action.purchase.request"

    user_id = fields.Many2one(
        'res.users',
        'User'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id
    )

    def purchase_request(self):
        pur_tender = self.env['purchase.agreement']
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        purchase_agreement_type = self.env['purchase.agreement.type'].search([],limit=1)
        if not purchase_agreement_type:
            raise ValidationError("Add Agreement Type For Purchase Agreement")
        if not self.user_id or not self.company_id:
            raise ValidationError("Add User And Company For Purchase Agreement")
        if active_record.part_details_ids:
            for line in active_record.part_details_ids:
                if line.product:
                    vals = {
                        'purchase_tender_id': active_record.id,
                        'sh_source': active_record.name,
                        'sh_agreement_type': purchase_agreement_type.id,
                        'sh_purchase_user_id': self.user_id.id,
                        'company_id': self.company_id.id,
                        'sh_purchase_agreement_line_ids': [
                            (0, 0, {'sh_product_id': line.product.id, 'sh_qty': line.part_rq_qty})]
                    }
                    tender_val = pur_tender.create(vals)
        # ================================End================22-02-2023

        from_state = active_record.state
        from_date = False
        open_date = 0
        if active_record.state == 'request_accept':
            active_record.request_accept_out = datetime.today()
            if active_record.request_accept_in and active_record.request_accept_out:
                from_date = active_record.request_accept_in
                start = datetime.strftime(active_record.request_accept_in, '%Y-%m-%d %H:%M:%S')
                end = datetime.strftime(active_record.request_accept_out, '%Y-%m-%d %H:%M:%S')
                start_last = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end_last = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                open_date = (end_last - start_last)
                active_record.request_accept_days = (end_last - start_last)
            # self.request_accept_days = (active_record.request_accept_out - active_record.request_accept_in)
            date_to = active_record.request_accept_out
            # active_record.request_accept_days = (active_record.request_accept_out - active_record.request_accept_in)
        active_record.purchase_request_in = datetime.today()
        active_record.write({'state': 'purchase_request'})
        active_record.update({'detail_ids': [(0, 0, {
            'from_stage': from_state,
            'to_stage': active_record.state,
            'in_date': from_date or False,
            'out_date': date_to,
            'open_days': open_date or False})]
                     })
        return tender_val
