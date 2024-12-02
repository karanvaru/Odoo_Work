
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import datetime

class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_country_id = fields.Many2one(
        'res.country',
        'Country'
    )
    is_transfer = fields.Boolean('Is Transfer')
    bu_ids = fields.Many2many('business.unit', compute="_compute_bu_ids", store=True)
    

    @api.depends('invoice_line_ids.product_id')
    def _compute_bu_ids(self):
        for move in self:
            # Get all BU IDs from the products in the invoice lines
            bu_ids = move.invoice_line_ids.mapped('product_id.bu_id')
            # Set the field to the unique list of BUs
            move.bu_ids = [(6, 0, bu_ids.ids)]

    @api.onchange('company_id')
    def onchange_company_id(self):
        for record in self:
            record.invoice_country_id = record.company_id.country_id.id

    # def _write(self, vals):
    #     if 'state' in vals:
    #         for invoice in self:
    #             if invoice.state == 'posted':
    #                 invoice.action_generate_sheet()
    #     return super(AccountMove, self)._write(vals)

    def _get_target_achived_amounts(self,  commission_config_id, filter_id):
        target_achived = 0
        common_domain = [
            ('move_id.invoice_date', '>=', commission_config_id.start_date),
            ('move_id.invoice_date', '<=', commission_config_id.end_date),
            ('move_id.state', '=', 'posted'),
            ('move_id.user_id', '=', self.user_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ]
        if commission_config_id.commission_type == 'bu_wise':
            domain = common_domain + [('product_id.bu_id', 'in', filter_id.ids)]
        elif commission_config_id.commission_type == 'bu_group_wise':
            domain = common_domain + [('product_id.bu_id.bu_group_id', '=', filter_id.ids)]
        if commission_config_id.commission_type == 'company_wise':
            domain = common_domain + [('move_id.company_id', 'in', filter_id.ids)]
        if commission_config_id.commission_type == 'country_wise':
            domain = common_domain + [('company_id.country_id', 'in', filter_id.ids)]
        if commission_config_id.commission_type == 'region_wise':
            domain = common_domain + [('company_id.country_id', 'in', filter_id.ids)]

        amount_field = 'price_subtotal'
        if commission_config_id.commission_measure_type == 'gross_profit':
            amount_field = 'gp'
        read_records = self.env['account.move.line'].read_group(
            domain,
            ['product_id', amount_field, 'move_type'],
            ['product_id']
        )
        price_total_amt = 0
        for read_record in read_records:
            move_type = read_record['product_id'][1]
            if move_type == 'out_invoice':
                target_achived += read_record['product_id'][0]
            elif move_type == 'out_refund':
                target_achived -= read_record['product_id'][0]
            
        return target_achived

    def _get_commission_percentage(self, target_rule_id,  target_achived, threshold_id):
        target_amount = target_rule_id.target_amount
        target_percentage = (100.0 * target_achived) / target_amount
        commission_percentage = 0
        target_commission_percent_line = threshold_id.line_ids.filtered(
            lambda i: i.from_percentage <= target_percentage and i.to_percentage >= target_percentage
        ).sorted(key = lambda i: i.from_percentage)
        if target_commission_percent_line:
            target_commission_percent_line = target_commission_percent_line[0]
            commission_percentage = target_commission_percent_line.commission_percentage
            if target_commission_percent_line.is_prorata:
                commission_percentage = target_percentage

        commission_amount_achived = (
            target_rule_id.commission_amount * commission_percentage
        ) / 100.0

        return commission_amount_achived, target_percentage

    def _generate_bu_wise_commission(self, commission_config_id, threshold_id):
        bu_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id')
        for bu_id in bu_ids:
            target_rule_id = commission_config_id.commission_structure_line_ids.filtered(
                lambda i: i.business_unit_id == bu_id
            )
            if target_rule_id:
                target_achived = self._get_target_achived_amounts(
                    commission_config_id,
                    filter_id=bu_id
                )
                commission_amount_achived, target_percentage_achived = self._get_commission_percentage(
                    target_rule_id,
                    target_achived,
                    threshold_id
                )
                target_rule_id.write({
                    'target_achived': target_achived,
                    'target_percentage_achived': target_percentage_achived,
                    'commission_amount_achived': commission_amount_achived
                })
        return True

    def _generate_bu_group_wise_commission(self, commission_config_id, threshold_id):
        bu_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id')
        bu_group_ids = self.invoice_line_ids.mapped('product_id').mapped('bu_id').mapped('bu_group_id')
        for bu_group_id in bu_group_ids:
            target_rule_id = commission_config_id.commission_structure_line_ids.filtered(
                lambda i: i.bu_group_id == bu_group_id
            )
            if target_rule_id:
                target_achived = self._get_target_achived_amounts(
                    commission_config_id,
                    filter_id=bu_group_id
                )
                commission_amount_achived, target_percentage_achived = self._get_commission_percentage(
                    target_rule_id,
                    target_achived,
                    threshold_id
                )
                target_rule_id.write({
                    'target_achived': target_achived,
                    'target_percentage_achived': target_percentage_achived,
                    'commission_amount_achived': commission_amount_achived
                })
        return True

    def _generate_company_wise_commission(self, commission_config_id, threshold_id):
        company_id = self.company_id
        target_rule_id = commission_config_id.commission_structure_line_ids.filtered(
            lambda i: i.company_id == company_id
        )
        if target_rule_id:
            target_rule_id = target_rule_id[0]

            target_achived = self._get_target_achived_amounts(
                commission_config_id,
                filter_id=company_id
            )
            commission_amount_achived, target_percentage_achived = self._get_commission_percentage(
                target_rule_id,
                target_achived,
                threshold_id
            )
            target_rule_id.write({
                'target_achived': target_achived,
                'target_percentage_achived': target_percentage_achived,
                'commission_amount_achived': commission_amount_achived
            })
        return True

    def _generate_country_wise_commission(self, commission_config_id, threshold_id):
        country_id = self.partner_id.country_id
        target_rule_id = commission_config_id.commission_structure_line_ids.filtered(
            lambda i: i.country_id == country_id
        )
        if target_rule_id:
            target_rule_id = target_rule_id[0]
            target_achived = self._get_target_achived_amounts(
                commission_config_id,
                filter_id=country_id
            )
            commission_amount_achived, target_percentage_achived = self._get_commission_percentage(
                target_rule_id,
                target_achived,
                threshold_id
            )
            target_rule_id.write({
                'target_achived': target_achived,
                'target_percentage_achived': target_percentage_achived,
                'commission_amount_achived': commission_amount_achived
            })
        return True

    def _generate_region_wise_commission(self, commission_config_id, threshold_id):
        country_id = self.partner_id.country_id
        country_group_ids  = self.env['res.country.group'].search([('country_ids', 'in', country_id.ids)])
        for country_group_id in country_group_ids:
            target_rule_id = commission_config_id.commission_structure_line_ids.filtered(
                lambda i: i.country_id == country_id
            )
            if target_rule_id:
                target_rule_id = target_rule_id[0]
    
                target_achived = self._get_target_achived_amounts(
                    commission_config_id,
                    filter_id=country_group_id.country_ids
                )
                commission_amount_achived, target_percentage_achived = self._get_commission_percentage(
                    target_rule_id,
                    target_achived,
                    threshold_id
                )
                target_rule_id.write({
                    'target_achived': target_achived,
                    'target_percentage_achived': target_percentage_achived,
                    'commission_amount_achived': commission_amount_achived
                })
        return True

    def action_generate_sheet(self):
        for invoice in self:
            if invoice.state == 'posted':
                if invoice.user_id and not invoice.is_transfer:
                    
                    CommissionStructureObj = self.env['commission.structure'].sudo()
                    
                    common_domain = [
                        ('start_date', '<=', invoice.invoice_date),
                        ('end_date', '>=', invoice.invoice_date),
                        ('state', '=', 'approved'),
                    ]
                    
                    commission_config_id = CommissionStructureObj.search([
                        ('user_id', '=', invoice.user_id.id),
                    ] + common_domain)

                    if not commission_config_id:
                        raise ValidationError(_("Agent don't have valid commission configuration!"))

                    commission_config_id.action_generate_commission()

                    bu_ids = invoice.invoice_line_ids.mapped('product_id').mapped('bu_id')
                    for bu_id in bu_ids:
                        # BU Manager commission
                        bu_manager_line_ids = bu_id.bu_manager_ids.filtered(
                            lambda i: invoice.company_id in i.company_ids
                        )
                        for bu_manager_line in bu_manager_line_ids:
                            bu_manager_config_id = CommissionStructureObj.search([
                                ('user_id', '=', bu_manager_line.user_id.id),
                            ] + common_domain)
                            if bu_manager_config_id:
                                bu_manager_config_id.action_generate_commission()

                        # BU Group commission
                        bu_group_manager_line_ids = bu_id.bu_group_id.bu_manager_ids.filtered(
                            lambda i: invoice.company_id in i.company_ids
                        )
                        for bu_group_manager_line in bu_group_manager_line_ids:
                            bu_group_manager_config_id = CommissionStructureObj.search([
                                ('user_id', '=', bu_group_manager_line.user_id.id),
                            ] + common_domain)
                            if bu_group_manager_config_id:
                                bu_group_manager_config_id.action_generate_commission()
                    
                    # Company manager
                    if self.company_id.company_manager_id:
                        company_manager_config_id = CommissionStructureObj.search([
                            ('user_id', '=', self.company_id.company_manager_id.id),
                        ] + common_domain)
                        if company_manager_config_id:
                            company_manager_config_id.action_generate_commission()


                    # Country Manager
                    if self.invoice_country_id.country_manager_id:
                        country_manager_config_id = CommissionStructureObj.search([
                            ('user_id', '=', self.invoice_country_id.country_manager_id.id),
                        ] + common_domain)
                        if country_manager_config_id:
                            country_manager_config_id.action_generate_commission()

                    # Region  Manager
                    country_group_ids = self.env['res.country.group'].sudo().search([
                        ('country_ids', 'in', self.invoice_country_id.ids),
                    ])
                    for country_group_id in country_group_ids:
                        if country_group_id.country_group_manager_id:
                            country_group_manager_config_id = CommissionStructureObj.search([
                                ('user_id', '=', country_group_id.country_group_manager_id.id),
                            ] + common_domain)
                            if country_group_manager_config_id:
                                country_group_manager_config_id.action_generate_commission()




class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    amount_gross_profit = fields.Float(
        string="Gross Profit",
        compute='_compute_amount_gross_profit',
        store=True
    )

    move_type = fields.Selection(related="move_id.move_type", store=True)

    @api.depends('price_unit', 'quantity', 'product_id.standard_price')
    def _compute_amount_gross_profit(self):
        for rec in self:
            rec.amount_gross_profit = (
                rec.price_unit - rec.product_id.standard_price
            ) * rec.quantity

