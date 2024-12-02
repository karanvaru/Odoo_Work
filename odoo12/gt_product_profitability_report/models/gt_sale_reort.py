# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
import datetime
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # product_id = fields.Many2one('product.product', 'Product Variant')
    list_price = fields.Float('Sale Value',store=True)
    standard_price = fields.Float(string="Product Cost" )
    profit = fields.Float(string="Profit")
    profitability = fields.Char(compute='_return_product_profitability',string="Profitability",store=True)
    return_qty = fields.Float(compute='_return_product_quantity',string='Retun Qty',store=True)
    qty_delivered = fields.Float('Qty Delivered')
    product_id = fields.Many2one('product.product',string="Product")

    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        for rs in res:
            if rs.product_id.type=='service':
                rs.product_id.standard_price=0
                rs.product_uom_qty=0
            elif rs.product_uom_qty == 0 and rs.qty_delivered == 0:
                rs.price_unit = 0
        return res

    @api.onchange('product_id','price_unit')
    def product_cost_from_saleline(self):
        self.standard_price = self.product_id.standard_price
        print("self.standard_price======",self.standard_price)
    #     self.profit = self.price_unit - self.product_id.standard_price
        # self.profitability = self.product_id.list_price - self.product_id.standard_price
    @api.one
    @api.depends('profit', 'return_qty','list_price','qty_delivered')
    def _return_product_profitability(self):
         for line in self:
            try:
                 self.profitability = float((self.qty_delivered-self.return_qty) * (self.profit / self.list_price) * 100)
                 print("self.profitability ======",self.profitability )
            except:
                 pass


    @api.depends('product_id','qty_delivered')
    def _return_product_quantity(self):
        for line in self:
            for picking_id in line.order_id.picking_ids:
                if picking_id.picking_type_id.code == 'incoming' and picking_id.state == 'done':
                    for move_id in picking_id.move_ids_without_package:
                        if line.product_id == move_id.product_id:
                            line.return_qty= move_id.quantity_done
                            # line.product_id.re_qty=line.return_qty
                            # print("re_qty========",line.return_qty)
        return True

class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(
        'Cost', company_dependent=True,
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help="Cost used for stock valuation in standard price and as a first price to set in average/fifo. "
             "Also used as a base price for pricelists. "
             "Expressed in the default unit of measure of the product.",store=True)
#
class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits=dp.get_precision('Product Price'), groups="base.group_user",
        help="Cost used for stock valuation in standard price and as a first price to set in average/FIFO.",store=True)

