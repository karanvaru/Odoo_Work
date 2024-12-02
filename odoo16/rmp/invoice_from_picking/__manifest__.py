# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice From Picking(Shipment/Delivery Order) Odoo",
    "version": "14.0.0.3",
    "depends": ['base', 'account', 'sale_management', 'stock', 'purchase', 'sale_stock'],
    "author": "BrowseInfo",
    "summary": "customer invoice from picking vendor invoices from Picking customer invoice from delivery order vendor bill from picking vendor bill from receipt invoice from Shipment invoice from Shipment Account invoice from picking single invoice from delivery order",
    'description': """
    
    Generate single invoice from multiple delivery order, Create single invoice from multiple shipment order, Single invoice for multiple orders, single invoice from Order, multiple delivery order generate single invoice, easy invoice from picking, invoice in picking
Generate single invoice from multiple delivery order, Create single invoice from multiple shipment order, Single invoice for multiple orders, single invoice from Orders, multiple delivery generate single invoice, easy invoice from picking.
invoice in picking, retrun invoice from picking, return invoice from shipment, return invoice from Delivery.
Picking from Customer Invoice
      Picking from Customer Invoice
      Invoice From Picking
      vendor invoices from Picking
      vendor invoices from Picking (Delivery Order/ Incoming Shipment
      vendor invoices from Incoming Shipment
      vendor invoices from Delivery Order
      invoices from Delivery Order
      invoices from Incoming Shipment
      invoice from Shipment
      Stock Move from Invoice
      Stock Picking from Invoice and Vendor Bill
      Stock Picking from Vendor Bill
      Picking from Vendor Bill
      Vendor Bill to Incoming Shipment
      invoice from Shipment
Account invoice from picking
invoice from stock fr    
Generate single invoice from multiple Delivery Order, Create single invoice from multiple Delivery Order, Single invoice for multiple Delivery Order, single invoice from Orders, multiple Picking generate single invoice, easy invoice from Delivery order
Generate single invoice from multiple Shipment, Create single invoice from multiple Shipment, Single invoice for multiple Shioment, single invoice from Picking, multiple shipment generate single invoice, easy invoice from incoming shipment
    Generate Single invoice from Multiple Picking ,generate invoice from delivery Order, generate invoice from picking, generate invoice from shipment.
    invoice by picking, invoice by delivery order, invoice by shipment
Gerar uma única fatura de vários pedidos de entrega, criar uma única fatura de vários pedidos de remessa, fatura única para vários pedidos, fatura única do pedido, vários pedidos de remessa geram fatura única, fatura fácil de picking, fatura na retirada
Gere uma fatura única a partir de vários pedidos de entrega, crie uma única fatura a partir de vários pedidos de remessa, fatura individual para vários pedidos, fatura única de pedidos, várias entregas geram fatura única, fatura fácil de picking.

    fatura na retirada, fatura da retirada da fatura, retorno da fatura da expedição, retorno da fatura da entrega.
    
Gere uma única fatura de vários pedidos, crie uma única fatura a partir de vários pedidos, uma única fatura para vários pedidos, uma única fatura de pedidos, vários picking geram uma única fatura, uma fatura fácil a partir de uma ordem de entrega
Gere uma única fatura de várias remessas, crie uma única fatura a partir de várias remessas, uma única fatura para vários itens, uma única fatura de retirada, várias remessas geram uma única fatura, fatura fácil a partir da remessa de entrada
    Gere uma única fatura a partir de uma seleção múltipla, gere uma fatura a partir da ordem de entrega, gere a fatura a partir do picking, gere a fatura a partir da remessa.
    fatura por picking, fatura por ordem de entrega, fatura por remessa

إنشاء فاتورة فردية من أمر تسليم متعدد ، إنشاء فاتورة واحدة من طلب شحن متعدد ، فاتورة واحدة لأوامر متعددة ، فاتورة واحدة من الطلب ، أمر تسليم متعدد توليد فاتورة واحدة ، فاتورة سهلة من الانتقاء ، فاتورة في قطف
إنشاء فاتورة واحدة من أمر تسليم متعدد ، إنشاء فاتورة واحدة من طلب شحن متعدد ، فاتورة واحدة لأوامر متعددة ، فاتورة واحدة من الطلبات ، تسليم متعدد توليد فاتورة واحدة ، فاتورة سهلة من قطف.

    فاتورة في قطف ، استرداد الفاتورة من التقاط ، الفواتير العودة من الشحن ، فاتورة العودة من التسليم.
    
إنشاء فاتورة فردية من أمر تسليم متعدد ، إنشاء فاتورة واحدة من أمر تسليم متعدد ، فاتورة واحدة لأمر تسليم متعدد ، فاتورة واحدة من الطلبات ، متعددة إختيار توليد فاتورة واحدة ، فاتورة سهلة من أمر التسليم
إنشاء فاتورة فردية من شحن متعدد ، إنشاء فاتورة واحدة من شحن متعدد ، فاتورة واحدة لعدة Shioment ، فاتورة واحدة من Picking ، شحن متعدد توليد فاتورة واحدة ، فاتورة سهلة من شحنة واردة
    توليد فاتورة واحدة من التقاط متعددة ، وتوليد فاتورة من التسليم النظام ، وتوليد فاتورة من قطف ، وتوليد الفاتورة من الشحن.
    فاتورة عن طريق اختيار ، فاتورة بواسطة أمر التسليم ، الفاتورة عن طريق الشحن
Générer une facture unique à partir d'un bon de livraison multiple, Créer une facture unique à partir de plusieurs commandes, Facture unique pour plusieurs commandes, Facture unique à partir de la commande, Bon de livraison multiple générer une facture unique, Facture facile à cueillir, Facture à la cueillette
Générer une facture unique à partir d'un bon de livraison multiple, Créer une facture unique à partir d'une commande d'expédition multiple, Facture unique pour plusieurs commandes, Facture unique des commandes, Livraison multiple générer une facture unique, Facture facile de la cueillette.

    Facturer à la cueillette, rétracter la facture de la cueillette, retourner la facture de l'expédition, retourner la facture de la livraison.
    
Générer une facture unique à partir de plusieurs ordres de livraison, Créer une facture unique à partir de plusieurs ordres de livraison, Facture unique pour plusieurs ordres de livraison, Facture unique des commandes, Facturation multiple générer une facture unique, Facture facile à partir du bon de livraison
Générer une facture unique à partir de plusieurs envois, Créer une facture unique à partir de plusieurs envois, Facture unique pour plusieurs shioments, facture unique à partir de prélèvement, plusieurs envois générer une facture unique, facture facile à partir de l'envoi entrant
    Générer une facture unique à partir de la cueillette multiple, générer la facture à partir de la commande, générer la facture à partir de la cueillette, générer la facture à partir de l'expédition.
    facture par prélèvement, facture par bon de livraison, facture par envoi

Genere una sola factura a partir de varias órdenes de entrega, cree una sola factura a partir de varias órdenes de envío, una sola factura para varias órdenes, una sola factura a partir de una orden, una orden de entrega múltiple genere una sola factura, una factura fácil para recoger, una factura para recoger
Genere una sola factura a partir de varias órdenes de entrega, cree una única factura a partir de varias órdenes de envío, una factura única para pedidos múltiples, una sola factura desde pedidos, una entrega múltiple genere una sola factura, una factura fácil de elegir.

    factura en la selección, devolución de la factura de la recolección, devolución de la factura del envío, devolución de la factura de la Entrega.
    
Genere una sola factura desde una orden de entrega múltiple, cree una sola factura desde una orden de entrega múltiple, una sola factura por una orden de entrega múltiple, una sola factura desde pedidos, una selección múltiple genere una sola factura, una factura fácil desde una orden de entrega
Genere una sola factura desde un Envío múltiple, Cree una sola factura desde un Envío múltiple, Una sola factura por Shioment múltiple, Una sola factura desde Picking, Envío múltiple genere una sola factura, Factura sencilla desde el envío entrante
    Genere una sola factura desde varias selecciones, genere facturas desde el pedido de entrega, genere facturas desde picking, genere facturas desde el envío.
    factura por picking, factura por orden de entrega, factura por envío


""",
    'category': 'Accounting',
    "website": "https://www.browseinfo.in",
    "data": [
        'security/ir.model.access.csv',
        'wizard/stock_invoice_onshipping.xml',
        'views/inherited_stock_picking.xml',
        'views/inherited_invoice_view.xml',
        'views/inherited_purchase.xml',
        
    ],
    "price": 29,
    "currency": 'EUR',
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/mzAseYyeyw0',
    "images": ["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
