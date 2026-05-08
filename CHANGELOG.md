# Changelog

All notable changes to this module are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## 1.0.0 - 2026-05-08 - Initial public release

First release on apps.odoo.com.

### Added

- **Request Type** selector on FSM tasks: Installation / Repair / Diagnostic /
  Preventive Maintenance / RMA.
- **Equipment + Serial / Lot** link from `project.task` to
  `maintenance.equipment` and `stock.lot`. Equipment S/N surfaced as a
  related read-only field.
- **Repair tab** on the FSM task form with rich-text Problem Description,
  Engineer Findings, and Resolution / Work Done.
- **Tablet Signature widgets** for Engineer + Customer, auto-stamping a
  "Signed At" timestamp when the customer signs.
- **Send Repair Protocol** button: renders a QWeb PDF with both signatures
  embedded and opens the standard mail composer pre-filled with the
  recipient, branded HTML body, and PDF attached.
- **Bridge to Odoo Repair**: `x_repair_order_id` Many2one on
  `project.task`; `fsm_task_ids` One2many inverse on `repair.order`.
- **Smart-buttons** in both directions: "Repair Case" on FSM task,
  "Field Visits" with count on repair.order.
- **One-click "Create Repair Order"** from an FSM task with auto-fill of
  customer, lot/serial, and problem description.
- **Full Ukrainian localization** (`i18n/uk.po`): every field, button,
  page label, and selection value translated.
- **Mail template** with severity badge and "View in Odoo" deep-link button.
- Linkage between report and template handled in `_post_init_hook` (avoids
  ref/eval cross-file resolution issues at install time).
