# Changelog

All notable changes to this module will be documented in this file.

## 19.0.1.0.0 - 2026-05-08 - Initial release

- Request Type selector on FSM tasks: Installation / Repair / Diagnostic /
  Preventive Maintenance / RMA.
- Equipment link to `maintenance.equipment` and Serial / Lot via `stock.lot`
  with domain filtered to the equipment's product.
- Rich-text Problem Description, Engineer Findings, Resolution / Work Done
  fields organised in a dedicated Repair tab on the FSM task form.
- Tablet Engineer Signature and Customer Signature widgets, with auto-stamp
  of `Signed At` when the customer signature is captured.
- Send Repair Protocol button: renders a QWeb PDF protocol with both
  signatures and emails it to the customer via `mail.template`.
- "View in Odoo" CTA in the protocol email body, deep-linking to the FSM
  task form.

Built initially for the ARAMIS Laser Systems demo on Odoo 19.
