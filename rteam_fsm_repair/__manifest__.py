{
    "name": "Rteam FSM Repair Workflow",
    "version": "19.0.1.0.4",
    "post_init_hook": "_post_init_hook",
    "category": "Services/Field Service",
    "summary": (
        "Repair flow on top of Field Service: request types, equipment, "
        "tablet signature, protocol email."
    ),
    "description": """
Rteam FSM Repair Workflow
=========================

Adds repair-specific fields and a sign-protocol flow on top of Odoo's
Field Service module. Designed for service teams that handle on-site
repair, installation, diagnostic, preventive maintenance, and RMA visits.

Features
--------
* Request Type selector on every FSM task (Installation / Repair /
  Diagnostic / Preventive Maintenance / RMA)
* Equipment link to ``maintenance.equipment`` + Serial / Lot via
  ``stock.lot``
* Problem Description, Engineer Findings, Resolution rich-text fields
  in a dedicated Repair tab
* Tablet Engineer Signature and Customer Signature widgets
* Send Repair Protocol button: renders a PDF protocol with both
  signatures and emails it to the customer

Suggested kanban stages for a Repair project (configure manually):
Diagnostic -> Quote -> Awaiting Parts -> In Progress -> Testing -> Closed.

Helpdesk -> FSM linkage is provided natively by ``helpdesk_fsm``
(declared as a dependency); this module focuses on the FSM-side fields.

License: LGPL-3, free.
""",
    "author": "Rteam",
    "website": "https://rteam.agency",
    "license": "LGPL-3",
    "depends": [
        "industry_fsm",
        "helpdesk_fsm",
        "maintenance",
        "stock",
        "mail",
    ],
    "data": [
        "reports/report_protocol_template.xml",
        "data/mail_template_data.xml",
        "views/project_task_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
