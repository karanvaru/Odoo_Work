# -*- coding: utf-8 -*-
{
    "name": "CRM Duplicates Real Time Search",
    "version": "12.0.2.0.1",
    "category": "Sales",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/crm-duplicates-real-time-search-254",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "crm"
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/crm_lead_view.xml",
        "views/res_partner_view.xml",
        "data/data.xml",
        "security/ir.model.access.csv"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool for real-time control of customers' and opportunities duplicates",
    "description": """
    This is the sales managers' tool to exclude double work and broken communication through fore-handed exposure of duplicates of customers and opportunities.

    If you do not use CRM and searches for the tool only for partners' duplicates, look at the tool <a href='https://apps.odoo.com/apps/modules/12.0/partner_duplicates/'>Contacts Duplicates Real Time Search</a>
    Real-time duplicates search
    Configurable duplicates' criteria
    Rigid or soft duplicates
    Compatible with Odoo standard features
    # Performance issues
    <p style='font-size:18px;'>
Since the search is done in real-time Odoo has to check all shown records for duplicates among all existing records. For example, when you open opportunities' kanban with 80 items, and you have 10,000 leads, the tool make 80 searches by your criteria among 10000 documents.  It may result in slowdowns of the following operations:
</p>
<ul style='font-size:18px;'>
<li>Opening kanban and list views of customers and opportunities</li>
<li>Saving changes after update of partners and opportunities</li>
</ul>
<p style='font-size:18px;'>
The tool is <strong>optimized</strong> to make searches as efficient as Odoo ORM allows it. Simultaneously, with a growing number of documents a search will become slower.
</p>
    # How rules work
    <p style='font-size:18px;'>
As a duplicate criteria use any stored field of the following types: char (name, email, phone, mobile, etc.), text (descriptions), many2one (reference for a parent company or a related customer), selection (for instance, type), date and datetime (e.g. birthday), integer and float (any unique code or even planned revenue).
</p>
<p style='font-size:18px;'>
For all field a duplicate should have absolutely the same value (e.g. '123' = '123', but '123' is not equal '1234'). Only for the case of soft search by char fields it is the operator 'ilike'. Thus, 'agro' is considered to be a potential duplicate of 'Agrolait' (but Agrolait is not considered as a duplicate of 'agro').
</p>
<p style='font-size:18px;'>
For partners' duplicates you may restrict search only for companies and stand-alone individuals. If the option is checked, Odoo will search only for and only among partners without parent.
</p>
    Configure soft and rigid criteria to search duplicates of customers and opportunities
    Users can't save a customer if there is a rigid duplicate found
    Warn salespersons of possible customers duplicates
    Instant access to customer possible duplicates from kanban
    Partners overall duplicates analysis
    Partners tree: observe potential duplciates counter
    Salespersons are forbidden save an opportunity if there is a rigid duplicate found
    Warn salespersons of possible opportunites duplicates
    One-click access for opportunities duplicates from kanban view
    Filter opportunities with possible duplicates
    Number of potential opportunities duplicates right in the opportunities' list
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "68.0",
    "currency": "EUR",
}