# Part of Rteam FSM Repair Workflow. See LICENSE file for full copyright and licensing details.
"""19.0 -> 20.0: carry the Repair data of field service tasks over to shifts.

Up to 19.0 the Repair fields live on ``project.task`` (``industry_fsm``).
Odoo 20 plans a visit as a ``planning.slot`` (``planning_field_service``)
and this module moved its fields there. At the end-migrate step the old
columns of ``project_task`` are still in the database: the ORM drops them
right after, in ``ir.model.data._process_end``.

How Odoo's own upgrade turns a field service task into a shift is not
documented, so the only link trusted here is ``planning_slot.task_id``
(``project_forecast``):

1. every task holding Repair data is copied into ``rteam_fsm_repair_legacy_task``,
   which stays in the database as the record of what was there and where
   it went;
2. a task with exactly one shift pointing at it hands its values and its
   signatures to that shift;
3. any other task keeps its data as a note in its own chatter with the
   signatures attached, and its repair order gets a note naming the visit,
   so the case history stays readable.
"""

import logging

from markupsafe import Markup
from odoo import SUPERUSER_ID, Command, api
from odoo.tools import SQL
from odoo.tools.sql import column_exists, table_exists

_logger = logging.getLogger(__name__)

LEGACY_TABLE = "rteam_fsm_repair_legacy_task"
VALUE_COLUMNS = (
    "x_request_type",
    "x_equipment_id",
    "x_serial_lot_id",
    "x_problem_description",
    "x_findings",
    "x_resolution",
    "x_signed_by",
    "x_signed_at",
    "x_repair_order_id",
)
SIGNATURE_FIELDS = {
    "x_engineer_signature": "Engineer signature",
    "x_customer_signature": "Customer signature",
}
REQUEST_TYPES = {
    "installation": "Installation",
    "repair": "Repair",
    "diagnostic": "Diagnostic",
    "maintenance": "Preventive Maintenance",
    "rma": "RMA",
}
HTML_LABELS = (
    ("x_problem_description", "Problem Description"),
    ("x_findings", "Engineer Findings"),
    ("x_resolution", "Resolution / Work Done"),
)


def migrate(cr, version):
    if not version or not table_exists(cr, "project_task"):
        return
    if table_exists(cr, LEGACY_TABLE):
        _logger.warning(
            "rteam_fsm_repair: %s already exists, Repair data not moved again", LEGACY_TABLE
        )
        return
    columns = [c for c in VALUE_COLUMNS if column_exists(cr, "project_task", c)]
    found = _snapshot(cr, columns)
    if not found:
        _logger.info("rteam_fsm_repair: no field service task held Repair data")
        return
    moved = _move_to_shifts(cr, columns)
    kept = _keep_on_tasks(cr, columns)
    message = (
        "rteam_fsm_repair: %s field service task(s) held Repair data: %s moved to their "
        "planning shift, %s kept as a note on the task; all listed in table %s"
    )
    log = _logger.warning if kept else _logger.info
    log(message, found, moved, kept, LEGACY_TABLE)


def _snapshot(cr, columns):
    """Copy every task holding Repair data into the legacy table."""
    has_value = [SQL("t.%s IS NOT NULL", SQL.identifier(c)) for c in columns]
    has_value.append(
        SQL(
            """EXISTS (SELECT 1 FROM ir_attachment a
                        WHERE a.res_model = 'project.task' AND a.res_id = t.id
                          AND a.res_field IN %s)""",
            tuple(SIGNATURE_FIELDS),
        )
    )
    select = [SQL("t.id AS task_id")]
    select += [SQL("t.%s", SQL.identifier(c)) for c in columns]
    cr.execute(
        SQL(
            """CREATE TABLE %(legacy)s AS
               SELECT %(select)s,
                      NULL::integer AS slot_id,
                      NULL::varchar AS outcome,
                      (now() AT TIME ZONE 'UTC') AS migrated_at
                 FROM project_task t
                WHERE %(has_value)s""",
            legacy=SQL.identifier(LEGACY_TABLE),
            select=SQL(", ").join(select),
            has_value=SQL(" OR ").join(has_value),
        )
    )
    found = cr.rowcount
    cr.execute(SQL("ALTER TABLE %s ADD PRIMARY KEY (task_id)", SQL.identifier(LEGACY_TABLE)))
    return found


def _move_to_shifts(cr, columns):
    """Hand the values and signatures of a task to its only shift."""
    if not column_exists(cr, "planning_slot", "task_id"):
        return 0
    legacy = SQL.identifier(LEGACY_TABLE)
    cr.execute(
        SQL(
            """UPDATE %(legacy)s l
                  SET slot_id = s.slot_id, outcome = 'moved to the shift'
                 FROM (SELECT task_id, min(id) AS slot_id
                         FROM planning_slot
                        WHERE task_id IS NOT NULL
                        GROUP BY task_id
                       HAVING count(*) = 1) s
                WHERE s.task_id = l.task_id""",
            legacy=legacy,
        )
    )
    moved = cr.rowcount
    if not moved:
        return 0
    if columns:
        cr.execute(
            SQL(
                "UPDATE planning_slot s SET %(sets)s FROM %(legacy)s l WHERE l.slot_id = s.id",
                sets=SQL(", ").join(
                    SQL("%(c)s = COALESCE(s.%(c)s, l.%(c)s)", c=SQL.identifier(c)) for c in columns
                ),
                legacy=legacy,
            )
        )
    cr.execute(
        SQL(
            """UPDATE ir_attachment a
                  SET res_model = 'planning.slot', res_id = l.slot_id
                 FROM %(legacy)s l
                WHERE l.slot_id IS NOT NULL
                  AND a.res_model = 'project.task'
                  AND a.res_id = l.task_id
                  AND a.res_field IN %(fields)s
                  AND NOT EXISTS (SELECT 1 FROM ir_attachment b
                                   WHERE b.res_model = 'planning.slot'
                                     AND b.res_id = l.slot_id
                                     AND b.res_field = a.res_field)""",
            legacy=legacy,
            fields=tuple(SIGNATURE_FIELDS),
        )
    )
    return moved


