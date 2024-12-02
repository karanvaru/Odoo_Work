from odoo import api, fields, models, _


class HelpdeskFields(models.Model):
    _inherit = "helpdesk.ticket"
    _order = 'create_date desc'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    contract_id = fields.Many2one(
        'contract.contract',
        string='Contract',
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        readonly=True,
    )
    closed_date = fields.Datetime(
        copy=False,
        readonly=True,
    )
    assigned_date = fields.Datetime(
        copy=False,
        readonly=True,
    )
    work_phone = fields.Char(
        string='Phone Number',
        store=True,
        copy=False,
    )
    ticket_line_ids = fields.One2many(
        'helpdesk.ticket.line',
        'ticket_id',
        string="Ticket Lines"
    )
    ticket_id = fields.Many2one(
        'helpdesk.ticket',
    )
    issue_type = fields.Selection(
        [
            ('refill', 'Refill'),
            ('other', 'Other')
        ],
        string='Issue Type'
    )
    department = fields.Char(
        string='Department',
        readonly=True
    )
    location_id = fields.Many2one(
        'res.partner',
        string="Location",
        readonly=True,
    )
    product_category_id = fields.Many2one(
        'product.category',
        string="Product Category",
        readonly=True,
    )
    asset_number = fields.Char(
        string="Asset Number",
        readonly=True,
    )
    mobile_number = fields.Char(
        string='Mobile',
    )

    # count = fields.Integer(
    #     string='Count'
    # )
    # partner_id = fields.Many2one(
    #     'res.partner',
    #     string='Contact',
    #     readonly=True,
    #     copy=False,
    # )

    # @api.onchange('user_id')
    # def _onchange_user_id(self):
    #     print('sssssssssssssssss', self.user_id)
    #     if self.user_id:
    #         print('sssssssssssssssss', self.stage_id)
    #         self.stage_id.name = 'Assign'

    @api.onchange('product_id')
    def _onchange_contract_id(self):
        # return {'domain': {'contract_id': [('id', '=', self.product_id.current_contract_id.id),
        #                                    ('state', '=', 'active')]}}
        if self.product_id:
            # if self.contract_id.state == 'active':
            self.contract_id = self.product_id.current_contract_id.id
            self.partner_id = self.contract_id.partner_id.id
            self.location_id = self.contract_id.partner_shipping_id.id
            # self.partner_name = self.contract_id.partner_id.name
            self.department = self.contract_id.contract_line_fixed_ids.filtered(lambda line: line.product_id == self.product_id).department
            self.product_category_id = self.product_id.categ_id.id
            self.asset_number = self.contract_id.contract_line_fixed_ids.filtered(lambda line: line.product_id == self.product_id).default_code

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self.env.user.has_group('ki_contract_menu.group_smart_printer_customer_user'):
            args += [('create_uid', '=', self.env.user.id)]
        return super(HelpdeskFields, self)._search(args, offset, limit, order, count=count,
                                                   access_rights_uid=access_rights_uid)

    def write(self, vals):
        for _ticket in self:
            now = fields.Datetime.now()
            stage_close = self.env['helpdesk.ticket.stage'].search([('name', 'in', ['Call Close', 'Cancelled'])])
            if stage_close:
                vals["closed_date"] = now
        return super().write(vals)

    def action_refill_request(self):
        refill = self.env['refill.request'].create({
            'product_id': self.product_id.id,
            'ticket_id': self.id,
            'date': self.create_date,
        })
        act = self.env.ref('ki_contract_menu.refill_request_actions').read([])[0]
        act['domain'] = [('ticket_id', '=', self.id)]

        return act

    def action_open_refill_request(self):
        act = self.env.ref('ki_contract_menu.refill_request_actions').read([])[0]
        act['domain'] = [('ticket_id', '=', self.id)]
        # act['context'] = {'default_product_id': self.id}
        return act

    def action_open_in_out_register(self):
        act = self.env.ref('ki_contract_menu.product_register_action').read([])[0]
        act['domain'] = [('line_ids.ticket_id', '=', self.id)]
        return act


class HelpdeskTicketLines(models.Model):
    _name = "helpdesk.ticket.line"
    _description = "Helpdesk Ticket Line"

    ticket_id = fields.Many2one(
        'helpdesk.ticket',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Parts',
    )

    quantity = fields.Integer(
        string='Quantity',
    )


class HelpdeskCategory(models.Model):
    _inherit = 'helpdesk.ticket.category'

    type = fields.Selection(
        [
            ('printer', 'Printer'),
            ('cartridge', 'Cartridge'),
            ('parts', 'Parts')
        ],
        string='Type',
    )
