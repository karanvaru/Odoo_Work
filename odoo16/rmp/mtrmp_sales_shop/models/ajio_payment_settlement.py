from odoo import models,fields,api

class AjioPaymentSettlement(models.Model):
    _name = 'ajio.payment.settlement'
    _description = 'ajio Payment Settlement'

    order_id = fields.Many2one('sale.order', 'Order ID')
    sales_shop_id = fields.Many2one('sale.shop')
    # product_id = fields.Many2one('product.product')

    journey_type = fields.Char('Journey Type')
    clearing_doc_no = fields.Char('Clearing doc no')
    clearing_date = fields.Char('Clearing date')
    expected_Settlement_date = fields.Char('Expected settlement date')
    internal_document_no = fields.Char('Internal Document no')
    forward_po_number = fields.Char('Forward PO Number')
    forward_po_date = fields.Char('Forward PO date')
    invoice_number = fields.Char('Invoice Number')
    invoice_date = fields.Char('Invoice Date')
    order_no = fields.Char('Order No')
    order_date = fields.Char('Order Date')
    awb_no = fields.Char('AWB No')
    shipment_no = fields.Char('Shipment No')
    value = fields.Char('Value')
    status = fields.Char('Status')
    credit_note_no = fields.Char('Credit Note No')
    delivery_challan_number = fields.Char('Delivery Challan Number')
    delivery_challan_date = fields.Char('Delivery Challan date')
    pob_id = fields.Char('POB ID')
    fulfilment_type = fields.Char('Fulfillment type')









