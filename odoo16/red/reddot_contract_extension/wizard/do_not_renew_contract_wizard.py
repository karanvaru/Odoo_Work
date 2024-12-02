from odoo import models, fields, api


class DoNotRenewContractWizard(models.TransientModel):
    _name = 'do.not.renew.contract.wizard'
    _description = "Do Not Renew Contract Wizard"

    comment = fields.Text(
        'Remark',
        required=True
    )

    def action_confirm(self):
        return  True
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        current_contact = self.env[active_model].browse(active_id)
        if current_contact:
            current_contact.update({
                'close_contract_comment': self.comment,
                'renewal_status': 'do_not_renew',
            })
            template_id = self.env.ref(
                'reddot_contract_extension.mail_template_contract_send_terminate')
            if template_id:
                template_id.send_mail(current_contact.id)

            
            
