# Part of Rteam FSM Repair Workflow. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    fsm_slot_ids = fields.One2many(
        comodel_name="planning.slot",
        inverse_name="x_repair_order_id",
        string="Field Service Visits",
        help="On-site visits associated with this repair case.",
    )
    fsm_slot_count = fields.Integer(
        string="Visits Count",
        compute="_compute_fsm_slot_count",
    )

    @api.depends("fsm_slot_ids")
    def _compute_fsm_slot_count(self):
        for rec in self:
            rec.fsm_slot_count = len(rec.fsm_slot_ids)

    def action_view_fsm_slots(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Field Visits - %s", self.name or ""),
            "res_model": "planning.slot",
            "view_mode": "list,form",
            "domain": [("x_repair_order_id", "=", self.id)],
            "context": {
                "default_x_repair_order_id": self.id,
                "default_partner_id": self.partner_id.id if self.partner_id else False,
                "default_x_serial_lot_id": self.lot_id.id if self.lot_id else False,
            },
        }
