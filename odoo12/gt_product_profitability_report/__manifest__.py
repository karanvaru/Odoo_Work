# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#    Globalteckz Software Solutions and Services                             #
#    Copyright (C) 2013-Today(www.globalteckz.com).                          #
#                                                                            #
#    This program is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU Affero General Public License as          #
#    published by the Free Software Foundation, either version 3 of the      #
#    License, or (at your option) any later version.                         #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #  
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU Affero General Public License for more details.                     #
#                                                                            #
#                                                                            #
##############################################################################

{
    "name" : "Product Profitability Report",
    "version" : "1.0",
    "depends" : ['product','sale','delivery','base','stock','sale_stock',],
    "author" : "Globalteckz",
    "website" : "www.globalteckz.com",
    "category" : "Sales ",
    'summary': 'It will handle product profitability report by yearly , monthly ,daily and by Products ',
    "description": """Profitability Report


""",
    "demo" : [],
    "data" : [
       'security/ir.model.access.csv',
        'views/gt_sale_report_view.xml',
       
      #  
                    ],
    'auto_install': False,
    "installable": True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

