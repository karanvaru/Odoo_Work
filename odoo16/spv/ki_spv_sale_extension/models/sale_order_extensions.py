from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    maker_id = fields.Many2one(
        'res.partner',
        string="Maker"
    )


# self.update({"members_ids": [(6, 0, self.team_id.team_members_ids.ids)]})

class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    warranty_detail = fields.Html(
        'Warranty Detail'
    )
    tarrif_type = fields.Selection([
        ('residential', 'Residential'),
        ('corporate', 'Corporate'),
        ('industrial', 'Industrial')],
        string="Tarrif Type"
    )
    location = fields.Char(
        string="Location"
    )
    distributor_id = fields.Many2one(
        'res.partner',
        string="Discom"
    )
    chanel_partner = fields.Many2one(
        'res.partner',
        string="Chanel partner"
    )
    item_ids = fields.One2many(
        'sale.order.item.lines',
        'sale_order_id'
    )
    saving_roi_ids = fields.One2many(
        'saving.roi.lines',
        'sale_order_id',
        store=True,
        compute="_compute_saving_roi_lines"
    )
    payback_ids = fields.One2many(
        'sale.payback.lines',
        'sale_order_id'
    )
    payment_schedule_ids = fields.One2many(
        'sale.payment.schedule',
        'sale_order_id'
    )
    total_saving_ids = fields.One2many(
        'total.saving',
        'sale_order_id',
        store=True,
        compute="_compute_total_saving_ids"
    )
    pv_note = fields.Text(
        string="Note"
    )
    document_required_for_application = fields.Many2many(
        'sale.document.types',
        string="Documents Required For Application"
    )
    proposal_subject = fields.Char(
        string="Proposal Subject"
    )
    proposal_subject_2 = fields.Char(
        string="Proposal Subject 2"
    )
    subsidy = fields.Monetary(
        string="Subsidy",
        compute="_compute_subsidy"
    )
    net_meter_charges = fields.Float(
        string="Net Meter Charges"
    )
    extra_charges = fields.Float(
        string="Extra Charges"
    )
    subsidy_rate_kw = fields.Monetary(
        string="Subsidy Rate/KW",
        compute="_compute_subsidy_rate_kw"
    )

    total_saving_first_year = fields.Monetary(
        string="Total Saving 1st Year",
        compute="_compute_total_saving"
    )
    total_saving_second_year = fields.Monetary(
        string="Total Saving 2st Year",
        compute="_compute_total_saving"
    )
    total_saving_third_year = fields.Monetary(
        string="Total Saving 3st Year",
        compute="_compute_total_saving"
    )
    total_saving_four_year = fields.Monetary(
        string="Total Saving Fourth Year",
        compute="_compute_total_saving"
    )

    total_payment = fields.Float(
        string="Total Payment(In %)",
        compute="_compute_payment_schedule"
    )
    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_payment_schedule"
    )
    total_process_time = fields.Integer(
        string="Total Process Time(Days)",
        compute="_compute_payment_schedule"
    )

    net_cash_first_year = fields.Monetary(
        string="Net Cash 1st Year",
        compute="_compute_net_cash"
    )
    net_cash_second_year = fields.Monetary(
        string="Net Cash 2st Year",
        compute="_compute_net_cash"
    )
    net_cash_third_year = fields.Monetary(
        string="Net Cash 3st Year",
        compute="_compute_net_cash"
    )
    net_cash_four_year = fields.Monetary(
        string="Net Cash Fourth Year",
        compute="_compute_net_cash"
    )

    solar_plant_cost = fields.Monetary(
        string="Solar Plant Cost",
        compute="_compute_solar_plant_cost"
    )

    @api.constrains('payment_schedule_ids', 'order_line')
    def _check_o2m_field(self):
        if self.total_payment > 100:
            raise ValidationError(_('Warning! Total Payment Not More than 100%'))

    @api.onchange('order_line')
    def warning(self):
        if len(self.order_line) > 1:
            raise UserError(_('Warning! You cannot add multiple lines.'))

    def _compute_solar_plant_cost(self):
        self.solar_plant_cost = self.amount_total - self.subsidy + self.net_meter_charges + self.extra_charges

    @api.depends('order_line')
    def _compute_total_saving_ids(self):
        for rec in self:
            total_save = []
            first_year_40 = rec.solar_plant_cost * 0.4
            first_year_30 = first_year_40 * 0.3
            first_year_bill = 8 * rec.order_line.product_uom_qty * 4.2 * 360

            second_year_40 = (rec.solar_plant_cost - first_year_40) * 0.4
            second_year_30 = second_year_40 * 0.3
            second_year_bill = first_year_bill

            third_year_40 = (rec.solar_plant_cost - second_year_40) * 0.4
            third_year_30 = third_year_40 * 0.3
            third_year_bill = second_year_bill

            four_year_40 = (rec.solar_plant_cost - first_year_40 - second_year_40 - third_year_40) * 0.4
            four_year_30 = four_year_40 * 0.3
            four_year_bill = third_year_bill

            list_40 = []
            list_40.append(first_year_40)
            list_40.append(second_year_40)
            list_40.append(third_year_40)
            list_40.append(four_year_40)

            list_30 = []
            list_30.append(first_year_30)
            list_30.append(second_year_30)
            list_30.append(third_year_30)
            list_30.append(four_year_30)

            list_bill = []
            list_bill.append(first_year_bill)
            list_bill.append(second_year_bill)
            list_bill.append(third_year_bill)
            list_bill.append(four_year_bill)

            saving_dict = {
                "Depreciation 40% of book value": list_40,
                "Tax benefit @30% (A)": list_30,
                "Saving in Electricity Bill (B)": list_bill,
            }
            for key, value in saving_dict.items():
                values = {
                    'particular': key,
                    'first_year': value[0],
                    'second_year': value[1],
                    'third_year': value[2],
                    'four_year': value[3],
                }
                total_save.append((0, 0, values))
            rec.write({'total_saving_ids': [(5, 0, 0)]})
            rec.total_saving_ids = total_save

    @api.depends('order_line')
    def _compute_saving_roi_lines(self):
        for rec in self:
            saving_roi_line = []
            total_inv = rec.solar_plant_cost
            rate = 8
            unit_gen = rec.order_line.product_uom_qty * 4.2 * 360
            year_bill_save = rate * unit_gen
            save_in_25 = year_bill_save * 25
            if year_bill_save == 0:
                pay_back_period = 0
            else:
                pay_back_period = total_inv / year_bill_save
            if total_inv == 0:
                r_o_i = 0
            else:
                r_o_i = year_bill_save / total_inv
            saving_dict = {
                "Total Investment (Rs.) (A)": total_inv,
                "Existing Rate per Unit (Rs./unit) (B)": rate,
                "Units generation from solar project (approx) (C)": unit_gen,
                "Yearly bill Savings in (Rs.) (E = B x C - D)": year_bill_save,
                "Total Savings in 25 years(Rs.) (E x 25)": save_in_25,
                "Pay back period in Years without depreciation benefit (A / D)": pay_back_period,
                "R.O.I (Return on Investment in %) without depreciation benefit (D / A)%": r_o_i,
            }
            for key, value in saving_dict.items():
                val = {
                    'name': key,
                    'amount': value
                }
                saving_roi_line.append((0, 0, val))
            rec.write({'saving_roi_ids': [(5, 0, 0)]})
            rec.saving_roi_ids = saving_roi_line

    def _compute_net_cash(self):
        self.net_cash_first_year = 0
        self.net_cash_second_year = 0
        self.net_cash_third_year = 0
        self.net_cash_four_year = 0
        self.net_cash_first_year = self.total_saving_first_year - self.solar_plant_cost
        self.net_cash_second_year = self.net_cash_first_year + self.total_saving_second_year
        self.net_cash_third_year = self.net_cash_second_year + self.total_saving_third_year
        self.net_cash_four_year = self.net_cash_third_year + self.total_saving_four_year

    @api.model
    def default_get(self, fields):
        result = super(InheritSaleOrder, self).default_get(fields)
        # saving_roi_name = ['Total Investment (Rs.) (A)', 'Existing Rate per Unit (Rs./unit) (B)',
        #                    'Units generation from solar project (approx) (C)',
        #                    'Yearly bill Savings in (Rs.) (E = B x C - D)', 'Total Savings in 25 years(Rs.) (E x 25)',
        #                    'Pay back period in Years without depreciation benefit (A / D)',
        #                    'R.O.I (Return on Investment in %) without depreciation benefit (D / A)%']
        # saving_name = []
        # for name in saving_roi_name:
        #     values = {
        #         'name': name,
        #     }
        #     saving_name.append((0, 0, values))
        # total_saving_particular = ['Depreciation 40% of book value', 'Tax benefit @30% (A)',
        #                            'Saving in Electricity Bill (B)']
        # particular = []
        # for saving in total_saving_particular:
        #     values = {
        #         'particular': saving,
        #     }
        #     particular.append((0, 0, values))
        sale_t_c = self.env['res.config.settings'].sudo().search([])
        warranty_detail = ''
        for rec in sale_t_c:
            warranty_detail = rec.warranty_detail
        result.update({
            # 'saving_roi_ids': saving_name,
            # 'total_saving_ids': particular,
            'warranty_detail': warranty_detail,
        })
        return result

    # @api.onchange('amount_total', 'total_saving_ids', 'order_line')
    # def onchange_first_year(self):
    #     print("========================= onchange_first_year")
    #     # self.first_year = 0
    #     first_year = []
    #     first_year_40 = self.amount_total * 0.4
    #     first_year_30 = first_year_40 * 0.3
    #     first_year.append(first_year_40)
    #     first_year.append(first_year_30)
    #     first_year_list = []
    #     for rec in first_year:
    #         values = {
    #             'first_year': rec,
    #         }
    #         first_year_list.append((values))
    #     self.update({
    #         'total_saving_ids': (6, 0, first_year_list)
    #     })

    # print("======================= first_year", first_year)

    def _compute_payment_schedule(self):
        self.total_payment = 0
        self.total_amount = 0
        self.total_process_time = 0
        for rec in self.payment_schedule_ids:
            self.total_payment += rec.payment
            self.total_amount += rec.amount
            self.total_process_time += rec.process_time

    def _compute_total_saving(self):
        self.total_saving_first_year = 0
        self.total_saving_second_year = 0
        self.total_saving_third_year = 0
        self.total_saving_four_year = 0
        total_saving_first_year = 0
        total_saving_second_year = 0
        total_saving_third_year = 0
        total_saving_four_year = 0
        first_list = []
        second_list = []
        third_list = []
        four_list = []
        for rec in self.total_saving_ids:
            first_list.append(rec.first_year)
            second_list.append(rec.second_year)
            third_list.append(rec.third_year)
            four_list.append(rec.four_year)
            total_saving_first_year += rec.first_year
            total_saving_second_year += rec.second_year
            total_saving_third_year += rec.third_year
            total_saving_four_year += rec.four_year
        self.total_saving_first_year = total_saving_first_year - first_list[0]
        self.total_saving_second_year = total_saving_second_year - second_list[0]
        self.total_saving_third_year = total_saving_third_year - third_list[0]
        self.total_saving_four_year = total_saving_four_year - four_list[0]

    def _compute_subsidy(self):
        self.subsidy = 0
        for rec in self.order_line:
            if rec.product_uom_qty <= 3.0:
                self.subsidy = self.subsidy_rate_kw * rec.product_uom_qty * 0.4
            elif rec.product_uom_qty > 3.0 and rec.product_uom_qty <= 10.0:
                self.subsidy = self.subsidy_rate_kw * rec.product_uom_qty * 0.2

    def _compute_subsidy_rate_kw(self):
        self.subsidy_rate_kw = 0
        if self.tarrif_type == 'residential':
            for rec in self.order_line:
                if rec.product_uom_qty <= 2:
                    self.subsidy_rate_kw = 49093
                elif rec.product_uom_qty <= 3:
                    self.subsidy_rate_kw = 47818
                elif rec.product_uom_qty <= 6:
                    self.subsidy_rate_kw = 46647
                elif rec.product_uom_qty <= 10:
                    self.subsidy_rate_kw = 46089.6
                elif rec.product_uom_qty <= 25:
                    self.subsidy_rate_kw = 43512
                elif rec.product_uom_qty <= 50:
                    self.subsidy_rate_kw = 43512
                else:
                    self.subsidy_rate_kw = 37212

        elif self.tarrif_type == 'corporate':
            for rec in self.order_line:
                if rec.product_uom_qty <= 2:
                    self.subsidy_rate_kw = 49093
                elif rec.product_uom_qty <= 3:
                    self.subsidy_rate_kw = 47796
                elif rec.product_uom_qty <= 6:
                    self.subsidy_rate_kw = 46647
                elif rec.product_uom_qty <= 10:
                    self.subsidy_rate_kw = 46089.6
                elif rec.product_uom_qty <= 25:
                    self.subsidy_rate_kw = 43512
                elif rec.product_uom_qty <= 50:
                    self.subsidy_rate_kw = 42675
                else:
                    self.subsidy_rate_kw = 38350

    @api.onchange('order_line', 'tarrif_type')
    def onchange_unite_price(self):
        if self.tarrif_type == 'residential':
            for rec in self.order_line:
                if rec.product_uom_qty <= 2:
                    rec.price_unit = 51210
                elif rec.product_uom_qty <= 4:
                    rec.price_unit = 48934
                elif rec.product_uom_qty <= 5:
                    rec.price_unit = 47796
                elif rec.product_uom_qty <= 6:
                    rec.price_unit = 46658
                elif rec.product_uom_qty <= 10:
                    rec.price_unit = 46089.6
                elif rec.product_uom_qty <= 25:
                    rec.price_unit = 44115.7
                elif rec.product_uom_qty <= 50:
                    rec.price_unit = 43813
                else:
                    rec.price_unit = 37212.6
        elif self.tarrif_type == 'corporate':
            for rec in self.order_line:
                if rec.product_uom_qty <= 2:
                    rec.price_unit = 51210
                elif rec.product_uom_qty <= 5:
                    rec.price_unit = 47796
                elif rec.product_uom_qty <= 6:
                    rec.price_unit = 46658
                elif rec.product_uom_qty <= 10:
                    rec.price_unit = 46089
                elif rec.product_uom_qty <= 25:
                    rec.price_unit = 43813
                elif rec.product_uom_qty <= 50:
                    rec.price_unit = 42675
                else:
                    rec.price_unit = 38350

    @api.onchange('partner_id')
    def onchange_customer(self):
        for rec in self:
            rec.location = rec.partner_id.city

    # @api.model
    # def create(self, vals_list):
    #     res = super(InheritSaleOrder, self).create(vals_list)
    #     sale_t_c = self.env['res.config.settings'].sudo().search([])
    #     for rec in sale_t_c:
    #         res['warranty_detail'] = rec.warranty_detail
    #     return res


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warranty_detail = fields.Html('Warranty Detail')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ki_spv_sale_extension.warranty_detail', self.warranty_detail)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            warranty_detail=ICPSudo.get_param('ki_spv_sale_extension.warranty_detail'),
        )
        return res


