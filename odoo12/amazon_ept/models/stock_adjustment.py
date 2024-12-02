from odoo import models,fields,api

class amazon_adjustment_reason_code(models.Model):
    _name="amazon.adjustment.reason.code"
    _description = "amazon.adjustment.reason.code"
    
    name=fields.Char("Name",required=True)
    type=fields.Selection([('-','-'),('+','+')])
    description=fields.Char("Description")
    long_description=fields.Text("Long Description")
    group_id=fields.Many2one("amazon.adjustment.reason.group",string="Group")
    counter_part_id=fields.Many2one("amazon.adjustment.reason.code",string="Counter Part")
    is_reimbursed = fields.Boolean("Is Reimbursed ?",default=False,help="Is Reimbursed?")
    
class amazon_adjustment_reason_group(models.Model):
    _name="amazon.adjustment.reason.group"
    _description = "amazon.adjustment.reason.group"
    
    @api.one
    def check_counter_part_group_or_not(self):
        is_counter_part_group=False
        for code in self.reason_code_ids:
            if code.counter_part_id:
                is_counter_part_group=True
                break
        self.is_counter_part_group=is_counter_part_group
            
    name=fields.Char("Name",required=True)
    is_counter_part_group=fields.Boolean(compute=check_counter_part_group_or_not,string="Is counter Part group")
    reason_code_ids=fields.One2many('amazon.adjustment.reason.code','group_id',string="Reason Codes") 

#comment by dhaval [16-1-2019]
#reason : field is already defined in Amazon FBA
# class stock_warehouse(models.Model):
#     _inherit="stock.warehouse"
#     
#     unsellable_location_id=fields.Many2one("stock.location",string="Dispotion Unsallable Location")

class amazon_stock_adjustment_config(models.Model):
    _name="amazon.stock.adjustment.config"
    _description="amazon.stock.adjustment.config"

    def _get_email_template(self):
        template=False
        try:
            template=self.env.ref('amazon_ept.email_template_amazon_stock_adjustment_email_ept')
        except:
            pass
        return template.id
        
    group_id=fields.Many2one("amazon.adjustment.reason.group",string="Group")
    seller_id=fields.Many2one("amazon.seller.ept",string="Seller")
    location_id=fields.Many2one("stock.location",string="Location")
    is_send_email=fields.Boolean("Is Send Email ?",default=False)
    email_template_id=fields.Many2one("mail.template",string="Email Template",default=_get_email_template)
    picking_type_id=fields.Many2one("stock.picking.type",string="Picking Type")

    _sql_constraints=[('amazon_stock_adjustment_unique_constraint','unique(group_id,seller_id)',"Group must be unique per seller")]
