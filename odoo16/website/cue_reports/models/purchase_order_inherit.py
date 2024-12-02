from odoo import fields, models, api
from num2words import num2words


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order Inherit'

    declaration = fields.Html(
        string="Declaration",
    )

    # def amount_to_text(self, num):
    #     num = str(num)
    #     rupees = num2words(int(num.split(".")[0]))
    #     paisa = num2words(int(num.split(".")[1]))
    #     if paisa != 'zero':
    #         val = rupees + ' Rupees ' + paisa + ' Paisa Only'
    #     else:
    #         val = rupees + ' Rupees ' + ' Only'
    #     val = val.title()
    #     return val

    def amount_to_text(self, num):
        num = str(num)
        paisa = 'zero'
        rupees = num2words(int(num.split(".")[0]))
        if '1' in num:
            paisa = num2words(int(num.split(".")[1]))
        if paisa != 'zero':
            val = rupees + ' Rupees ' + paisa + ' Paisa Only'
        else:
            val = rupees + ' Rupees ' + ' Only'
        val = val.title()
        return val