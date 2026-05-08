# Rteam FSM Repair Workflow

Adds repair-specific fields and a sign-protocol flow on top of Odoo's Field
Service module. Designed for service teams that handle on-site repair,
installation, diagnostic, preventive maintenance, and RMA visits.

- **Target**: Odoo 19 Enterprise (Field Service is Enterprise-only)
- **License**: LGPL-3 (free)
- **Module technical name**: `rteam_fsm_repair`
- **Author**: [Rteam](https://rteam.agency)

## Features

1. `Request Type` selector on every FSM task (Installation / Repair /
   Diagnostic / Preventive Maintenance / RMA)
2. `Equipment` link to `maintenance.equipment` + `Serial / Lot` via
   `stock.lot` (domain-filtered to the equipment's product)
3. Rich-text `Problem Description`, `Engineer Findings`,
   `Resolution / Work Done` fields organised in a dedicated **Repair** tab
4. Tablet `Engineer Signature` and `Customer Signature` widgets
   (auto-stamps `Signed At` when the customer signature is captured)
5. **Send Repair Protocol** button: renders a PDF protocol with both
   signatures and emails it to the customer in one click

The Helpdesk &harr; FSM linkage (ticket spawning a field intervention with a
back-reference) is provided natively by `helpdesk_fsm`, declared as a
dependency. This module focuses on the FSM-side data layer.

## Suggested kanban stages

Configure these manually on your FSM Repair project (Settings &rarr;
Project &rarr; Stages):

```
Diagnostic -> Quote -> Awaiting Parts -> In Progress -> Testing -> Closed
```

## Install

```bash
git clone git@github.com:RteamAgency/rteam-fsm-repair.git
# place the inner rteam_fsm_repair/ folder on your Odoo addons path
# or add this repo as a git submodule on Odoo.sh / on-prem deployments
```

Then in Odoo: Apps &rarr; Update Apps List &rarr; install
**"Rteam FSM Repair Workflow"**.

Module dependencies are pulled automatically: `industry_fsm`,
`helpdesk_fsm`, `maintenance`, `stock`, `mail`.

## Roadmap (not in MVP)

- Role-based access groups (Engineer profile with start/finish-only rights)
- Multi-currency parts costing per repair
- RMA loop module (parent OEM &harr; in-house lab &harr; field tech)
- Spare-parts requisition wizard from FSM task to internal transfer

## Author

[Rteam](https://rteam.agency) - Odoo consulting and custom development,
based in Ukraine. Built initially for ARAMIS Laser Systems demo on Odoo 19.

## License

LGPL-3. See [LICENSE](LICENSE).
