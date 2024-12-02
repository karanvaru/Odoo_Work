# -*- coding: utf-8 -*-
{
    "name": "CRM Check List and Approval Process",
    "version": "12.0.2.0.1",
    "category": "Sales",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/crm-check-list-and-approval-process-245",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "crm"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/crm_stage.xml",
        "views/crm_lead.xml",
        "views/crm_chek_list.xml",
        "data/data.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to make sure required jobs are carefully done on this pipeline stage",
    "description": """
    Making a customer from an opportunity is the only goal of CRM pipeline. To achieve that goal sales staff needs to undertake a specific sequence of actions. Each of those actions is important on a definite funnel stage. Efficient companies know that missing of any step might result in a long-run failure. This is the tool to make sure such a failure will not happen. The app provides a check list for each pipeline stage to control over requirements' fulfilment, and make sure that each action is fully approved by responsible users.

    Check lists are assigned per each opportunity stage. Set of check list points is up to you. Check list fulfilment is shown on opportunities' kanban and form views to easily control progress
    As soon as an opportunity is moved to a certain stage, its check list is updated to a topical one from this stage. For instance, actions for 'new' and 'proposition' stages must be different, don't they?
    To move a CRM lead forward in your funnel, a check list should be fully confirmed. By 'moving forward' any change of stage with lesser sequence to a bigger sequence is implied
    Confirmation might assume involvement of different user roles. Certain check list points might be approved only by top-level employees, for example. In such a case just assign a user group for this check list item 
    Check list actions are saved in the opportunity history. In case a lead is moved back, already done check list items would be recovered. However, in case the 'not saved' option is set for the item up, the point should be approved each time from scratch
    The tool let you grant users with the super check list rights right on a user form. In such a case, such users are able (a) to confirm any check points disregarding defined user groups; (b) move any opportunity further without fulfilling check lists
    For some situations you do not need a check list fulfilment even a new stage is further. For example, for the 'Cancelled' stage. In such a case just mark this stage as 'No need for checklist'
    Opportunity check list per stages
    Opportunity stage check lists
    Check list to be confirmed before moving an opportunity further
    Approval process distributed by various user roles
    Opportunities check list progress kanban view
    The super rights to approve any check items and move opportunities
    Check list tree view
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
}