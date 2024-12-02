from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import datetime

class AccountMove(models.Model):
    _inherit = "account.move"

    commission_sheet_id = fields.Many2one(
        'commission.history',
        string="Commission Sheet",
        copy=False,
        readonly=True
    )
    agent_id = fields.Many2one(
        'hr.employee',
        string="Agent employee",
        required=False,
        domain=[("is_agent", "=", True)]
    )

    is_create_commission = fields.Boolean(
        string="Create Commission?",
        default=True,
        copy=False,
    )
    commission_history_line_id = fields.Many2one(
        'commission.history.line',
        string="History Line",
        required=False,
    )


    def _write(self, vals):
        if 'payment_state' in vals:
            for invoice in self:
                if invoice.payment_state == 'paid':
                    if invoice.is_create_commission:
                        invoice.action_generate_sheet()
        return super(AccountMove, self)._write(vals)



    def _generate_bu_level_commission(self, contract_id):
        lines_to_commission = self.invoice_line_ids.filtered(lambda i: i.product_id.bu_id in self.agent_id.bu_ids)
        bu_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id')
        order = self
        agent_id = self.agent_id
        agent_ids = self.env['hr.employee'].search([('parent_id', 'child_of', agent_id.id)])
        for bu_id in bu_ids:
            target_rule_id = contract_id.hr_contract_commission_config_line_ids.filtered(lambda i: i.business_unit_id == bu_id)
            if target_rule_id:
                target_rule_id = target_rule_id[0]
                order_date = self.invoice_date
                #                 rule_id = target_rule_id.rule_id
                target_start_date = order_date.replace(day=1)
                target_end_date = order_date.replace(month=order_date.month + 1, day=1) - datetime.timedelta(days=1)
                if target_rule_id.division_level == 'all':
                    sale_domain = [
                        ('product_id.bu_id', '=', bu_id.id),
                        ('move_id.invoice_date', '>=', target_start_date),
                        ('move_id.invoice_date', '<=', target_end_date),
                        # ('move_id.payment_state', '=', 'paid'),
                        ('move_id.agent_id', 'in', agent_ids.ids),
                    ]
                    
                    amount_field = 'price_subtotal'
                    if contract_id.commission_type == 'gp':
                        amount_field = 'amount_gross_profit'
                    read_records = self.env['account.move.line'].read_group(
                        sale_domain,
                        [amount_field],
                        ['product_id']
                    )
                    price_total_amt = 0
                    for read_record in read_records:
                        price_total_amt += read_record[amount_field]
                    target_amount = target_rule_id.target_amount

                    target_percentage = (100.0 * price_total_amt) / target_amount
                    target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                        lambda
                            i: i.from_percentage > target_percentage
                    ).sorted(key = lambda i: i.from_percentage)
                    if target_commission_percent_line:
                        target_commission_percent_line = target_commission_percent_line[0]

                        base_amount = target_rule_id.commission_amount
                    
                        user = agent_id
                        commission_users = agent_id._get_commission_users(
                            company=order.company_id
                        )
                        commission_date = order.invoice_date
                        if not commission_date:
                            commission_date = fields.Date.today()
                        commission_sheet = user._get_commission_history(
                            commission_date=commission_date,
                            company=order.company_id
                        )
                        values = commission_users[user]
#                         price_total_amt = target_rule_id.commission_amount
                        
                        if order.currency_id != order.company_id.currency_id:
                            base_amount = order.currency_id._convert(
                                base_amount, order.company_id.currency_id
                            )
                        if base_amount >= 1.0:
                            exist_line = commission_sheet.commission_line_ids.filtered(
                                lambda i: i.business_unit_id == bu_id)
                            if exist_line:
                                exist_line.update({
                                    'base_amount': base_amount,
                                    'percentage': target_commission_percent_line.commission_percentage,
                                })
                                order.update({
                                    'commission_history_line_id': exist_line
                                })
                            else:
                                values = {
                                    'commission_user_id': agent_id.id,
                                    'commission_type': contract_id.commission_type,
                                    'target_amount': target_amount,
                                    'target_achieved_amount': price_total_amt,
                                    #                                     'commission_type': 'product',
                                    'commission_history_id': commission_sheet.id,
                                    'date_commission': commission_date,
                                    'base_amount': base_amount,
                                    'percentage': target_commission_percent_line.commission_percentage,
                                    #                                 'sale_id': order.id,
                                    'move_id': order.id,
                                    'responsible_user_id': order.agent_id.id,
                                    'business_unit_id': bu_id.id,
                                    'calculation_types': 'bu_level',
                                    'origin_ref' :  "business.unit" + ','+ str(bu_id.id)

                                    #                                 'product_id': line.product_template_id.id,
                                    #                             'agent_user_id': order.agent_id.id,
                                }
                                history_line = self.env['commission.history.line'].sudo().create(values)
#                                 order.update({
#                                     'commission_history_line_id': history_line
#                                 })
            
                elif target_rule_id.division_level == 'company_wise':
                    
                    target_comoany_rule_id = target_rule_id.line_ids.filtered(
                        lambda i: i.company_id == order.company_id)
                    if target_comoany_rule_id:
                        sale_domain = [
                            ('product_id.bu_id', '=', bu_id.id),
                            ('move_id.invoice_date', '>=', target_start_date),
                            ('move_id.invoice_date', '<=', target_end_date),
                            # ('move_id.payment_state', '=', 'paid'),
                            ('move_id.agent_id', 'in', agent_ids.ids),
                            ('move_id.company_id', '=', target_comoany_rule_id.company_id.id)
                        ]
                        amount_field = 'price_subtotal'
                        if contract_id.commission_type == 'gp':
                            amount_field = 'amount_gross_profit'
                        read_records = self.env['account.move.line'].read_group(
                            sale_domain,
                            [amount_field],
                            ['product_id']
                        )
                        price_total_amt = 0
                        for read_record in read_records:
                            price_total_amt += read_record[amount_field]
                        base_amount = target_rule_id.commission_amount

                        target_amount = target_comoany_rule_id.target_amount
                        target_percentage = (100.0 * price_total_amt) / target_amount
