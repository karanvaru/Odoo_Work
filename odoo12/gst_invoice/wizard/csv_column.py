# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, models

class CsvColumn(models.TransientModel):
    _name = "csv.column"
    _description = "CSV column"

    def getB2BColumn(self, gstType):
        columns = []
        if gstType == 'gstr1':
            columns = [
                'GSTIN/UIN of Recipient',
                'Receiver Name',
                'Invoice Number',
                'Invoice date',
                'Invoice Value',
                'Place Of Supply',
                'Reverse Charge',
                'Applicable % of Tax Rate',
                'Invoice Type',
                'E-Commerce GSTIN',
                'Rate',
                'Taxable Value',
                'Cess Amount'
            ]
        if gstType == 'gstr2':
            columns = [
                'GSTIN of Supplier',
                'Invoice Number',
                'Invoice date',
                'Invoice Value',
                'Place Of Supply',
                'Reverse Charge',
                'Invoice Type',
                'Rate',
                'Taxable Value',
                'Integrated Tax Paid',
                'Central Tax Paid',
                'State/UT Tax Paid',
                'Cess Amount',
                'Eligibility For ITC',
                'Availed ITC Integrated Tax',
                'Availed ITC Central Tax',
                'Availed ITC State/UT Tax',
                'Availed ITC Cess'
            ]

        return columns

    def getB2BURColumn(self):
        columns = [
            'Supplier Name',
            'Invoice Number',
            'Invoice date',
            'Invoice Value',
            'Place Of Supply',
            'Supply Type',
            'Rate',
            'Taxable Value',
            'Integrated Tax Paid',
            'Central Tax Paid',
            'State/UT Tax Paid',
            'Cess Amount',
            'Eligibility For ITC',
            'Availed ITC Integrated Tax',
            'Availed ITC Central Tax',
            'Availed ITC State/UT Tax',
            'Availed ITC Cess'
        ]
        return columns

    def getB2CLColumn(self):
        columns = [
            'Invoice Number',
            'Invoice date',
            'Invoice Value',
            'Place Of Supply',
            'Applicable % of Tax Rate',
            'Rate',
            'Taxable Value',
            'Cess Amount',
            'E-Commerce GSTIN',
            'Sale from Bonded WH'
        ]
        return columns

    def getB2CSColumn(self):
        columns = [
            'Type',
            'Place Of Supply',
            'Applicable % of Tax Rate',
            'Rate',
            'Taxable Value',
            'Cess Amount',
            'E-Commerce GSTIN'
        ]
        return columns

    def getImpsColumn(self):
        columns = [
            'Invoice Number of Reg Recipient',
            'Invoice Date',
            'Invoice Value',
            'Place Of Supply',
            'Rate',
            'Taxable Value',
            'Integrated Tax Paid',
            'Cess Amount',
            'Eligibility For ITC',
            'Availed ITC Integrated Tax',
            'Availed ITC Cess'
        ]
        return columns

    def getImpgColumn(self):
        columns = [
            'Port Code',
            'Bill Of Entry Number',
            'Bill Of Entry Date',
            'Bill Of Entry Value',
            'Document type',
            'GSTIN Of SEZ Supplier',
            'Rate',
            'Taxable Value',
            'Integrated Tax Paid',
            'Cess Amount',
            'Eligibility For ITC',
            'Availed ITC Integrated Tax',
            'Availed ITC Cess'
        ]
        return columns

    def getExportColumn(self):
        columns = [
            'Export Type',
            'Invoice Number',
            'Invoice date',
            'Invoice Value',
            'Port Code',
            'Shipping Bill Number',
            'Shipping Bill Date',
            'Applicable % of Tax Rate',
            'Rate',
            'Taxable Value'
        ]
        return columns

    def getHSNColumn(self):
        columns = [
            'HSN',
            'Description',
            'UQC',
            'Total Quantity',
            'Total Value',
            'Taxable Value',
            'Integrated Tax Amount',
            'Central Tax Amount',
            'State/UT Tax Amount',
            'Cess Amount'
        ]
        return columns
