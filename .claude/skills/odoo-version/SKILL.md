---
name: odoo-version
description: >-
  Odoo 20.0 notes for this repository: what differs from the Odoo 20.0
  rules in odoo-guidelines, odoo-web-guidelines, odoo-security and
  odoo-review, plus Rteam's rules for client addon repositories. Read before
  writing, reviewing or auditing any Odoo code here.
---

# Odoo 20.0 in this repository

## Odoo 20.0

The sibling skills were written for this version: apply them as written,
with the Rteam rules and the correction below.

### Not in the skills, not done by upgrade_code

Checked against odoo/odoo 20.0 at `299075f` on 2026-10-28, while porting
Rteam's six apps from 19.0. `upgrade_code` converts access rights to
`ir.access`, FA icons to Material Symbols and `_sql_constraints` to
`models.Constraint`; these need a hand port.

| On 19.0 and earlier | On 20.0 |
| --- | --- |
| `ir.config_parameter` `get_param(key, default)` / `set_param(key, value)` | Gone, no alias: an `AttributeError` at runtime. Read with `get_str`, `get_int`, `get_float` or `get_bool` (missing or invalid value: the default), write with `set_str`, `set_int`, `set_float`, `set_bool` (`None` or `False` clears). Pick the type the code converts to; `int(get_param(...))` in a try/except becomes `get_int(key, default)`. Grep every module and XML `<function name="set_param">` before a 20.0 estimate. |
| Tests: `self.registry_enter_test_mode()` | A context manager: `self.enterContext(self.registry_test_mode())`. |
| `industry_fsm`, `helpdesk_fsm` | Removed from enterprise; Field Service is `planning_field_service` (on `planning.slot`) and `helpdesk_planning_field_service`. A module depending on them is ported by hand. |
| Python 3.10 or later | Python 3.12 to 3.14. |

`odoo.http.request` still exists in models (core `res_users` reads the login
IP from it, guarded by `if request`); the skills' rule against using it in
models stands for new code.

## Rteam rules for this repository

An Rteam Odoo repository holds custom addons for one client (or one of our own
apps) on a released Odoo version, usually deployed on Odoo.sh. It is neither
Odoo's master nor a stable branch of Odoo, so read the sibling skills with
these adjustments:

- **Stable vs master (odoo-review).** New features in our own addons are normal
  work, so the "master" reading applies to new code. Do not reformat code a
  change does not touch: keep the diff minimal and match the surrounding style.
- **Changes in a stable version (odoo-guidelines `stable.md`)** binds changes
  to Odoo's own modules, which we never edit in place: extend them from our
  addon by inheritance. For our addons already in production:
  - bump `version` in `__manifest__.py` whenever fields, views or data change:
    Odoo.sh updates a production module only when its version goes up;
  - add a migration script (`migrations/<version>/pre-*.py` or `post-*.py`)
    when existing records need values, and never rename or drop a stored field
    without one;
  - keep existing XML ids: other modules and user data reference them.
- **Review scope (odoo-review step 1).** Diff from the merge-base:
  `git diff origin/stage...HEAD` for a task branch, `git diff
  origin/main...HEAD` for a release branch. A two-dot diff against the stage
  tip shows every unreleased stage commit as removed by this change. There is
  no enterprise "other half" to look for unless the change spans two of our
  repositories.
- **Branches and commits** follow the `odoo-git` skill in this folder, not
  Odoo's own conventions.
- **Data.** Tests and demo data use invented names, amounts and documents,
  never a client's records.

## Traps found on Rteam's apps

- **`_()` reads the caller's locals.** With no language in the context, as
  in a cron job, `_()` takes a local named `cr`, `cursor`, `uid`, `user` or
  `context` from the calling frame. A `prozorro.sync.cursor` record held in
  `cursor` crashed every scheduled sync (rteam_prozorro 19.0.1.0.3). Name
  such locals otherwise, or call `self.env._()`.
- **A non-stored compute is cached for the transaction.** Read before the
  records it looks up exist (and not in its `depends`), it keeps the old
  value: a second Confirm sent a second Telegram approval
  (rteam_tg_invoice 19.0.1.1.1). Invalidate it or search directly.
- **Tests run without demo data** (`scripts/stand.sh`, the CI template):
  create what a test needs, load a chart with
  `env["account.chart.template"].try_loading("generic_coa", company)` when
  the company has no journal, and give test users explicit groups.

## Correction for every version

- odoo-security names `setInnerHtml` among the `@web/core/utils/html`
  helpers. It does not exist in any version (checked on 18.0, 19.0, 20.0 and
  master on 2026-10-27): the helper is `setElementContent`.
