---
name: odoo-git
description: >-
  Rteam's git conventions for Odoo repositories: commit header
  [TASK-CODE][TAG] module: summary, a why-first body, which branch a task
  starts from, the stage / release / main flow, and pull request hygiene. Use
  when writing or amending a commit message, creating a branch for a task, or
  opening or updating a pull request on an Rteam Odoo repository.
---

# Rteam git conventions for Odoo repositories

Adapted from Odoo's own `odoo-git` skill (odoo/odoo 20.0, LGPL-3) for the
flow Rteam's tech lead runs on every client repository. Branch names used
below: `main` is Production, `stage` is Staging.

## Commit message

A commit message is a header `[TASK-CODE][TAG] module_name: summary`, a blank
line, a body that says **why** the change is made, and trailers last.

```
[ACME-0042][FIX] acme_sale: keep the delivery date on a duplicated order

Steps to reproduce:
- Open a confirmed order with a delivery date
- Duplicate it

The copy loses the delivery date, so the warehouse plans it for today.
The copy should keep the date the customer agreed to.

The field was declared with copy=False when it was added in ACME-0017.

After this commit the field is copied; the onchange on the commitment
date still recomputes it when the salesperson changes that date.
```

```
[ACME-0042][IMP] acme_sale, *: fixes

Fixed the order and some other things.
```

The second message has no reproduction steps, a vague summary, and says
nothing about why.

### Header

- `TASK-CODE` is the task's code in Rteam's tracker (rteam.top): the project
  prefix and number, such as `ACME-0042`. Never the numeric record id. Take
  it from the branch name (branches start with it, see below); when the
  branch does not carry it, ask the author. Never invent a code.
- `TAG` is one of:

  | Tag | Use |
  | --- | --- |
  | `[ADD]` | new module, or new files and features inside a module |
  | `[FIX]` | bug fix |
  | `[IMP]` | improvement of existing behaviour |
  | `[REF]` | refactoring, no behaviour change intended |
  | `[REM]` | removed code, views, data or modules |
  | `[MIG]` | migration: migration scripts, a port to another Odoo version |

  Older history also carries `[DEV]`; do not use it for new commits.
- `module_name` is the technical name of the addon. Several modules:
  `acme_sale, acme_stock:`. Many: the main one then `*`. A change outside any
  addon names the folder: `.claude:`, `.github:`, `scripts:`.
- The summary says what the commit does in a few words; the whole header
  stays around 80 characters.

### Body

The diff shows what changed. The body brings what the diff cannot: who asked,
what was wrong for whom, and why this solution.

- For a bug fix: the reported steps, what happens, what should happen. Take
  them from the task or the client's report; ask the author when they are not
  at hand. A plausible guess presented as the report is worse than a
  question.
- For a feature: what it does and for which role at the client.
- "Before this commit, ... After this commit, ..." is a good shape when it
  fits.
- Wrap at about 72 characters. ASCII punctuation only: no em dash, curly
  quotes or ellipsis character.
- Never put client personal data, credentials, or database contents in a
  commit message.

### Trailers

- `Co-authored-by: Name <email>` when someone else wrote part of the change.
- The task is already linked by the header code. Odoo's own trailers
  (`task-123`, `opw-123`) point at Odoo's tracker; do not use them.

## Branches and pull requests

1. **Check the sync-back before branching.**

   ```bash
   git fetch origin
   git rev-list --count origin/stage..origin/main   # production commits missing on staging
   ```

   `0`: branch from `origin/main`. Anything else: the sync-back after the
   last release has not been done. Branch from `origin/stage` for the staging
   pull request, and tell the tech lead the sync-back is due. Never fix it by
   force-pushing `stage` or `main`.
2. **Branch name starts with the task code:** `ACME-0042`. If that branch
   already exists, add a suffix that keeps the code first:
   `ACME-0042-delivery-date`.
3. **Develop and test locally** on the branch.
4. **Before the pull request**, review the diff from the merge-base
   (`git diff origin/stage...HEAD`) with the `odoo-review` skill (rules pass,
   then merits pass) and audit it with `odoo-security`. Fix the findings or explain them in the pull request
   description.
5. **Pull request from the task branch into `stage`.** The description says
   why, as the commit message does, and names the task code. Merging is the
   tech lead's or the client's call: never merge your own pull request.
6. After the merge the task is tested on staging. Only tasks that pass are
   release candidates.
7. **Release:** a branch named by date, `release_DD_MM_YYYY`, carries the
   approved tasks' commits (merged or cherry-picked), and a pull request takes
   it into `main`.
8. After production takes the release, the tech lead syncs `stage` from
   `main`.

- Where a repository has a `demo` branch, a fix needed on the demo gets a
  second pull request from the same task branch into `demo`, on top of the
  one into `stage`.
- One logical change per commit, one module per commit unless the change is
  inseparable. Squash fixups into the commit they fix: a pull request carries
  only commits that should land.
- Update a task branch by rebasing it on its base and pushing with
  `--force-with-lease`. Never force-push `main`, `stage`, `demo` or a release
  branch, and never merge `stage` into a task branch.
- A bug fix comes with a test that reproduces it when one is possible.
- Never commit secrets, `.env` files, database dumps or exports of client
  data.
