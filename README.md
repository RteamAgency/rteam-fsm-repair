# Rteam FSM Repair Workflow

Adds repair-specific fields and a sign-protocol flow on top of Odoo's Field
Service module. Designed for service teams that handle on-site repair,
installation, diagnostic, preventive maintenance, and RMA visits.

- **Target**: Odoo 20 Enterprise (Field Service is Enterprise-only). On 20.0 a
  field service visit is a `planning.slot` (`planning_field_service`); the
  `19.0` branch serves Odoo 19, where it was an `industry_fsm` task.
- **License**: LGPL-3 (free)
- **Module technical name**: `rteam_fsm_repair`
- **Author**: [Rteam](https://rteam.agency)

## Features

1. `Request Type` selector on every field service visit (Installation / Repair /
   Diagnostic / Preventive Maintenance / RMA)
2. `Equipment` link to `maintenance.equipment` + `Serial / Lot` via
   `stock.lot` (domain-filtered to the equipment's product)
3. Rich-text `Problem Description`, `Engineer Findings`,
   `Resolution / Work Done` fields organised in a dedicated **Repair** tab
4. Tablet `Engineer Signature` and `Customer Signature` widgets
   (auto-stamps `Signed At` when the customer signature is captured)
5. **Send Repair Protocol** button: renders a PDF protocol with both
   signatures and emails it to the customer in one click

Helpdesk is not required: on 20.0 the module depends on Field Service
(`planning_field_service`) and Repair only.

## Install

```bash
git clone git@github.com:RteamAgency/rteam-fsm-repair.git
# place the inner rteam_fsm_repair/ folder on your Odoo addons path
# or add this repo as a git submodule on Odoo.sh / on-prem deployments
```

Then in Odoo: Apps &rarr; Update Apps List &rarr; install
**"Rteam FSM Repair Workflow"**.

Module dependencies are pulled automatically: `planning_field_service`,
`repair`, `maintenance`, `stock`, `mail`.

## Upgrading a 19.0 database

Odoo 20 plans a field service visit as a planning shift; on 19.0 this module's
Repair data sat on the field service task. When the upgraded database runs
`-u rteam_fsm_repair` with the 20.0 code, the migration
(`migrations/20.0.1.1.3/end-migrate.py`) carries it over:

- a task with exactly one shift linked to it (`planning_slot.task_id`, from
  `project_forecast`) hands its Repair values and both signatures to that shift;
- any other task keeps its Repair data as a note in its own chatter, with the
  signatures attached, and its repair order gets a note linking to the visit;
- every task that held Repair data is listed in the table
  `rteam_fsm_repair_legacy_task` with its values and where they went
  (`slot_id`, `outcome`). The table stays in the database.

How Odoo links a converted task to its shift is not documented: run the
upgrade on a copy first and check the server log line from `rteam_fsm_repair`
that counts what was moved.

## Roadmap (not in MVP)

- Role-based access groups (Engineer profile with start/finish-only rights)
- Multi-currency parts costing per repair
- RMA loop module (parent OEM &harr; in-house lab &harr; field tech)
- Spare-parts requisition wizard from a field service visit to internal transfer

## Author

[Rteam](https://rteam.agency) - Odoo consulting and custom development,
based in Ukraine. Built initially for ARAMIS Laser Systems demo on Odoo 19.

## License

LGPL-3. See [LICENSE](LICENSE).
