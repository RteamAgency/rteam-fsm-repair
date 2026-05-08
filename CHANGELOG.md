# Changelog

All notable changes to this module are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## 1.1.1 - 2026-05-08 - Fix: encode non-ASCII as numeric HTML entities

### Fixed

- `static/description/index.html`: all non-ASCII characters (Cyrillic
  language names, German umlauts, Spanish &ntilde;, Romanian &abreve;,
  Arabic) converted to numeric HTML entities (`&#NNNN;`). The
  apps.odoo.com listing chrome mis-decodes raw UTF-8 in the description
  page and renders Cyrillic / Arabic as garbled Latin-1 sequences.

## 1.1.0 - 2026-05-08 - Multi-language localization + Technical Reference

### Added

- **Localization in 8 languages**: English, Russian, Ukrainian, German,
  Spanish, Romanian, Polish, Arabic. Every field, button, page label,
  selection value, and error message translated. Drop-in for international
  rollouts.
- **Technical Reference section** in module description and listing page:
  explicit list of every new field, page, button, smart-button, report,
  template, and hook the module adds, with technical names and the views
  they appear in.

### Changed

- Banner localization tile: replaced "Ukrainian localization" with
  "Localized in 8 languages" + visible language list (EN / RU / UK / DE /
  ES / RO / PL / AR).
- About-Rteam attribution rewritten to reflect global Odoo partner
  positioning (manufacturers, equipment dealers, distribution companies
  across the EU, UK, UAE, Ukraine) instead of "consultancy in Ukraine".

## 1.0.1 - 2026-05-08 - Store assets aligned with Rteam family design

### Changed

- Store icon (`static/description/icon.png`) and banner
  (`static/description/banner.png`) redesigned to match the Light + Gradient
  identity used by Odoo Health Check and Rteam AI Bot listings: violet-to-teal
  signature gradient on the F monogram, solid teal `+` marker, light surface
  background with violet/teal blob auras, "by Rteam" gradient attribution.
- Banner right side: 4 feature tiles (Tablet signatures, FSM <-> Repair bridge,
  Multi-visit cases, Ukrainian localization) replacing the prior bullet list.

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
