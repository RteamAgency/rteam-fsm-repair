{
    "name": "FSM + Repair: Field Service Repair Workflow",
    "version": "19.0.1.0.1",
    "post_init_hook": "_post_init_hook",
    "category": "Services/Field Service",
    "summary": (
        "Bridge Field Service and Repair: tablet signatures, protocol email, "
        "multi-visit cases, equipment lifecycle."
    ),
    "description": """
FSM + Repair: Field Service Repair Workflow
===========================================

Native Odoo treats Field Service tasks and Repair Orders as two unrelated
workflows. In real service operations they're the same case: an engineer
visits, can't fix it on-site, the unit goes to a workshop, parts are
ordered, a second engineer re-installs after the in-shop work.

This module adds the missing bridge.

Features
--------
* **Request Type** selector on every FSM task: Installation / Repair /
  Diagnostic / Preventive Maintenance / RMA
* **Equipment** link to ``maintenance.equipment`` + Serial/Lot via
  ``stock.lot``, with Equipment Serial No surfaced as a related read-only
  field
* **Problem Description**, **Engineer Findings**, **Resolution / Work
  Done** rich-text fields organised in a dedicated Repair tab on the FSM
  task form
* **Tablet Engineer Signature** and **Customer Signature** widgets, with
  auto-stamp of "Signed At" the moment the customer captures the signature
* **Send Repair Protocol** button: renders a QWeb PDF protocol with both
  signatures and emails it to the customer in one click; PDF is attached
  to the task chatter
* **Bridge to Odoo Repair**: link any FSM task to a ``repair.order`` as
  the persistent "case file"; one repair order can span N field visits
  plus in-shop work plus RMA escalation
* **Smart-button "Repair Case"** on FSM task form -> jumps to the linked
  repair order
* **Smart-button "Field Visits"** with count on the repair order ->
  filtered list of all on-site visits for that case
* **One-click "Create Repair Order"** from an FSM task: pre-fills
  customer, lot/serial, problem description, links them, opens the new
  case-file form
* **Full Ukrainian localization** (uk_UA): every field, button, page,
  label, and selection value translated
* **Mail template** with severity badge, "View in Odoo" deep-link
  button, and PDF auto-attached

Who is this for
---------------
- Manufacturers and OEMs that build, sell, and service their own
  equipment (laser cutters, packaging machines, industrial printers...)
- Equipment dealers with after-sale service contracts
- Field service teams running tiered service programs (on-site visit ->
  in-shop repair -> RMA to OEM)
- Any Odoo deployment using ``industry_fsm`` AND ``repair`` AND
  ``helpdesk_fsm`` together

What it solves
--------------
Before this module, a single laser-cutter problem produces:

- 1 Helpdesk ticket
- 1 FSM task (engineer visit)
- 0 way to track that "the unit went to lab"
- 1 Repair Order (created manually, disconnected)
- 1 second FSM task for re-install (no link to the first)

After: one ``repair.order`` is the case file, with N linked Field Visits
on its smart-button. Engineer captures signatures on tablet, customer
gets the protocol PDF emailed before they leave the room.

Suggested kanban stages for the Repair project (configure manually under
Settings -> Project -> Stages):

::

    Diagnostic -> Quote -> Awaiting Parts -> In Progress -> Testing -> Closed

Built initially for a Ukrainian manufacturer of laser-cutting equipment,
generalized as a free LGPL-3 module for any service operation that needs
the same bridge.

Out of scope (configuration done manually in Odoo)
--------------------------------------------------
- Role-based access groups (Engineer profile with start/finish-only
  rights) - configure standard FSM/Repair groups via Settings -> Users
- Multi-currency parts costing per repair - handled natively by
  ``industry_fsm_sale`` + Odoo Accounting
- Sign module integration with certified-PDF audit trail - planned for
  a separate companion module

License
-------
LGPL-3, free. See LICENSE file.
""",
    "author": "Rteam",
    "website": "https://rteam.agency",
    "support": "alex@rteam.top",
    "license": "LGPL-3",
    "depends": [
        "industry_fsm",
        "helpdesk_fsm",
        "maintenance",
        "stock",
        "repair",
        "mail",
    ],
    "data": [
        "reports/report_protocol_template.xml",
        "data/mail_template_data.xml",
        "views/project_task_views.xml",
        "views/repair_order_views.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
