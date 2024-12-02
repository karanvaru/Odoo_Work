from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError



class ResPartnerInherited(models.Model):
    _inherit = "res.partner"

    total_canisters_count = fields.Integer('Total Canisters Count')
    canisters_delivered = fields.Integer('Canisters Delivered')
    canisters_reservered = fields.Integer('Canisters Reserved')
    remaining_canisters = fields.Integer('Remaining Canisters')

    sales_of_medicine_ids = fields.One2many('sale.order','partner_id',string="Sales Of Medicine",domain="[('partner_id', '=', id)]")

class ProductTeamplte(models.Model):
    _inherit = "product.template"
    
    is_canister = fields.Boolean(string='Is Canister', default=True)
    canister_id = fields.Many2one('product.product','Canister Product Id',domain=[('type', '=', 'product'), ('product_tmpl_id.type', '=', 'canister')])
    # canister_id = fields.Many2one(
    #     'product.template',
    #     string='Canister',
    #     domain="[('is_canister', '=', True)]",
    # )
    type = fields.Selection(
        selection_add=[('canister', 'Canister'),
                       ('medicine', 'Medicine')])   
    
class SaleOrder(models.Model):
    _inherit = "sale.order"

    medicine_product_id = fields.Many2one('product.template', string='Medicine Product')
    medicine_quantity = fields.Float("Total Medicine Quantity", compute='_compute_medicine_quantity')

    @api.multi
    def check_canisters(self):
        medicine_product = self.medicine_product_id
        if not medicine_product:
            raise UserError("Please select a medicine product.")

        canister_product = medicine_product.canister_id

        if not canister_product:
            raise UserError("No canister associated with the selected medicine.")

        # Calculate the quantity of canisters required based on the sale order line
        canisters_required = sum(line.product_id == canister_product for line in self.order_line)

        # Check the availability of canisters
        canisters_available = canisters_required <= canister_product.qty_available

        if canisters_available:
            raise UserError("Canisters are available.")
        else:
            # Display a wizard or pop-up to create a Manufacturing Order
            return {
                'name': 'Create Manufacturing Order',
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_mode': 'form',
                'view_id': self.env.ref('mrp.mrp_production_form_view').id,
                'target': 'new',
                'context': {'default_canister_product_id': canister_product.id},
            }
    def create_manufacturing_order(self):
        canister_product = self.medicine_product_id.canister_id

        canisters_required = sum(line.product_id == canister_product for line in self.order_line)

        manufacturing_order = self.env['mrp.production'].create({
            'product_id': canister_product.id,
            'product_uom_id': canister_product.uom_id.id,
            'product_qty': canisters_required,
            'origin': self.name,
            'state': 'draft',
        })

        return {
            'name': 'Manufacturing Order Created',
            'type': 'ir.actions.act_window.message',
            'message': f"Manufacturing Order '{manufacturing_order.name}' created with {canisters_required} canisters.",
            'target': 'new',
        }
    

    @api.multi
    def action_check_canisters(self):
        canisters_available = True 
        if not canisters_available:
            raise ValidationError(_("Canisters are not available. You need to create a Manufacturing Order."))
    
    @api.multi
    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}  

    @api.multi
    def action_confirm(self):
       for order in self:
            canisters_available = True 
            medicine_quantity = 0 

            if canisters_available:
                canister_product_id = 1 
                if canister_product_id:
                    self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': canister_product_id,
                        'product_uom_qty': medicine_quantity,
                        'price_unit': 0.0, 
                    })
            if order.mo_id:
                if order.mo_id.state == 'done' and order.mo_id.product_qty >= order.medicine_quantity:
                    canisters_needed = order.medicine_quantity 
                    canisters_available = order.mo_id.product_qty

                    if canisters_needed <= canisters_available:
                        super(SaleOrder, order).action_confirm
                    else:
                        raise ValidationError(_("Not enough canisters are available for the added Medicines in the SO line."))
                else:
                    raise ValidationError(_("MO is not in the 'Done' state or has insufficient availability."))
            else:
                raise ValidationError(_("No Manufacturing Order (MO) associated with this Sale Order."))

      
    
    def _compute_medicine_quantity(self):
        self.medicine_quantity = sum(self.order_line.filtered(lambda line: line.product_id.type == 'product').mapped('product_uom_qty'))


        