class SaleOrderItemLines(models.Model):
    _name = 'sale.order.item.lines'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )
    name = fields.Text(
        string="Description",
        store=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure"
    )
    qty = fields.Float(
        string="Quantity"
    )
    maker_id = fields.Many2one(
        'res.partner',
        string="Maker"
    )

    @api.onchange('product_id')
    def onchange_items(self):
        for rec in self:
            rec.maker_id = rec.product_id.maker_id.id
            rec.uom_id = rec.product_id.uom_id.id
            rec.name = rec.product_id.display_name
            # rec.name = rec.product_id.get_product_multiline_description_sale()


class SavingRoiLines(models.Model):
    _name = 'saving.roi.lines'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
    name = fields.Char(
        string="Name"
    )
    amount = fields.Float(
        string="Amount",
        # compute='_compute_amount'
    )

    # def _compute_amount(self):
    #     self.amount = 0
    #     amount_list = []
    #     total_inv = self.sale_order_id.amount_total
    #     rate = 8
    #     unit_gen = self.sale_order_id.order_line.product_uom_qty * 4.2 * 360
    #     year_bill_save = rate * unit_gen
    #     save_in_25 = year_bill_save * 25
    #     pay_back_period = total_inv / year_bill_save
    #     r_o_i = year_bill_save / total_inv
    #     amount_list.append(total_inv)
    #     amount_list.append(rate)
    #     amount_list.append(unit_gen)
    #     amount_list.append(year_bill_save)
    #     amount_list.append(save_in_25)
    #     amount_list.append(pay_back_period)
    #     amount_list.append(r_o_i)
    #     for rec in self:
    #         self.amount = [(6, 0, amount_list)]
    #     # for rec in amount_list:
    #     #     for res in self:
    #     #         res.update({"amount": (6, 0, rec)})
    #     print("====================== amount_list 399", amount_list)


