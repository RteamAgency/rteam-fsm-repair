{
    "name": "FSM + Repair: Field Service Repair Workflow",
    "version": "19.0.1.1.0",
    "post_init_hook": "_post_init_hook",
    "category": "Services/Field Service",
    "summary": (
        "Bridge Field Service and Repair: tablet signatures, protocol email, "
        "multi-visit cases, equipment lifecycle, 8 languages."
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
* **Repair tab** on the FSM task form with rich-text Problem Description,
  Engineer Findings, Resolution / Work Done
* **Tablet Engineer + Customer signatures** with auto-stamp of Signed At
  the moment the customer captures their signature
* **Send Repair Protocol** button: renders a QWeb PDF with both signatures
  and emails it to the customer in one click; PDF auto-attached
* **Bridge to Odoo Repair**: link any FSM task to a ``repair.order`` as
  the persistent case file; one repair order can span N field visits plus
  in-shop work plus RMA escalation
* **Smart-button "Repair Case"** on FSM task -> jumps to linked repair order
* **Smart-button "Field Visits"** with count on repair order -> filtered
  list of all on-site visits for that case
* **One-click "Create Repair Order"** from FSM task: pre-fills customer,
  lot/serial, problem description, links them, opens the new case form
* **Localized in 8 languages**: EN, RU, UK, DE, ES, RO, PL, AR
* **Mail template** with severity badge, "View in Odoo" deep-link button,
  and PDF auto-attached

Technical reference (what gets added, where)
--------------------------------------------

Inherited model ``project.task`` (Field Service tasks):

* ``x_request_type`` Selection [installation, repair, diagnostic,
  maintenance, rma], tracking
* ``x_equipment_id`` Many2one -> ``maintenance.equipment``, tracking
* ``x_equipment_serial_no`` Char related (``x_equipment_id.serial_no``),
  read-only
* ``x_serial_lot_id`` Many2one -> ``stock.lot``, tracking
* ``x_problem_description``, ``x_findings``, ``x_resolution`` Html
* ``x_engineer_signature``, ``x_customer_signature`` Binary
  (``widget="signature"``, ``attachment=True``)
* ``x_signed_by`` Char, ``x_signed_at`` Datetime (auto-stamp via
  ``@api.onchange("x_customer_signature")``)
* ``x_repair_order_id`` Many2one -> ``repair.order``, tracking, indexed
* Methods: ``_action_url()``, ``action_send_repair_protocol()``,
  ``action_create_repair_order()``, ``action_open_repair_order()``

Inherited model ``repair.order`` (Repair Orders):

* ``fsm_task_ids`` One2many -> ``project.task`` (inverse
  ``x_repair_order_id``)
* ``fsm_task_count`` Integer (computed)
* Method: ``action_view_fsm_tasks()``

Inherited views:

* ``project.view_task_form2`` (FSM/project task form):

  - New "Repair" tab in notebook (visible if ``is_fsm == True``)
  - All x_ fields above grouped into the new tab
  - "Create Repair Order" button (visible if no repair order linked)
  - "Send Repair Protocol" button (visible if customer signature captured)
  - "Repair Case" smart-button in button_box (visible if linked)

* ``project.view_task_kanban``: surfaces ``x_request_type`` for filtering
* ``repair.view_repair_order_form``: "Field Visits" smart-button with
  count in button_box (visible if count > 0)

New records:

* ``ir.actions.report`` ``rteam_fsm_repair.action_report_repair_protocol``:
  QWeb PDF protocol bound to ``project.task`` via Print menu
* ``mail.template`` ``rteam_fsm_repair.mail_template_repair_protocol``:
  branded HTML body, "View in Odoo" CTA, PDF auto-attached

post_init_hook ``_post_init_hook``: links the report to the mail template's
``report_template_ids`` Many2many (avoids ``ref()``/``eval`` cross-file
xmlid resolution issues at install time).

No new menus, no new top-level views, no global ACL changes.

Who is this for
---------------
- Manufacturers and OEMs that build, sell, and service their own
  equipment (laser cutters, packaging machines, industrial printers,
  medical devices)
- Equipment dealers with after-sale service contracts
- Field service teams running tiered service programs (on-site visit ->
  in-shop repair -> RMA escalation to OEM)
- Any Odoo deployment using ``industry_fsm`` AND ``repair`` AND
  ``helpdesk_fsm`` together

Suggested kanban stages for a Repair project (configure manually under
Settings -> Project -> Stages)::

    Diagnostic -> Quote -> Awaiting Parts -> In Progress -> Testing -> Closed

Out of scope (configure manually in Odoo)
-----------------------------------------
- Role-based access groups: configure standard FSM/Repair groups via
  Settings -> Users
- Multi-currency parts costing per repair: handled natively by
  ``industry_fsm_sale`` + Odoo Accounting
- Sign module integration with certified-PDF audit trail: planned for
  a separate companion module
- RMA shipping tracking to external OEMs: planned for a separate
  companion module

About Rteam
-----------
Rteam is a global Odoo partner specializing in Odoo Enterprise
implementations and custom development for manufacturers, equipment
dealers, and distribution companies across the EU, the UK, the UAE,
and Ukraine. We design and ship production-grade Odoo Apps for the
public catalogue and tailor enterprise deployments end-to-end.

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