def _keep_on_tasks(cr, columns):
    """Log the Repair data of every task left without a shift in its chatter."""
    legacy = SQL.identifier(LEGACY_TABLE)
    if column_exists(cr, "planning_slot", "task_id"):
        outcome = SQL(
            """CASE WHEN EXISTS (SELECT 1 FROM planning_slot s WHERE s.task_id = l.task_id)
                    THEN 'note on the task: several shifts'
                    ELSE 'note on the task: no shift' END"""
        )
    else:
        outcome = SQL("'note on the task: shifts have no task link'")
    cr.execute(
        SQL(
            "UPDATE %(legacy)s l SET outcome = %(outcome)s WHERE l.slot_id IS NULL",
            legacy=legacy,
            outcome=outcome,
        )
    )
    kept = cr.rowcount
    if not kept:
        return 0

    env = api.Environment(cr, SUPERUSER_ID, {})
    if "project.task" not in env:
        cr.execute(
            SQL(
                "UPDATE %s SET outcome = 'kept in this table only' WHERE slot_id IS NULL",
                legacy,
            )
        )
        return kept

    cr.execute(
        SQL(
            "SELECT %(cols)s FROM %(legacy)s WHERE slot_id IS NULL ORDER BY task_id",
            cols=SQL(", ").join(SQL.identifier(c) for c in ["task_id", *columns]),
            legacy=legacy,
        )
    )
    rows = cr.dictfetchall()

    cr.execute(
        SQL(
            """SELECT id, res_id, res_field, mimetype
                 FROM ir_attachment
                WHERE res_model = 'project.task'
                  AND res_field IN %(fields)s
                  AND res_id IN %(tasks)s
                ORDER BY id""",
            fields=tuple(SIGNATURE_FIELDS),
            tasks=tuple(row["task_id"] for row in rows),
        )
    )
    signatures = {}
    for att_id, task_id, res_field, mimetype in cr.fetchall():
        extension = ".png" if mimetype == "image/png" else ""
        cr.execute(
            "UPDATE ir_attachment SET res_field = NULL, name = %s WHERE id = %s",
            (SIGNATURE_FIELDS[res_field] + extension, att_id),
        )
        signatures.setdefault(task_id, []).append(att_id)

    bodies = {row["task_id"]: _task_note(env, row) for row in rows}
    tasks = env["project.task"].with_context(active_test=False).browse(list(bodies))
    tasks._message_log_batch(
        bodies,
        attachment_ids={
            task_id: [Command.link(att_id) for att_id in signatures.get(task_id, [])]
            for task_id in bodies
        },
    )

    visits_by_order = {}
    for row in rows:
        if row.get("x_repair_order_id"):
            visits_by_order.setdefault(row["x_repair_order_id"], []).append(row["task_id"])
    if visits_by_order:
        orders = env["repair.order"].browse(list(visits_by_order)).exists()
        orders._message_log_batch(
            {order.id: _order_note(env, visits_by_order[order.id]) for order in orders}
        )
    return kept


def _task_note(env, row):
    lines = []
    if row.get("x_request_type"):
        label = REQUEST_TYPES.get(row["x_request_type"], row["x_request_type"])
        lines.append(("Request Type", label))
    for column, model, label in (
        ("x_equipment_id", "maintenance.equipment", "Equipment"),
        ("x_serial_lot_id", "stock.lot", "Serial / Lot"),
        ("x_repair_order_id", "repair.order", "Repair Order"),
    ):
        if row.get(column):
            record = env[model].browse(row[column]).exists()
            lines.append((label, record.display_name if record else f"#{row[column]}"))
    if row.get("x_signed_by"):
        lines.append(("Signed By (Customer Name)", row["x_signed_by"]))
    if row.get("x_signed_at"):
        lines.append(("Signed At (UTC)", str(row["x_signed_at"])))

    body = Markup(
        "<p>Repair data of this field service visit, kept by FSM + Repair when the "
        "database moved to Odoo 20: no single planning shift was linked to this task.</p>"
    )
    if lines:
        body += Markup("<ul>%s</ul>") % Markup().join(
            Markup("<li><b>%s</b>: %s</li>") % (label, value) for label, value in lines
        )
    for column, label in HTML_LABELS:
        if row.get(column):
            # Html fields were sanitized when saved; the message body is sanitized again.
            body += Markup("<p><b>%s</b></p>%s") % (label, Markup(row[column]))
    return body


def _order_note(env, task_ids):
    tasks = env["project.task"].with_context(active_test=False).browse(task_ids)
    links = Markup(", ").join(
        Markup('<a href="/odoo/project.task/%s">%s</a>') % (task.id, task.display_name)
        for task in tasks
    )
    return (
        Markup(
            "<p>Field service visit(s) of this case from before Odoo 20, not linked to a "
            "planning shift: %s. Their Repair data is in a note on each task.</p>"
        )
        % links
    )