class SaleProductProfitReport(models.Model):
    _name = "sale.product.profit.report"
    _description = "Sales Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Order Reference', readonly=True)
    date = fields.Datetime('Order Date', readonly=True)
    confirmation_date = fields.Datetime('Confirmation Date', readonly=True)
    product_id = fields.Many2one('product.product', 'Product Variant', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    qty_delivered = fields.Float('Qty Delivered', readonly=True)
    qty_to_invoice = fields.Float('Qty To Invoice', readonly=True)
    qty_invoiced = fields.Float('Qty Invoiced', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    price_total = fields.Float('Total', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    untaxed_amount_to_invoice = fields.Float('Untaxed Amount To Invoice', readonly=True)
    untaxed_amount_invoiced = fields.Float('Untaxed Amount Invoiced', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Team', readonly=True, oldname='section_id')
    country_id = fields.Many2one('res.country', 'Customer Country', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', 'Customer Entity', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True)
    # weight = fields.Float('Gross Weight', readonly=True)
    # volume = fields.Float('Volume', readonly=True)
    #
    # discount = fields.Float('Discount %', readonly=True)
    # discount_amount = fields.Float('Discount Amount', readonly=True)

    order_id = fields.Many2one('sale.order', 'Order #', readonly=True)

    price_unit = fields.Float('Product Sale Value')
    standard_price = fields.Float(string="Product Cost value")
    profit = fields.Float(string="Profit")
    profitability = fields.Float(string="Profitability")
    return_qty = fields.Float(string=' Qty Returned')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        # self.product_id.type !='service'
        select_ = """
                min(l.id) as id,
                l.product_id as product_id,
                sum(l.qty_delivered*(l.price_unit -(ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty)) as profit,
                sum((l.qty_delivered - l.return_qty) * ((l.price_unit - ((ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty)) * 100)/CASE COALESCE (((ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty), 0) WHEN 0 THEN 1.0 ELSE (l.qty_delivered - l.return_qty)* ((ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty) END) as profitability,
                t.uom_id as product_uom,
                sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
                sum(l.return_qty) as return_qty,
                sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
                sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
                sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as price_total,
                sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as price_subtotal,
                sum(l.untaxed_amount_to_invoice / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as untaxed_amount_to_invoice,
                sum(l.untaxed_amount_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as untaxed_amount_invoiced,
                sum((ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty) as standard_price,
                count(*) as nbr,
                s.name as name,
                s.date_order as date,
                s.confirmation_date as confirmation_date,
                s.state as state,
                s.partner_id as partner_id,
                s.user_id as user_id,
                s.company_id as company_id,
                extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                t.categ_id as categ_id,
                s.pricelist_id as pricelist_id,
                s.analytic_account_id as analytic_account_id,
                s.team_id as team_id,
                p.product_tmpl_id,
                partner.country_id as country_id,
                partner.commercial_partner_id as commercial_partner_id,
                sum(l.price_unit) as price_unit,
                s.id as order_id
            """
        #sum((l.qty_delivered - l.return_qty) * ((l.price_unit - t.standard_price) * 100)/CASE COALESCE (t.standard_price, 0) WHEN 0 THEN 1.0 ELSE (l.qty_delivered - l.return_qty)* t.standard_price END) as profitability,
        # sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight, sum((l.qty_delivered - l.return_qty) * ((l.price_unit -t.standard_price) *100) / t.standard_price) as profitability,               #
        # sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume,
        # l.discount as discount,
        # sum((l.price_unit * l.discount / 100.0 / CASE COALESCE(s.currency_rate, 0)WHEN0THEN 1.0ELSEs.currency_rateEND)) as discount_amount,
        # sum((l.qty_delivered - l.return_qty) * ((l.price_unit - ((ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty)) * 100)/CASE COALESCE (((ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty), 0) WHEN 0 THEN 1.0 ELSE (l.qty_delivered - l.return_qty)* ((ip.value_float*l.qty_delivered/u.factor*u2.factor)::decimal(16,2)/l.product_uom_qty) END) as profitability,
        #        t.uom_id as product_uom,


        for field in fields.values():
            select_ += field

        from_ = """
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner partner on s.partner_id = partner.id
                            left join product_product p on (l.product_id=p.id) 
                                left join product_template t on (p.product_tmpl_id=t.id)
                                 LEFT JOIN ir_property ip ON (ip.name='standard_price' AND ip.res_id=CONCAT('product.product,',p.id) AND ip.company_id=s.company_id)
                        left join uom_uom u on (u.id=l.product_uom)
                        left join uom_uom u2 on (u2.id=t.uom_id)
                        left join product_pricelist pp on (s.pricelist_id = pp.id)
                    %s
            """ % from_clause

        groupby_ = """
                l.product_id,
                l.order_id,
                t.uom_id,
                t.categ_id,
                l.price_unit,
                l.profit,
                l.profitability,
                l.return_qty,
                s.name,
                t.standard_price,
                s.date_order,
                s.confirmation_date,
                s.partner_id,
                s.user_id,
                s.state,
                s.company_id,
                s.pricelist_id,
                s.analytic_account_id,
                s.team_id,
                p.product_tmpl_id,
                partner.country_id,
                partner.commercial_partner_id,
              
                s.id %s
        """ % (groupby)
            # ,  l.discount,
        return '%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        print("self._table====",self._table)
        print("_table===qqqq", self._query())
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))



class SaleOrderReportProforma(models.AbstractModel):
    _inherit = 'report.sale.report_saleproforma'
    _description = 'Proforma Report'

    @api.multi
    def _get_report_values(self, docids, data=None):

        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'proforma': True
        }


