from operator import truediv
from pickle import TRUE

from pkg_resources import require
from odoo import api, fields, models, _


class ContractTerminateReasionWizard(models.TransientModel):
    _name = 'contract.terminate.entry.wizard'
    _description = 'Contract Terminate Entry Wizard'

    deactive_reasion = fields.Selection([
        ('onSite', 'On Site'),
        ('onOurOffice', 'On Our Office'),
        ('dead', 'Dead'),
        ('other', 'Other')
    ], string='Deactive Reasion', required=True)
    terminate_comment = fields.Text(
        string="Termination Comment",
        required=True
    )

    def terminate_it(self):
        new_contract_id = self._context.get('active_id')
        contractObj = self.env['contract.contract'].search([('id', '=', new_contract_id)], limit=1)
        contractlineObj = self.env['contract.line'].search([('id', '=', new_contract_id)], limit=1)

        if contractObj:
            contractObj.update({
                'state': 'terminate',
                'is_terminated': True,
                'terminate_comment': self.terminate_comment
            })
            contractObj.contract_line_fixed_ids[0].product_id.update({
                'product_status': 'deactive',
                'deactive_reasion': self.deactive_reasion,
                'customer_id': False,
                'partner_shipping_pro_id': False,
            })
            contractObj.contract_line_fixed_ids[0].update({
                'comment': self.terminate_comment,
                'state_tree': 'terminate',
                'active': False,
                'is_canceled': True,

            })

        elif contractlineObj:
            status_check_id = self.env['contract.line'].search(
                [('contract_id', '=', contractlineObj.contract_id.id), ('is_canceled', '!=', True)])
            if len(status_check_id) == 1:
                contractlineObj.contract_id.update({
                    'state': 'terminate',
                    'is_terminated': True,
                    'terminate_comment': self.terminate_comment

                })
                contractlineObj.update({
                    'comment': self.terminate_comment,
                    'active': False,
                    'is_canceled': True,
                    'state_tree': 'terminate',
                })
                contractlineObj.product_id.update({
                    'product_status': 'deactive',
                    'current_contract_id': False,
                    'customer_id': False,
                    'partner_shipping_pro_id': False
                })
            else:
                contractlineObj.update({
                    'state_tree': 'terminate',
                    'active': False,
                    'is_canceled': True,
                    'comment': self.terminate_comment,

                })
                contractlineObj.product_id.update({
                    'product_status': 'deactive',
                    'current_contract_id': False,
                    'customer_id': False,
                    'partner_shipping_pro_id': False,
                    'deactive_reasion': self.deactive_reasion,

                })
