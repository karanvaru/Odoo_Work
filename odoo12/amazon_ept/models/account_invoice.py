from odoo import models, api, fields


class account_invoice(models.Model):
    _inherit = "account.invoice"

    amazon_instance_id = fields.Many2one("amazon.instance.ept", "Instances")
    seller_id = fields.Many2one("amazon.seller.ept", "Seller")
    reimbursement_id = fields.Char(string="Reimbursement Id")
    fulfillment_by = fields.Selection(
        [('MFN', 'Manufacturer Fulfillment Network'), ('AFN', 'Amazon Fulfillment Network')],
        string="Fulfillment By", default='MFN')
        
    """ 
    In invoice Odoo will set fiscal position based on partner fiscal position and it is creating issue
    while creating invoice from sales order
    Due to that reason override this method and set fiscal position based on sales order
    """
    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        result = super(account_invoice, self)._onchange_partner_id()
        if self.amazon_instance_id:
            if self.invoice_line_ids:
                order = self.invoice_line_ids[0].sale_line_ids and \
                        self.invoice_line_ids[0].sale_line_ids[0].order_id or False
                if order:
                    fpos = order.fiscal_position_id and order.fiscal_position_id.id or False
                    if fpos and self.fiscal_position_id.id != fpos:
                        self.fiscal_position_id = fpos or False
        return result

    """
     Set seller,global channel,instance in the refund
    """
    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None,
                        journal_id=None):
        values = super(account_invoice, self)._prepare_refund(invoice, date_invoice=date_invoice, date=date,
                                                              description=description, journal_id=journal_id)
        values.update({'seller_id': self.seller_id and self.seller_id.id or False,
                       'global_channel_id': self.seller_id.global_channel_id and
                                            self.seller_id.global_channel_id.id or False,
                       'amazon_instance_id': self.amazon_instance_id and
                                             self.amazon_instance_id.id or False
                       })
        return values

    """ 
    Scheduler method to send invoice via email to customer
    This method will send invoice in Amazon backend 
    Amazon will send to the customer
    """
    @api.model
    def send_amazon_invoice_via_email(self, args={}):
        instance_obj = self.env['amazon.instance.ept']
        seller_obj = self.env['amazon.seller.ept']
        invoice_obj = self.env['account.invoice']
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = seller_obj.search([('id', '=', seller_id)])
            if not seller:
                return True

            email_template = self.env.ref('account.email_template_edi_invoice', False)
            instances = instance_obj.search([('seller_id', '=', seller.id)])

            for instance in instances:
                if instance.invoice_tmpl_id:
                    email_template = instance.invoice_tmpl_id
                invoices = invoice_obj.search(
                    [('amazon_instance_id', '=', instance.id), ('state', 'in', ['open', 'paid']),
                     ('sent', '=', False), ('type', '=', 'out_invoice')])
                for invoice in invoices:
                    email_template.send_mail(invoice.id)
                    invoice.write({'sent': True})
        return True

    """ 
    Scheduler method to send refund via email to customer
    This method will send invoice in Amazon backend 
    Amazon will send to the customer
    """
    @api.model
    def send_amazon_refund_via_email(self, args={}):
        instance_obj = self.env['amazon.instance.ept']
        seller_obj = self.env['amazon.seller.ept']
        invoice_obj = self.env['account.invoice']
        seller_id = args.get('seller_id', False)
        if seller_id:
            seller = seller_obj.search([('id', '=', seller_id)])
            if not seller:
                return True
            email_template = self.env.ref('account.email_template_edi_invoice', False)
            instances = instance_obj.search([('seller_id', '=', seller.id)])
            for instance in instances:
                if instance.refund_tmpl_id:
                    email_template = instance.refund_tmpl_id
                invoices = invoice_obj.search(
                    [('amazon_instance_id', '=', instance.id), ('state', 'in', ['open', 'paid']),
                     ('sent', '=', False), ('type', '=', 'out_refund')], limit=1)
                for invoice in invoices:
                    email_template.send_mail(invoice.id)
                    invoice.write({'sent': True})
        return True
