# -*- coding: utf-8 -*-

from math import fmod
#from openerp import models, api, _ odoo13
#from openerp.exceptions import UserError, Warning odoo13
from odoo import models, api, _
from odoo.exceptions import UserError, Warning
from odoo.exceptions import UserError

class TimsheetTaskInvoice(models.TransientModel):
    _name = 'task.timesheet.invoice'
    _description = "Task Timesheet Invoice"

    def check_custom_add_lines(self, invoice, account_line):
        return True

#    @api.multi odoo13
    def _prepare_invoice(self, account_line, customer, project):
        # inv_obj = self.env['account.invoice']odoo13
        inv_obj = self.env['account.move']
        invoice_vals = {}
 
        domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.user.company_id.id),
        ]
        journal_id = self.env['account.journal'].search(domain, limit=1)
        if not journal_id:
            raise UserError(_('Please configure an accounting sale journal for this company.'))
 
        invoice_vals.update({
#            'origin': 'Invoice from Timesheet',odoo13
            'invoice_origin': 'Invoice from Timesheet',
#            'type': 'out_invoice',
            'move_type': 'out_invoice',
            'partner_id': customer.id,
            'journal_id': journal_id.id,
#            'payment_term_id': customer.property_payment_term_id.id,odoo13
            'invoice_payment_term_id': customer.property_payment_term_id.id,
            'fiscal_position_id': customer.property_account_position_id.id,
        })
        return inv_obj.sudo().create(invoice_vals)

#    @api.multi odoo13
    def _prepare_invoice_line(self, account_lines, invoice):
        task_list= []
        aline_list = []
        invoice_line_vals = []
        for account_line in account_lines:
            aline_list.append(account_line.id)
            time_in = str(int(account_line.time_in)) + ':' + str(int(fmod(account_line.time_in, 1) * 60))
            time_out = str(int(account_line.time_out)) + ':' + str(int(fmod(account_line.time_out, 1) * 60))
            name = ''
            
            # get price unit for line
            price_unit = 0.0
            if account_line.task_id and account_line.task_id.price_rate > 0.0:
                price_unit = account_line.task_id.price_rate
            elif account_line.project_id and account_line.project_id.price_rate > 0.0:
                price_unit = account_line.project_id.price_rate
            else:
                price_unit = account_line.project_id.partner_id.price_rate

            # get product_id
            product_id_helpdesk = False
            account = False
            if account_line.task_id and account_line.task_id.product_id_helpdesk:
                product_id_helpdesk = account_line.task_id.product_id_helpdesk.id 
                account = account_line.task_id.product_id_helpdesk.property_account_income_id or account_line.task_id.product_id_helpdesk.categ_id.property_account_income_categ_id
            elif account_line.project_id and account_line.project_id.product_id_helpdesk:
                product_id_helpdesk = account_line.project_id.product_id_helpdesk.id
                account = account_line.project_id.product_id_helpdesk.property_account_income_id or account_line.project_id.product_id_helpdesk.categ_id.property_account_income_categ_id
            else:
                product_id_helpdesk = account_line.project_id.partner_id.product_id_helpdesk.id
                account = account_line.project_id.partner_id.product_id_helpdesk.property_account_income_id or account_line.project_id.partner_id.product_id_helpdesk.categ_id.property_account_income_categ_id        

            
            if account_line.task_id:
                task_list.append(account_line.task_id.id)
                name = account_line.task_id.name + ' : '
                #amount = account_line.task_id.price_rate
                account_analytic_id = account_line.task_id.project_id.analytic_account_id.id
            else:
                #amount = account_line.project_id.price_rate
                account_analytic_id = account_line.project_id.analytic_account_id.id
            name += account_line.name + ' / Time In '+ str(time_in) + ' / Time Out ' + str(time_out) + '\n'
            
            if not account:
                # account = self.env['ir.property'].get('property_account_income_categ_id', 'product.category')
                account = self.env['ir.property']._get('property_account_income_categ_id', 'product.category')
            if not account:
                raise UserError(_('Please configure Default Income account for Product income: `property_account_income_categ_id`.'))
            line_product = self.env['product.product'].sudo().browse(product_id_helpdesk) if product_id_helpdesk else False
            res = {
                    'name': _(name),
                    'account_id': account.id ,
                    'price_unit': price_unit,#we allready manipulate the total task cost (account_obj.unit_amount*account_obj.amount)
                    'quantity': account_line.unit_amount,
#                    'invoice_id': invoice.id, odoo13
                    'move_id': invoice.id,
#                    'account_analytic_id': account_analytic_id, odoo13
                    # 'analytic_account_id' : account_analytic_id, #16
                    'product_id': product_id_helpdesk,
                    'tax_ids': [(6, 0, line_product.taxes_id.filtered(lambda tax: tax.company_id == account_line.company_id).ids)] if line_product else [],
                    'product_uom_id': line_product.uom_id.id if line_product else False,
                }
#            self.env['account.invoice.line'].create(res) odoo13
            invoice_line_vals.append((0, 0, res))
            self.check_custom_add_lines(invoice , account_line)
        invoice.write({'invoice_line_ids' : invoice_line_vals})
#        invoice.project_task_ids = task_list V14
#        invoice.analytic_line_ids = aline_list V14
        return True

#    @api.multi odoo13
    def create_timesheet_invoice(self):
        active_ids = self._context.get('active_ids')
        # inv_obj = self.env['account.invoice']odoo13
        inv_obj = self.env['account.move']
        analytic_account_line = self.env['account.analytic.line'].sudo().browse(active_ids)
        customer_invoice = {}#(10,100): []
        for res_line in analytic_account_line:
            if res_line.invoiced_created:
                raise UserError(_('Invoice can not be created since some of Timesheet lines are already invoiced so please check.'))
            if not res_line.project_id.partner_id:
                raise UserError(_('No customer found on some Timesheet lines.'))
            if (res_line.partner_id.id, res_line.project_id.id) not in customer_invoice:
                customer_invoice[(res_line.partner_id.id, res_line.project_id.id)] = [res_line]
            else:
                customer_invoice[(res_line.partner_id.id, res_line.project_id.id)].append(res_line)
        invoice_ids = []
        for line in customer_invoice:
            partner_id = self.env['res.partner'].sudo().browse(line[0])
            project_id = self.env['project.project'].sudo().browse(line[1])
            invoice = self._prepare_invoice(customer_invoice[line], partner_id, project_id)
            
            for timesheet in customer_invoice[line]:
                timesheet.write({
                    'custom_timesheet_invoice_id': invoice.id
                })
            
            if invoice is None:
                raise UserError(_('No invoices created.'))
            invoice_ids.append(invoice.id)
            self._prepare_invoice_line(customer_invoice[line], invoice)
            for analyitic_line in customer_invoice[line]:#set boolean invoiced to true so next time it will be skip
                analyitic_line.invoiced_created = True

#        action_id = self.env.ref('account.action_invoice_tree1') odoo13
        action_id = self.env.ref('account.action_move_out_invoice_type')
        if action_id:
            action = action_id.sudo().read([])[0]
            action['domain'] =\
               "[('id','in', ["+','.join(map(str, invoice_ids))+"])]"
            return action
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
