================================================
FSM + Repair: Field Service Repair Workflow
================================================

Bridge Odoo Field Service and Repair into one continuous service case:
tablet signatures, instant protocol email, multi-visit history per asset,
**localized in 8 languages**.

- **Target**: Odoo 19 Enterprise
- **License**: LGPL-3 (free)
- **Module technical name**: ``rteam_fsm_repair``
- **Author**: `Rteam <https://rteam.agency>`_
- **Support**: alex@rteam.top
- **Repository**: https://github.com/RteamAgency/rteam-fsm-repair


Why this module exists
======================

Native Odoo treats Field Service tasks and Repair Orders as two unrelated
workflows. In real service operations they're the same case: an engineer
visits, can't fix it on-site, the unit goes to a workshop, parts are
ordered, a second engineer re-installs after the in-shop work.

Today this means two disconnected records and a manager piecing the
timeline together by chatter. **FSM + Repair adds the missing bridge.**

Built initially for a manufacturer of laser-cutting equipment with eight
field engineers, RMA loops to OEMs in the US and Germany, and a nine-tier
service program. Generalized as a free LGPL-3 module for any service
operation that needs the same shape.


Features
========

1. **Request Type per visit**: Installation / Repair / Diagnostic /
   Preventive Maintenance / RMA.
2. **Equipment + serial lifecycle**: link visits to ``maintenance.equipment``
   and ``stock.lot``, with Equipment S/N as a related read-only field.
3. **Repair tab on the FSM task form** with rich-text Problem Description,
   Engineer Findings, Resolution / Work Done.
4. **Tablet signatures** for Engineer + Customer with auto-stamp Signed At.
5. **Send Repair Protocol** button: renders QWeb PDF with both signatures
   and emails it to the customer in one click.
6. **Bridge to Odoo Repair**: link any FSM task to a ``repair.order`` as
   the persistent case file.
7. **Smart-button "Repair Case"** on FSM task and **"Field Visits"** with
   count on the repair order, both directions navigable.
8. **One-click "Create Repair Order"** from FSM task: pre-fills customer,
   lot/serial, problem description, links them, opens the new case form.
9. **Localized in 8 languages**: English, Русский, Українська, Deutsch,
   Español, Română, Polski, العربية.
10. **Mail template** with severity badge, "View in Odoo" deep-link button,
    and PDF auto-attached.


Technical reference (what gets added, where)
============================================

Inherited model ``project.task`` (Field Service tasks)
------------------------------------------------------

================================  ===================================================  ================================
Technical name                    Type                                                 Visible in
================================  ===================================================  ================================
``x_request_type``                Selection (5 values)                                 Repair tab + kanban
``x_equipment_id``                Many2one -> ``maintenance.equipment``                Repair tab
``x_equipment_serial_no``         Char (related, read-only)                            Repair tab
``x_serial_lot_id``               Many2one -> ``stock.lot``                            Repair tab
``x_problem_description``         Html                                                 Repair tab
``x_findings``                    Html                                                 Repair tab
``x_resolution``                  Html                                                 Repair tab
``x_engineer_signature``          Binary, ``widget="signature"``                       Repair tab
``x_customer_signature``          Binary, ``widget="signature"``                       Repair tab
``x_signed_by``                   Char                                                 Repair tab
``x_signed_at``                   Datetime (auto-stamp via onchange)                   Repair tab
``x_repair_order_id``             Many2one -> ``repair.order``                         Repair tab + smart-button
================================  ===================================================  ================================

New methods on ``project.task``: ``_action_url()``,
``action_send_repair_protocol()``, ``action_create_repair_order()``,
``action_open_repair_order()``.


Inherited model ``repair.order`` (Repair Orders)
------------------------------------------------

================================  =====================================================================  ============================
Technical name                    Type                                                                   Visible in
================================  =====================================================================  ============================
``fsm_task_ids``                  One2many -> ``project.task`` (inverse ``x_repair_order_id``)           smart-button
``fsm_task_count``                Integer (computed)                                                     smart-button counter
================================  =====================================================================  ============================

New method on ``repair.order``: ``action_view_fsm_tasks()``.


New page, buttons, smart-buttons
--------------------------------

- New **"Repair" tab** in ``project.view_task_form2`` notebook (visible only
  when ``is_fsm == True``).
- Button **"Create Repair Order"** in Repair tab (visible if no repair
  order linked).
- Button **"Send Repair Protocol"** in Repair tab (visible if customer
  signature captured).
- Smart-button **"Repair Case"** in ``project.task`` button_box (visible
  if linked).
- Smart-button **"Field Visits"** with count in ``repair.order``
  button_box (visible if count > 0).
- Kanban inherit on ``project.view_task_kanban`` to surface
  ``x_request_type``.


New records
-----------

- ``ir.actions.report`` ``rteam_fsm_repair.action_report_repair_protocol``:
  QWeb PDF protocol bound to ``project.task`` via Print menu.
- ``mail.template`` ``rteam_fsm_repair.mail_template_repair_protocol``:
  branded HTML body with "View in Odoo" CTA, PDF auto-attached.
- ``post_init_hook`` ``_post_init_hook``: links the report to the mail
  template's ``report_template_ids``.

No new menus, no new top-level views, no global ACL changes. Existing FSM
and Repair access groups govern visibility.


Who is this for
===============

- **Manufacturers and OEMs** that build, sell, and service their own
  equipment (laser cutters, packaging machines, industrial printers,
  medical devices)
- **Equipment dealers** with after-sale service contracts and a mix of
  in-field and in-shop repair
- **Field service teams** running tiered service programs (on-site visit
  -> in-shop repair -> RMA escalation to OEM)
- **Any Odoo deployment** using ``industry_fsm`` AND ``repair`` AND
  ``helpdesk_fsm`` together


Install
=======

::

    git clone https://github.com/RteamAgency/rteam-fsm-repair.git
    # place the inner rteam_fsm_repair/ folder on your Odoo addons path,
    # or add this repo as a git submodule on Odoo.sh / on-prem deployments

In Odoo: Apps -> Update Apps List -> install **FSM + Repair**.
Module dependencies are pulled automatically: ``industry_fsm``,
``helpdesk_fsm``, ``repair``, ``maintenance``, ``stock``, ``mail``.


Configuration
=============

1. Project -> Settings -> create a Field Service project; add the
   recommended kanban stages:
   ``Diagnostic -> Quote -> Awaiting Parts -> In Progress -> Testing -> Closed``.
2. Equipment -> create the units you service (one record per serial number).
3. Open any FSM task: the **Repair** tab is right there with all the new
   fields.


What it does NOT do
===================

Out of scope for this module:

- **Role-based access groups** (Engineer profile with start/finish-only
  rights) -> configure standard FSM/Repair groups via Settings -> Users.
- **Multi-currency parts costing per repair** -> handled natively by
  ``industry_fsm_sale`` + Odoo Accounting.
- **Sign module integration** with certified-PDF audit trail -> planned
  for a separate companion module.
- **RMA shipping tracking** to external OEMs -> planned for a separate
  companion module.


About Rteam
===========

Rteam is a global Odoo partner specializing in Odoo Enterprise
implementations and custom development for manufacturers, equipment
dealers, and distribution companies. We design and ship
production-grade Odoo Apps for the public catalogue and tailor enterprise
deployments end-to-end across the EU, the UK, the UAE, and Ukraine.

- Email: alex@rteam.top
- Source code: https://github.com/RteamAgency/rteam-fsm-repair
- Website: https://rteam.agency


License
=======

LGPL-3. Free forever. See ``LICENSE`` file for full copyright and
licensing details.