#                         target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
#                             lambda
#                                 i: i.from_percentage <= target_percentage and i.to_percentage >= target_percentage
#                         )
                        target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                            lambda
                                i: i.from_percentage > target_percentage
                        ).sorted(key = lambda i: i.from_percentage)
                        if target_commission_percent_line:
                            target_commission_percent_line = target_commission_percent_line[0]

                            user = agent_id
                            commission_users = agent_id._get_commission_users(
                                company=order.company_id
                            )
                            commission_date = order.invoice_date
                            if not commission_date:
                                commission_date = fields.Date.today()
                            commission_sheet = user._get_commission_history(
                                commission_date=commission_date,
                                company=order.company_id
                            )
                            values = commission_users[user]

                            if order.currency_id != order.company_id.currency_id:
                                base_amount = order.currency_id._convert(
                                    base_amount, order.company_id.currency_id
                                )
                            if base_amount >= 1.0:
                                ref =  target_comoany_rule_id.company_id
                                calculation_types = 'bu_level'
                                exist_line = commission_sheet.commission_line_ids.filtered(
                                    lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                if exist_line:
                                    exist_line.update({
                                        'base_amount': base_amount,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        'target_achieved_amount': price_total_amt,
                                    })
                                else:
                                    values = {
                                        'commission_user_id': agent_id.id,
                                        'commission_type': contract_id.commission_type,
                                        'commission_history_id': commission_sheet.id,
                                        'date_commission': commission_date,
                                        'base_amount': base_amount,
                                        'target_amount': target_amount,
                                        'target_achieved_amount': price_total_amt,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        #                                 'sale_id': order.id,
                                        'move_id': order.id,
                                        'responsible_user_id': order.agent_id.id,
                                        'business_unit_id': bu_id.id,
                                        'calculation_types': calculation_types,
                                        'origin_ref' :  "res.company" + ','+ str(target_comoany_rule_id.company_id.id)
                                        #                             'agent_user_id': order.agent_id.id,
                                    }
                                    history_line = self.env['commission.history.line'].sudo().create(values)
#                                 order.update({
#                                     'commission_history_line_id': history_line
#                                 })
        return 

    def _generate_company_level_commission(self, contract_id):
        target_rule_id = contract_id.hr_contract_commission_config_line_ids.filtered(lambda i: i.company_id == self.company_id)
        if target_rule_id:
            target_rule_id = target_rule_id[0]
            order_date = self.invoice_date
            #                 rule_id = target_rule_id.rule_id
            target_start_date = order_date.replace(day=1)
            target_end_date = order_date.replace(month=order_date.month + 1, day=1) - datetime.timedelta(days=1)
            
            
            agent_id = self.agent_id
            agent_ids = self.env['hr.employee'].search([('parent_id', 'child_of', agent_id.id)])
    #             target_comoany_rule_id = target_rule_id.employee_bu_company_target_allocation_ids.filtered(
#                 lambda i: i.company_id == order.company_id)
            if target_rule_id.division_level == 'all':
                sale_domain = [
#                     ('product_id.bu_id', '=', bu_id.id),
                    ('move_id.invoice_date', '>=', target_start_date),
                    ('move_id.invoice_date', '<=', target_end_date),
                    # ('move_id.payment_state', '=', 'paid'),
                    ('move_id.agent_id', 'in', agent_ids.ids),
                    ('move_id.company_id', '=', target_rule_id.company_id.id)
                ]
                amount_field = 'price_subtotal'
                if contract_id.commission_type == 'gp':
                    amount_field = 'amount_gross_profit'
                read_records = self.env['account.move.line'].read_group(
                    sale_domain,
                    [amount_field],
                    ['product_id']
                )
                price_total_amt = 0
                for read_record in read_records:
                    price_total_amt += read_record[amount_field]
                base_amount = target_rule_id.commission_amount

                target_amount = target_rule_id.target_amount
                target_percentage = (100.0 * price_total_amt) / target_amount

                target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                    lambda
                        i: i.from_percentage > target_percentage
                ).sorted(key = lambda i: i.from_percentage)
                if target_commission_percent_line:
                    target_commission_percent_line = target_commission_percent_line[0]
                    user = agent_id
                    commission_users = agent_id._get_commission_users(
                        company=self.company_id
                    )
                    commission_date = self.invoice_date
                    if not commission_date:
                        commission_date = fields.Date.today()
                    commission_sheet = user._get_commission_history(
                        commission_date=commission_date,
                        company=self.company_id
                    )
                    values = commission_users[user]

                    if self.currency_id != self.company_id.currency_id:
                        base_amount = self.currency_id._convert(
                            base_amount, self.company_id.currency_id
                        )
                    if base_amount >= 1.0:
                        ref =  target_rule_id.company_id
                        calculation_types = 'company_level'
                        exist_line = commission_sheet.commission_line_ids.filtered(
                            lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                        if exist_line:
                            exist_line.update({
                                'base_amount': base_amount,
                                'percentage': target_commission_percent_line.commission_percentage,
                                'target_achieved_amount': price_total_amt,
                            })
                        else:
                            values = {
                                'commission_user_id': agent_id.id,
                                'commission_type': contract_id.commission_type,
                                'commission_history_id': commission_sheet.id,
                                'date_commission': commission_date,
                                'base_amount': base_amount,
                                'target_amount': target_amount,
                                'target_achieved_amount': price_total_amt,
                                'percentage': target_commission_percent_line.commission_percentage,
                                #                                 'sale_id': order.id,
                                'move_id': self.id,
                                'responsible_user_id': self.agent_id.id,
                                'calculation_types': 'company_level',
                                'origin_ref' :  "res.company" + ','+ str(target_rule_id.company_id.id)
    
    #                             'business_unit_id': bu_id.id,
                                #                             'agent_user_id': order.agent_id.id,
                            }
                            history_line = self.env['commission.history.line'].sudo().create(values)
    #                                 order.update({
    #                                     'commission_history_line_id': history_line
#                                 })
            elif target_rule_id.division_level == 'bu_wise':
                
                lines_to_commission = self.invoice_line_ids.filtered(lambda i: i.product_id.bu_id in self.agent_id.bu_ids)
                bu_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id')
                
                for bu_id in bu_ids:
                
                    target_bu_rule_id = target_rule_id.line_ids.filtered(
                        lambda i: i.business_unit_id == bu_id)
                    if target_bu_rule_id:
                        sale_domain = [
                            ('product_id.bu_id', '=', bu_id.id),
                            ('move_id.invoice_date', '>=', target_start_date),
                            ('move_id.invoice_date', '<=', target_end_date),
                            # ('move_id.payment_state', '=', 'paid'),
                            ('move_id.agent_id', 'in', agent_ids.ids),
                        ]
                        amount_field = 'price_subtotal'
                        if contract_id.commission_type == 'gp':
                            amount_field = 'amount_gross_profit'
                        read_records = self.env['account.move.line'].read_group(
                            sale_domain,
                            [amount_field],
                            ['product_id']
                        )
                        price_total_amt = 0
                        for read_record in read_records:
                            price_total_amt += read_record[amount_field]
                        target_amount = target_bu_rule_id.target_amount
    
                        target_percentage = (100.0 * price_total_amt) / target_amount
                        target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                            lambda
                                i: i.from_percentage > target_percentage
                        ).sorted(key = lambda i: i.from_percentage)
                        if target_commission_percent_line:
                            target_commission_percent_line = target_commission_percent_line[0]
                            base_amount = target_rule_id.commission_amount
                        
                            user = agent_id
                            commission_users = agent_id._get_commission_users(
                                company=self.company_id
                            )
                            commission_date = self.invoice_date
                            if not commission_date:
                                commission_date = fields.Date.today()
                            commission_sheet = user._get_commission_history(
                                commission_date=commission_date,
                                company=self.company_id
                            )
                            values = commission_users[user]
    #                         price_total_amt = target_rule_id.commission_amount
                            
                            if self.currency_id != self.company_id.currency_id:
                                base_amount = self.currency_id._convert(
                                    base_amount, self.company_id.currency_id
                                )
                            if base_amount >= 1.0:
                                ref =  bu_id
                                calculation_types = 'company_level'
                                exist_line = commission_sheet.commission_line_ids.filtered(
                                    lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                if exist_line:
                                    exist_line.update({
                                        'base_amount': base_amount,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        'target_achieved_amount': price_total_amt,
                                    })
                                else:
                                    values = {
                                        'commission_user_id': agent_id.id,
                                        'commission_type': contract_id.commission_type,
                                        #                                     'commission_type': 'product',
                                        'commission_history_id': commission_sheet.id,
                                        'date_commission': commission_date,
                                        'base_amount': base_amount,
                                        'target_amount': target_amount,
                                        'target_achieved_amount': price_total_amt,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        #                                 'sale_id': order.id,
                                        'move_id': self.id,
                                        'responsible_user_id': self.agent_id.id,
                                        'business_unit_id': bu_id.id,
                                        'calculation_types': 'company_level',
                                        'origin_ref' :  "business.unit" + ','+ str(bu_id.id)
                                        #                                 'product_id': line.product_template_id.id,
                                        #                             'agent_user_id': order.agent_id.id,
                                    }
                                    history_line = self.env['commission.history.line'].sudo().create(values)


    def _generate_bu_group_level_commission(self, contract_id):
        bu_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id')
        bu_group_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id').mapped('bu_group_id')
        order = self
        agent_id = self.agent_id
        agent_ids = self.env['hr.employee'].search([('parent_id', 'child_of', agent_id.id)])
#         for bu_id in bu_ids:
        for bu_group_id in bu_group_ids:
            target_rule_id = contract_id.hr_contract_commission_config_line_ids.filtered(lambda i: i.bu_group_id == bu_group_id)
            if target_rule_id:
                target_rule_id = target_rule_id[0]
                order_date = self.invoice_date
                #                 rule_id = target_rule_id.rule_id
                target_start_date = order_date.replace(day=1)
                target_end_date = order_date.replace(month=order_date.month + 1, day=1) - datetime.timedelta(days=1)
                if target_rule_id.division_level == 'all':
                    sale_domain = [
                        ('product_id.bu_id.bu_group_id', '=', bu_group_id.id),
                        ('move_id.invoice_date', '>=', target_start_date),
                        ('move_id.invoice_date', '<=', target_end_date),
                        # ('move_id.payment_state', '=', 'paid'),
                        ('move_id.agent_id', 'in', agent_ids.ids),
                    ]
                    
                    amount_field = 'price_subtotal'
                    if contract_id.commission_type == 'gp':
                        amount_field = 'amount_gross_profit'
                    read_records = self.env['account.move.line'].read_group(
                        sale_domain,
                        [amount_field],
                        ['product_id']
                    )
                    price_total_amt = 0
                    for read_record in read_records:
                        price_total_amt += read_record[amount_field]
                    target_amount = target_rule_id.target_amount

                    target_percentage = (100.0 * price_total_amt) / target_amount
                    target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                        lambda
                            i: i.from_percentage > target_percentage
                    ).sorted(key = lambda i: i.from_percentage)
                    if target_commission_percent_line:
                        target_commission_percent_line = target_commission_percent_line[0]
                        base_amount = target_rule_id.commission_amount
                    
                        user = agent_id
                        commission_users = agent_id._get_commission_users(
                            company=order.company_id
                        )
                        commission_date = order.invoice_date
                        if not commission_date:
                            commission_date = fields.Date.today()
                        commission_sheet = user._get_commission_history(
                            commission_date=commission_date,
                            company=order.company_id
                        )
                        values = commission_users[user]
