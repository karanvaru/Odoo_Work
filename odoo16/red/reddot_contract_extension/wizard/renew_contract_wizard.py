from odoo import models, fields, api, _


class RenewContractWizard(models.TransientModel):
    _name = 'renew.contract.wizard'
    _description = "Renew Contract Wizard"

    start_date = fields.Date(
        string='Start Date:',
        required=True,
        default=fields.Date.today()
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.today()
    )

    comment = fields.Text(
        'Comment',
        required=True
    )

    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        current_contact = self.env[active_model].browse(active_id)
        new_contract = current_contact.copy({
            'date_start': self.start_date,
            'date_end': self.end_date,
            'notes': self.comment,
            'state': 'draft',
            'renewal_status': ''
        })
        current_contact.update({
            'renewal_status': "approved",
            'new_contract_id': new_contract.id
        })
        action = self.env["ir.actions.actions"]._for_xml_id("hr_contract.action_hr_contract")
        action['views'] = [(self.env.ref('hr_contract.hr_contract_view_form').id, 'form')]
        action['res_id'] = new_contract.id
        return action