class SalePaybackLines(models.Model):
    _name = 'sale.payback.lines'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
    year = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10')],
        string='Year',
    )
    amount = fields.Float(
        string="Amount",
        compute="_compute_amount"
    )

    def _compute_amount(self):
        self.amount = 0
        for rec in self:
            rec.amount = 8 * self.sale_order_id.order_line.product_uom_qty * 4.2 * 360

    # @api.model
    # def default_get(self, fields):
    #     result = super(SalePaybackLines, self).default_get(fields)
    #     amount = 8 * self.sale_order_id.order_line.product_uom_qty * 4.2 * 360
    #     print("================= 444 amount", amount)
    #     result.update({'amount': amount})
    #     return result


class SalePaymentSchedule(models.Model):
    _name = 'sale.payment.schedule'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
    payment_stage = fields.Char(
        string="Payment Stage"
    )
    payment = fields.Float(
        string="Payment(In %)"
    )
    amount = fields.Float(
        string="Amount",
        compute="_compute_amount"
    )
    process_time = fields.Integer(
        string="Process Time(Days)"
    )

    # @api.model
    # def default_get(self, fields):
    #     vals = super(SalePaymentSchedule, self).default_get(fields)
    #     active_id = self._context.get('active_id')
    #     picking_obj = self.env['sale.order']
    #     picking = picking_obj.browse(active_id)
    #     print("======================= picking", picking)
    #     # print("===================== self.sale_order_id.total_payment", self.sale_order_id.total_payment)
    #     return vals

    def _compute_amount(self):
        solar_plant_cost = self.sale_order_id.solar_plant_cost
        self.amount = 0
        for rec in self:
            rec.amount = solar_plant_cost * rec.payment / 100

    # @api.model_create_multi
    # def create(self, vals_list):
    #     # active_id = self._context.get('active_id')
    #     # sale_order_obj = self.env['sale.order']
    #     # sale_order = sale_order_obj.browse(active_id)
    #     # print("================== sale_order id", sale_order)
    #     # print("===================== vals_list", vals_list)
    #     # print("===================== self.sale_order_id.total_payment", self.sale_order_id.total_payment)
    #     # print("==================== create")
    #     # sale_id = self.env['sale.order'].sudo().search(['id', '=', 'sale_order_id.id'])
    #     # print("=================sale_id ", sale_id)
    #     print('======================== self.sale_order_id', self.sale_order_id.id)
    #     if self.sale_order_id.total_payment > 100:
    #         print("================= if")
    #         raise ValidationError(_("The model name"))
    #     return super(SalePaymentSchedule, self).create(vals_list)