#                         price_total_amt = target_rule_id.commission_amount
                        
                        if order.currency_id != order.company_id.currency_id:
                            base_amount = order.currency_id._convert(
                                base_amount, order.company_id.currency_id
                            )
                        if base_amount >= 1.0:
                            ref =  bu_group_id
                            calculation_types = 'bu_group_level'
                            exist_line = commission_sheet.commission_line_ids.filtered(
                                lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                            if exist_line:
                                exist_line.update({
                                    'base_amount': base_amount,
                                    'percentage': target_commission_percent_line.commission_percentage,
                                    'target_achieved_amount': price_total_amt,
                                })
#                                     order.update({
#                                         'commission_history_line_id': exist_line
#                                     })
                            else:
                                values = {
                                    'commission_user_id': agent_id.id,
                                    'commission_type': contract_id.commission_type,
                                    'target_amount': target_amount,
                                    'target_achieved_amount': price_total_amt,
                                    #                                     'commission_type': 'product',
                                    'commission_history_id': commission_sheet.id,
                                    'date_commission': commission_date,
                                    'base_amount': base_amount,
                                    'percentage': target_commission_percent_line.commission_percentage,
                                    #                                 'sale_id': order.id,
                                    'move_id': order.id,
                                    'responsible_user_id': order.agent_id.id,
#                                     'business_unit_id': bu_id.id,
                                    'calculation_types': 'bu_group_level',
                                    'origin_ref' :  "business.unit.group" + ','+ str(bu_group_id.id)

                                    #                                 'product_id': line.product_template_id.id,
                                    #                             'agent_user_id': order.agent_id.id,
                                }
                                history_line = self.env['commission.history.line'].sudo().create(values)
#                                 order.update({
#                                     'commission_history_line_id': history_line
#                                 })
                elif target_rule_id.division_level == 'bu_wise':
                    for bu_id in bu_ids:
                        target_bu_rule_id = target_rule_id.line_ids.filtered(
                            lambda i: i.business_unit_id == bu_id)
                        if target_bu_rule_id:
                            sale_domain = [
                                ('product_id.bu_id.bu_group_id', '=', bu_group_id.id),
                                ('product_id.bu_id', '=', bu_id.id),
                                ('move_id.invoice_date', '>=', target_start_date),
                                ('move_id.invoice_date', '<=', target_end_date),
                                # ('move_id.payment_state', '=', 'paid'),
                                ('move_id.agent_id', 'in', agent_ids.ids),
                            ]
                            
                            amount_field = 'price_subtotal'
                            if contract_id.commission_type == 'gp':
                                amount_field = 'amount_gross_profit'
                            read_records = self.env['account.move.line'].read_group(
                                sale_domain,
                                [amount_field],
                                ['product_id']
                            )
                            price_total_amt = 0
                            for read_record in read_records:
                                price_total_amt += read_record[amount_field]
                            target_amount = target_bu_rule_id.target_amount
        
                            target_percentage = (100.0 * price_total_amt) / target_amount
                            target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                                lambda
                                    i: i.from_percentage > target_percentage
                            ).sorted(key = lambda i: i.from_percentage)
                            if target_commission_percent_line:
                                target_commission_percent_line = target_commission_percent_line[0]
                                base_amount = (target_bu_rule_id.commission_percentage * target_rule_id.commission_amount) / 100.0
                            
                                user = agent_id
                                commission_users = agent_id._get_commission_users(
                                    company=order.company_id
                                )
                                commission_date = order.invoice_date
                                if not commission_date:
                                    commission_date = fields.Date.today()
                                commission_sheet = user._get_commission_history(
                                    commission_date=commission_date,
                                    company=order.company_id
                                )
                                values = commission_users[user]
        #                         price_total_amt = target_rule_id.commission_amount
                                
                                if order.currency_id != order.company_id.currency_id:
                                    base_amount = order.currency_id._convert(
                                        base_amount, order.company_id.currency_id
                                    )
                                if base_amount >= 1.0:
                                    ref =  bu_id
                                    calculation_types = 'bu_group_level'
                                    exist_line = commission_sheet.commission_line_ids.filtered(
                                        lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                    if exist_line:
                                        exist_line.update({
                                            'base_amount': base_amount,
                                            'percentage': target_commission_percent_line.commission_percentage,
                                            'target_achieved_amount': price_total_amt,
                                        })
    #                                     order.update({
    #                                         'commission_history_line_id': exist_line
    #                                     })
                                    else:
                                        values = {
                                            'commission_user_id': agent_id.id,
                                            'commission_type': contract_id.commission_type,
                                            'target_amount': target_amount,
                                            'target_achieved_amount': price_total_amt,
                                            #                                     'commission_type': 'product',
                                            'commission_history_id': commission_sheet.id,
                                            'date_commission': commission_date,
                                            'base_amount': base_amount,
                                            'percentage': target_commission_percent_line.commission_percentage,
                                            #                                 'sale_id': order.id,
                                            'move_id': order.id,
                                            'responsible_user_id': order.agent_id.id,
#                                             'business_unit_id': bu_id.id,
                                            'calculation_types': 'bu_group_level',
                                            'origin_ref' :  "business.unit" + ','+ str(bu_id.id)
        
                                            #                                 'product_id': line.product_template_id.id,
                                            #                             'agent_user_id': order.agent_id.id,
                                        }
                                        history_line = self.env['commission.history.line'].sudo().create(values)
        #                                 order.update({
        #                                     'commission_history_line_id': history_line
        #                                 })
            
                elif target_rule_id.division_level == 'company_wise':
                    
                    target_comoany_rule_id = target_rule_id.line_ids.filtered(
                        lambda i: i.company_id == order.company_id)
                    if target_comoany_rule_id:
                        sale_domain = [
                            ('product_id.bu_id.bu_group_id', '=', bu_group_id.id),
                            ('move_id.invoice_date', '>=', target_start_date),
                            ('move_id.invoice_date', '<=', target_end_date),
                            # ('move_id.payment_state', '=', 'paid'),
                            ('move_id.agent_id', 'in', agent_ids.ids),
                            ('move_id.company_id', '=', target_comoany_rule_id.company_id.id)
                        ]
                        amount_field = 'price_subtotal'
                        if contract_id.commission_type == 'gp':
                            amount_field = 'amount_gross_profit'
                        read_records = self.env['account.move.line'].read_group(
                            sale_domain,
                            [amount_field],
                            ['product_id']
                        )
                        price_total_amt = 0
                        for read_record in read_records:
                            price_total_amt += read_record[amount_field]
#                         base_amount = target_rule_id.commission_amount
                        base_amount = (target_comoany_rule_id.commission_percentage * target_rule_id.commission_amount) / 100.0

                        target_amount = target_comoany_rule_id.target_amount
                        target_percentage = (100.0 * price_total_amt) / target_amount
                        target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                            lambda
                                i: i.from_percentage > target_percentage
                        ).sorted(key = lambda i: i.from_percentage)
                        if target_commission_percent_line:
                            target_commission_percent_line = target_commission_percent_line[0]
                            user = agent_id
                            commission_users = agent_id._get_commission_users(
                                company=order.company_id
                            )
                            commission_date = order.invoice_date
                            if not commission_date:
                                commission_date = fields.Date.today()
                            commission_sheet = user._get_commission_history(
                                commission_date=commission_date,
                                company=order.company_id
                            )
                            values = commission_users[user]

                            if order.currency_id != order.company_id.currency_id:
                                base_amount = order.currency_id._convert(
                                    base_amount, order.company_id.currency_id
                                )
                            if base_amount >= 1.0:
                                ref =  target_comoany_rule_id.company_id
                                calculation_types = 'bu_group_level'
                                exist_line = commission_sheet.commission_line_ids.filtered(
                                    lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                if exist_line:
                                    exist_line.update({
                                        'base_amount': base_amount,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        'target_achieved_amount': price_total_amt,
                                    })
#                                     order.update({
#                                         'commission_history_line_id': exist_line
#                                     })
                                else:
                                    values = {
                                        'commission_user_id': agent_id.id,
                                        'commission_type': contract_id.commission_type,
                                        'commission_history_id': commission_sheet.id,
                                        'date_commission': commission_date,
                                        'base_amount': base_amount,
                                        'target_amount': target_amount,
                                        'target_achieved_amount': price_total_amt,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        #                                 'sale_id': order.id,
                                        'move_id': order.id,
                                        'responsible_user_id': order.agent_id.id,
#                                         'business_unit_id': bu_id.id,
                                        'calculation_types': 'bu_group_level',
                                        'origin_ref' :  "res.company" + ','+ str(target_comoany_rule_id.company_id.id)
                                        #                             'agent_user_id': order.agent_id.id,
                                    }
                                    history_line = self.env['commission.history.line'].sudo().create(values)
    #                                 order.update({
#                                     'commission_history_line_id': history_line
#                                 })
            return 


    def _generate_region_level_commission(self, contract_id):
        country_id = self.partner_id.country_id
        if country_id:
            country_group_ids  = self.env['res.country.group'].search([('country_ids', 'in', country_id.ids)])
            for country_group_id in country_group_ids:
                order = self
                agent_id = self.agent_id
                agent_ids = self.env['hr.employee'].search([('parent_id', 'child_of', agent_id.id)])

                target_rule_id = contract_id.hr_contract_commission_config_line_ids.filtered(lambda i: i.country_group_id == country_group_id)
                if target_rule_id:
                    target_rule_id = target_rule_id[0]
                    order_date = self.invoice_date
                    #                 rule_id = target_rule_id.rule_id
                    target_start_date = order_date.replace(day=1)
                    target_end_date = order_date.replace(month=order_date.month + 1, day=1) - datetime.timedelta(days=1)
                    if target_rule_id.division_level == 'all':
                        sale_domain = [
                            ('partner_id.country_id', 'in', country_group_id.country_ids.ids),
                            ('move_id.invoice_date', '>=', target_start_date),
                            ('move_id.invoice_date', '<=', target_end_date),
                            # ('move_id.payment_state', '=', 'paid'),
                            ('move_id.agent_id', 'in', agent_ids.ids),
                        ]
                        
                        amount_field = 'price_subtotal'
                        if contract_id.commission_type == 'gp':
                            amount_field = 'amount_gross_profit'
                        read_records = self.env['account.move.line'].read_group(
                            sale_domain,
                            [amount_field],
                            ['product_id']
                        )
                        price_total_amt = 0
                        for read_record in read_records:
                            price_total_amt += read_record[amount_field]
                        target_amount = target_rule_id.target_amount
                        target_percentage = (100.0 * price_total_amt) / target_amount
                        target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                            lambda
                                i: i.from_percentage > target_percentage
                        ).sorted(key = lambda i: i.from_percentage)
                        if target_commission_percent_line:
                            target_commission_percent_line = target_commission_percent_line[0]
                            base_amount = target_rule_id.commission_amount
                        
                            user = agent_id
                            commission_users = agent_id._get_commission_users(
                                company=order.company_id
                            )
                            commission_date = order.invoice_date
                            if not commission_date:
                                commission_date = fields.Date.today()
                            commission_sheet = user._get_commission_history(
                                commission_date=commission_date,
                                company=order.company_id
                            )
                            values = commission_users[user]
    #                         price_total_amt = target_rule_id.commission_amount
                            
                            if order.currency_id != order.company_id.currency_id:
                                base_amount = order.currency_id._convert(
                                    base_amount, order.company_id.currency_id
                                )
                            if base_amount >= 1.0:
                                ref =  country_group_id
                                calculation_types = 'region_level'
                                exist_line = commission_sheet.commission_line_ids.filtered(
                                    lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                if exist_line:
                                    exist_line.update({
                                        'base_amount': base_amount,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        'target_achieved_amount': price_total_amt,
                                    })
    #                                     order.update({
    #                                         'commission_history_line_id': exist_line
    #                                     })
                                else:
                                    values = {
                                        'commission_user_id': agent_id.id,
                                        'commission_type': contract_id.commission_type,
                                        'target_amount': target_amount,
                                        'target_achieved_amount': price_total_amt,
                                        #                                     'commission_type': 'product',
                                        'commission_history_id': commission_sheet.id,
                                        'date_commission': commission_date,
                                        'base_amount': base_amount,
                                        'percentage': target_commission_percent_line.commission_percentage,
                                        #                                 'sale_id': order.id,
                                        'move_id': order.id,
                                        'responsible_user_id': order.agent_id.id,
    #                                     'business_unit_id': bu_id.id,
                                        'calculation_types': 'region_level',
                                        'origin_ref' :  "res.country.group" + ','+ str(country_group_id.id)
    
                                        #                                 'product_id': line.product_template_id.id,
                                        #                             'agent_user_id': order.agent_id.id,
                                    }
                                    history_line = self.env['commission.history.line'].sudo().create(values)
                    elif target_rule_id.division_level == 'country_wise':
                            country_id = self.partner_id.country_id
                            target_country_rule_id = target_rule_id.line_ids.filtered(
                                lambda i: i.country_id == country_id)
                            if target_country_rule_id:
                                sale_domain = [
                                    ('partner_id.country_id', 'in', country_id.ids),
#                                     ('product_id.bu_id', '=', bu_id.id),
                                    ('move_id.invoice_date', '>=', target_start_date),
                                    ('move_id.invoice_date', '<=', target_end_date),
                                    # ('move_id.payment_state', '=', 'paid'),
                                    ('move_id.agent_id', 'in', agent_ids.ids),
                                ]
                                
                                amount_field = 'price_subtotal'
                                if contract_id.commission_type == 'gp':
                                    amount_field = 'amount_gross_profit'
                                read_records = self.env['account.move.line'].read_group(
                                    sale_domain,
                                    [amount_field],
                                    ['product_id']
                                )
                                price_total_amt = 0
                                for read_record in read_records:
                                    price_total_amt += read_record[amount_field]
                                target_amount = target_country_rule_id.target_amount
            
                                target_percentage = (100.0 * price_total_amt) / target_amount
                                target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                                    lambda
                                        i: i.from_percentage > target_percentage
                                ).sorted(key = lambda i: i.from_percentage)
                                if target_commission_percent_line:
                                    target_commission_percent_line = target_commission_percent_line[0]
                                    base_amount = (target_country_rule_id.commission_percentage * target_rule_id.commission_amount) / 100.0
                                
                                    user = agent_id
                                    commission_users = agent_id._get_commission_users(
                                        company=order.company_id
                                    )
                                    commission_date = order.invoice_date
                                    if not commission_date:
                                        commission_date = fields.Date.today()
                                    commission_sheet = user._get_commission_history(
                                        commission_date=commission_date,
                                        company=order.company_id
                                    )
                                    values = commission_users[user]
            #                         price_total_amt = target_rule_id.commission_amount
                                    
                                    if order.currency_id != order.company_id.currency_id:
                                        base_amount = order.currency_id._convert(
                                            base_amount, order.company_id.currency_id
                                        )
                                    if base_amount >= 1.0:
                                        ref =  country_group_id
                                        calculation_types = 'region_level'
                                        exist_line = commission_sheet.commission_line_ids.filtered(
                                            lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                        if exist_line:
                                            exist_line.update({
                                                'base_amount': base_amount,
                                                'percentage': target_commission_percent_line.commission_percentage,
                                                'target_achieved_amount': price_total_amt,
                                            })
        #                                     order.update({
        #                                         'commission_history_line_id': exist_line
        #                                     })
                                        else:
                                            values = {
                                                'commission_user_id': agent_id.id,
                                                'commission_type': contract_id.commission_type,
                                                'target_amount': target_amount,
                                                'target_achieved_amount': price_total_amt,
                                                'commission_history_id': commission_sheet.id,
                                                'date_commission': commission_date,
                                                'base_amount': base_amount,
                                                'percentage': target_commission_percent_line.commission_percentage,
                                                'move_id': order.id,
                                                'responsible_user_id': order.agent_id.id,
                                                'calculation_types': 'region_level',
                                                'origin_ref' :  "res.country.group" + ','+ str(country_group_id.id)
                                            }
                                            history_line = self.env['commission.history.line'].sudo().create(values)
                    elif target_rule_id.division_level == 'bu_wise':
                        bu_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id')
                        for bu_id in bu_ids:
                            target_bu_rule_id = target_rule_id.line_ids.filtered(
                                lambda i: i.business_unit_id == bu_id)
                            if target_bu_rule_id:
                                sale_domain = [
                                    ('partner_id.country_id', 'in', country_group_id.country_ids.ids),
                                    ('product_id.bu_id', '=', bu_id.id),
                                    ('move_id.invoice_date', '>=', target_start_date),
                                    ('move_id.invoice_date', '<=', target_end_date),
                                    # ('move_id.payment_state', '=', 'paid'),
                                    ('move_id.agent_id', 'in', agent_ids.ids),
                                ]
                                
                                amount_field = 'price_subtotal'
                                if contract_id.commission_type == 'gp':
                                    amount_field = 'amount_gross_profit'
                                read_records = self.env['account.move.line'].read_group(
                                    sale_domain,
                                    [amount_field],
                                    ['product_id']
                                )
                                price_total_amt = 0
                                for read_record in read_records:
                                    price_total_amt += read_record[amount_field]
                                target_amount = target_bu_rule_id.target_amount
            
                                target_percentage = (100.0 * price_total_amt) / target_amount
                                target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                                    lambda
                                        i: i.from_percentage > target_percentage
                                ).sorted(key = lambda i: i.from_percentage)
                                if target_commission_percent_line:
                                    target_commission_percent_line = target_commission_percent_line[0]
                                    base_amount = (target_bu_rule_id.commission_percentage * target_rule_id.commission_amount) / 100.0
                                
                                    user = agent_id
                                    commission_users = agent_id._get_commission_users(
                                        company=order.company_id
                                    )
                                    commission_date = order.invoice_date
                                    if not commission_date:
                                        commission_date = fields.Date.today()
                                    commission_sheet = user._get_commission_history(
                                        commission_date=commission_date,
                                        company=order.company_id
                                    )
                                    values = commission_users[user]
            #                         price_total_amt = target_rule_id.commission_amount
                                    
                                    if order.currency_id != order.company_id.currency_id:
                                        base_amount = order.currency_id._convert(
                                            base_amount, order.company_id.currency_id
                                        )
                                    if base_amount >= 1.0:
                                        ref =  country_group_id
                                        calculation_types = 'region_level'
                                        exist_line = commission_sheet.commission_line_ids.filtered(
                                            lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                        if exist_line:
                                            exist_line.update({
                                                'base_amount': base_amount,
                                                'percentage': target_commission_percent_line.commission_percentage,
                                                'target_achieved_amount': price_total_amt,
                                            })
        #                                     order.update({
        #                                         'commission_history_line_id': exist_line
        #                                     })
                                        else:
                                            values = {
                                                'commission_user_id': agent_id.id,
                                                'commission_type': contract_id.commission_type,
                                                'target_amount': target_amount,
                                                'target_achieved_amount': price_total_amt,
                                                #                                     'commission_type': 'product',
                                                'commission_history_id': commission_sheet.id,
                                                'date_commission': commission_date,
                                                'base_amount': base_amount,
                                                'percentage': target_commission_percent_line.commission_percentage,
                                                #                                 'sale_id': order.id,
                                                'move_id': order.id,
                                                'responsible_user_id': order.agent_id.id,
    #                                             'business_unit_id': bu_id.id,
                                                'calculation_types': 'region_level',
                                                'origin_ref' :  "res.country.group" + ','+ str(country_group_id.id)
            
                                                #                                 'product_id': line.product_template_id.id,
                                                #                             'agent_user_id': order.agent_id.id,
                                            }
                                            history_line = self.env['commission.history.line'].sudo().create(values)
            #                                 order.update({
            #                                     'commission_history_line_id': history_line
            #                                 })
                
                    elif target_rule_id.division_level == 'company_wise':
                        
                        target_comoany_rule_id = target_rule_id.line_ids.filtered(
                            lambda i: i.company_id == order.company_id)
                        if target_comoany_rule_id:
                            sale_domain = [
                                ('partner_id.country_id', 'in', country_group_id.country_ids.ids),
                                ('move_id.invoice_date', '>=', target_start_date),
                                ('move_id.invoice_date', '<=', target_end_date),
                                # ('move_id.payment_state', '=', 'paid'),
                                ('move_id.agent_id', 'in', agent_ids.ids),
                                ('move_id.company_id', '=', target_comoany_rule_id.company_id.id)
                            ]
                            amount_field = 'price_subtotal'
                            if contract_id.commission_type == 'gp':
                                amount_field = 'amount_gross_profit'
                            read_records = self.env['account.move.line'].read_group(
                                sale_domain,
                                [amount_field],
                                ['product_id']
                            )
                            price_total_amt = 0
                            for read_record in read_records:
                                price_total_amt += read_record[amount_field]
    #                         base_amount = target_rule_id.commission_amount
                            base_amount = (target_comoany_rule_id.commission_percentage * target_rule_id.commission_amount) / 100.0
    
                            target_amount = target_comoany_rule_id.target_amount
                            target_percentage = (100.0 * price_total_amt) / target_amount
                            target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                                lambda
                                    i: i.from_percentage > target_percentage
                            ).sorted(key = lambda i: i.from_percentage)
                            if target_commission_percent_line:
                                target_commission_percent_line = target_commission_percent_line[0]
                                user = agent_id
                                commission_users = agent_id._get_commission_users(
                                    company=order.company_id
                                )
                                commission_date = order.invoice_date
                                if not commission_date:
                                    commission_date = fields.Date.today()
                                commission_sheet = user._get_commission_history(
                                    commission_date=commission_date,
                                    company=order.company_id
                                )
                                values = commission_users[user]
    
                                if order.currency_id != order.company_id.currency_id:
                                    base_amount = order.currency_id._convert(
                                        base_amount, order.company_id.currency_id
                                    )
                                if base_amount >= 1.0:
                                    ref =  country_group_id
                                    calculation_types = 'region_level'
                                    exist_line = commission_sheet.commission_line_ids.filtered(
                                        lambda i: i.origin_ref == ref and i.calculation_types == calculation_types)
                                    if exist_line:
                                        exist_line.update({
                                            'base_amount': base_amount,
                                            'percentage': target_commission_percent_line.commission_percentage,
                                            'target_achieved_amount': price_total_amt,
                                        })
    #                                     order.update({
    #                                         'commission_history_line_id': exist_line
    #                                     })
                                    else:
                                        values = {
                                            'commission_user_id': agent_id.id,
                                            'commission_type': contract_id.commission_type,
                                            'commission_history_id': commission_sheet.id,
                                            'date_commission': commission_date,
                                            'base_amount': base_amount,
                                            'target_amount': target_amount,
                                            'target_achieved_amount': price_total_amt,
                                            'percentage': target_commission_percent_line.commission_percentage,
                                            #                                 'sale_id': order.id,
                                            'move_id': order.id,
                                            'responsible_user_id': order.agent_id.id,
    #                                         'business_unit_id': bu_id.id,
                                            'calculation_types': 'region_level',
                                            'origin_ref' :  "res.country.group" + ','+ str(country_group_id.id)
                                            #                             'agent_user_id': order.agent_id.id,
                                        }
                                        history_line = self.env['commission.history.line'].sudo().create(values)
        #                                 order.update({
    #                                     'commission_history_line_id': history_line
    #                                 })
            


    def _generate_self_commission(self, contract_id):
        if contract_id.plan_target_amount > 0 and contract_id.plan_commission_amount > 0:
            order_date = self.invoice_date
            #                 rule_id = target_rule_id.rule_id
            target_start_date = order_date.replace(day=1)
            target_end_date = order_date.replace(month=order_date.month + 1, day=1) - datetime.timedelta(days=1)
            

            agent_id = self.agent_id
            agent_ids = self.env['hr.employee'].search([('parent_id', 'child_of', agent_id.id)])
            
            sale_domain = [
#                 ('product_id.bu_id', '=', bu_id.id),
                ('move_id.invoice_date', '>=', target_start_date),
                ('move_id.invoice_date', '<=', target_end_date),
                ('move_id.payment_state', '=', 'paid'),
                ('move_id.agent_id', 'in', agent_ids.ids),
            ]
            amount_field = 'price_subtotal'
            if contract_id.commission_type == 'gp':
                amount_field = 'amount_gross_profit'
            read_records = self.env['account.move.line'].read_group(
                sale_domain,
                [amount_field],
                ['product_id']
            )
            price_total_amt = 0
            for read_record in read_records:
                price_total_amt += read_record[amount_field]
            target_amount = contract_id.plan_target_amount

            target_percentage = (100.0 * price_total_amt) / target_amount
            target_commission_percent_line = contract_id.commission_target_percentage_employee_ids.filtered(
                lambda
                    i: i.from_percentage > target_percentage
            ).sorted(key = lambda i: i.from_percentage)
            if target_commission_percent_line:
                target_commission_percent_line = target_commission_percent_line[0]
                base_amount = contract_id.plan_commission_amount
            
                user = agent_id
                commission_users = agent_id._get_commission_users(
                    company=self.company_id
                )
                commission_date = self.invoice_date
                if not commission_date:
                    commission_date = fields.Date.today()
                commission_sheet = user._get_commission_history(
                    commission_date=commission_date,
                    company=self.company_id
                )
                values = commission_users[user]
