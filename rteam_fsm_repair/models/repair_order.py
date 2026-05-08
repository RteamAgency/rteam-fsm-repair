# Part of Rteam FSM Repair Workflow. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    fsm_task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="x_repair_order_id",
        string="Field Service Visits",
        help="On-site visits associated with this repair case.",
    )
    fsm_task_count = fields.Integer(
        string="Visits Count",
        compute="_compute_fsm_task_count",
    )

    def _compute_fsm_task_count(self):
        for rec in self:
            rec.fsm_task_count = len(rec.fsm_task_ids)

    def action_view_fsm_tasks(self):
        self.ensure_one()
        action = self.env.ref(
            "industry_fsm.project_task_action_fsm",
            raise_if_not_found=False,
        ) or self.env.ref("project.action_view_task")
        result = action.sudo().read()[0]
        result.update(
            {
                "domain": [("x_repair_order_id", "=", self.id)],
                "context": {
                    "default_x_repair_order_id": self.id,
                    "default_partner_id": self.partner_id.id if self.partner_id else False,
                    "default_x_serial_lot_id": self.lot_id.id if self.lot_id else False,
                },
                "name": _("Field Visits - %s", self.name or ""),
            }
        )
        return result