class TotalSaving(models.Model):
    _name = 'total.saving'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
    particular = fields.Char(
        string="Particular"
    )
    first_year = fields.Float(
        string="1st Year",
        # compute="_compute_total_save_year"
    )
    second_year = fields.Float(
        string="2st Year",
        # compute="_compute_total_save_year"
    )
    third_year = fields.Float(
        string="3st Year",
        # compute="_compute_total_save_year"
    )
    four_year = fields.Float(
        string="Fourth Year",
        # compute="_compute_total_save_year"
    )

    # def _compute_total_save_year(self):
    #     # self.first_year = 0
    #     # if self[0]:
    #     #     print('=====================if rec', self)
    #     #     self.first_year = self.sale_order_id.amount_total * 0.4
    #     self.first_year = 0
    #     self.second_year = 0
    #     self.third_year = 0
    #     self.four_year = 0
    #     # list = []
    #     first_year = []
    #     first_year_40 = self.sale_order_id.amount_total * 0.4
    #     first_year_30 = first_year_40 * 0.3
    #     first_year_bill = 8 * self.sale_order_id.order_line.product_uom_qty * 4.2 * 360
    #     first_year.append(first_year_40)
    #     first_year.append(first_year_30)
    #     first_year.append(first_year_bill)
    #     print("====================== first_year", first_year)
    #
    #     second_year = []
    #     second_year_40 = (self.sale_order_id.amount_total - first_year_40) * 0.4
    #     second_year_30 = second_year_40 * 0.3
    #     second_year_bill = first_year_bill
    #     second_year.append(second_year_40)
    #     second_year.append(second_year_30)
    #     second_year.append(second_year_bill)
    #     print("====================== second_year", second_year)
    #
    #     third_year = []
    #     third_year_40 = (self.sale_order_id.amount_total - second_year_40) * 0.4
    #     third_year_30 = third_year_40 * 0.3
    #     third_year_bill = second_year_bill
    #     third_year.append(third_year_40)
    #     third_year.append(third_year_30)
    #     third_year.append(third_year_bill)
    #     print("====================== third_year", third_year)
    #
    #     four_year = []
    #     four_year_40 = (self.sale_order_id.amount_total - first_year_40 - second_year_40 - third_year_40) * 0.4
    #     four_year_30 = four_year_40 * 0.3
    #     four_year_bill = third_year_bill
    #     four_year.append(four_year_40)
    #     four_year.append(four_year_30)
    #     four_year.append(four_year_bill)
    #     print("====================== four_year", four_year)

    # for rec in self:
    # lines = [(5, 0, 0)]
    # for line in first_year:
    #     val = {
    #         'first_year': line
    #     }
    #     lines.append((0, 0, val))
    #     for rec in self:
    #         rec.first_year = val['first_year']
    # rec = lines

    # for l in first_year:
    #     print("======================= l", l)
    #     for rec in self:
    #         print("================ rec[]", rec)
    #         rec.first_year = l
    #
    #         print("=============== rec", rec)

    # particular = []
    # for saving in first_year:
    #     values = {
    #         'particular': saving,
    #     }
    #     particular.append((0, 0, values))
    # sale_t_c = self.env['res.config.settings'].sudo().search([])
    # self.update({
    #     'first_year': first_year,
    # })

    # for res in self:
    #     print("====================== res", res)
    # print("====================== index", index)
    # res.first_year = first_year[0]
    # for rec in first_year:
    #     self.first_year = rec

    # def _compute_first_year(self):
    #     self.first_year = 0
    #     first_year_40 = self.sale_order_id.amount_total * 0.4
    #     first_year_30 = first_year_40 * 0.3
    #     list = [float(first_year_40), float(first_year_30)]
    #     first_year = []
    #     print("====================== list", list)
    #     for l in list:
    #         values = {
    #             'first_year': l,
    #         }
    #         first_year.append((0, 0, values))
    #     self.first_year = first_year
    # for rec in self:
    #     for l in list:
    #         rec.first_year = l
    # self.first_year[0] = 100
    # self.first_year[1] = 200
    # self.first_year[2] = 300

# particular = []
# for saving in total_saving_particular:
#     values = {
#         'particular': saving,
#     }
#     particular.append((0, 0, values))
# sale_t_c = self.env['res.config.settings'].sudo().search([])
# result.update({
#     'saving_roi_ids': saving_name,
#     'total_saving_ids': particular,
#     'warranty_detail': sale_t_c.warranty_detail,
# })

# @api.onchange('sale_order_id.order_line')
# def onchange_first_year(self):
#     print("========================= onchange_first_year")
#     self.first_year = 0
#     list = []
#     first_year = []
#     first_year_40 = self.sale_order_id.amount_total * 0.4
#     first_year_30 = first_year_40 * 0.3