#                         price_total_amt = target_rule_id.commission_amount
                
                if self.currency_id != self.company_id.currency_id:
                    base_amount = self.currency_id._convert(
                        base_amount, self.company_id.currency_id
                    )
                if base_amount >= 1.0:
#                     exist_line = commission_sheet.commission_line_ids.filtered(
#                         lambda i: i.business_unit_id == bu_id)
#                     if exist_line:
#                         exist_line.update({
#                             'base_amount': base_amount,
#                             'percentage': target_commission_percent_line.commission_percentage,
#                         })
# #                                     self.update({
# #                                         'commission_history_line_id': exist_line
# #                                     })
#                     else:
                        calculation_types = 'self'
                        exist_line = commission_sheet.commission_line_ids.filtered(
                            lambda i: i.calculation_types == calculation_types)
                        if exist_line:
                            exist_line.update({
                                'base_amount': base_amount,
                                'percentage': target_commission_percent_line.commission_percentage,
                                'target_achieved_amount': price_total_amt,
                            })
#                                     order.update({
#                                         'commission_history_line_id': exist_line
#                                     })
                        else:

                            values = {
                                'commission_user_id': agent_id.id,
                                'commission_type': contract_id.commission_type,
    
                                #                                     'commission_type': 'product',
                                'commission_history_id': commission_sheet.id,
                                'date_commission': commission_date,
                                'base_amount': base_amount,
                                'target_amount': target_amount,
                                'target_achieved_amount': price_total_amt,
                                'percentage': target_commission_percent_line.commission_percentage,
                                #                                 'sale_id': order.id,
                                'move_id': self.id,
                                'responsible_user_id': self.agent_id.id,
                                'calculation_types': 'self',
    #                             'origin_ref' :  "res.company" + ','+ str(target_comoany_rule_id.company_id.id)
    #                             'business_unit_id': bu_id.id,
                                #                                 'product_id': line.product_template_id.id,
                                #                             'agent_user_id': order.agent_id.id,
                            }
                            history_line = self.env['commission.history.line'].sudo().create(values)

    def action_generate_sheet(self):
        for invoice in self:
            if invoice.payment_state == 'paid':
                if invoice.agent_id:
#                     raise ValidationError(_("Please select valid agent!"))
                    state_domain = [('state', 'in', ['open'])]
                    contract_id = self.env['hr.contract'].search(
                        [
                            ('employee_id', 'in', invoice.agent_id.ids),
                            ('commission_config_plan_id', '!=', False),
                            ('contract_state', '=', 'approve')
                        ] + state_domain,
                        limit=1
                    )
                    if not contract_id:
                        raise ValidationError(_("Agent don't have valid contract!"))
            
                    if contract_id.calculation_types == 'bu_level':
                        invoice._generate_bu_level_commission(contract_id)
                    elif contract_id.calculation_types == 'company_level':
                        invoice._generate_company_level_commission(contract_id)
                    elif contract_id.calculation_types == 'region_level':
                        invoice._generate_region_level_commission(contract_id)
                    elif contract_id.calculation_types == 'bu_group_level':
                        invoice._generate_bu_group_level_commission(contract_id)
                    elif contract_id.calculation_types == 'self':
                        invoice._generate_self_commission(contract_id)