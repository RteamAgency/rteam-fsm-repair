# Part of Rteam FSM Repair Workflow. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError

REQUEST_TYPES = [
    ("installation", "Installation"),
    ("repair", "Repair"),
    ("diagnostic", "Diagnostic"),
    ("maintenance", "Preventive Maintenance"),
    ("rma", "RMA"),
]


class ProjectTask(models.Model):
    _inherit = "project.task"

    x_request_type = fields.Selection(
        selection=REQUEST_TYPES,
        string="Request Type",
        tracking=True,
        help="Classifies the on-site visit. Drives reporting and SLA filters.",
    )

    x_equipment_id = fields.Many2one(
        comodel_name="maintenance.equipment",
        string="Equipment",
        tracking=True,
        help="Installed unit being serviced. Links to its lifecycle history.",
    )
    x_equipment_serial_no = fields.Char(
        related="x_equipment_id.serial_no",
        string="Equipment S/N",
        store=False,
        readonly=True,
    )
    x_serial_lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Serial / Lot",
        tracking=True,
        help="Optional: stock.lot record for the unit being serviced.",
    )

    x_problem_description = fields.Html(string="Problem Description")
    x_findings = fields.Html(string="Engineer Findings")
    x_resolution = fields.Html(string="Resolution / Work Done")

    x_engineer_signature = fields.Binary(
        string="Engineer Signature",
        attachment=True,
    )
    x_customer_signature = fields.Binary(
        string="Customer Signature",
        attachment=True,
    )
    x_signed_by = fields.Char(string="Signed By (Customer Name)")
    x_signed_at = fields.Datetime(string="Signed At", readonly=True)

    x_repair_order_id = fields.Many2one(
        comodel_name="repair.order",
        string="Repair Order",
        tracking=True,
        index=True,
        help=(
            "Persistent repair case this on-site visit belongs to. One repair "
            "order can span multiple FSM visits + in-shop work + RMA escalation."
        ),
    )

    @api.onchange("x_customer_signature")
    def _onchange_customer_signature(self):
        for rec in self:
            if rec.x_customer_signature and not rec.x_signed_at:
                rec.x_signed_at = fields.Datetime.now()

    def _action_url(self):
        """Return a deep-link to this task's form view (used by mail templates)."""
        self.ensure_one()
        base = self.get_base_url()
        action = self.env.ref(
            "industry_fsm.project_task_action_fsm",
            raise_if_not_found=False,
        ) or self.env.ref(
            "project.action_view_task",
            raise_if_not_found=False,
        )
        if not action:
            return base
        return f"{base}/odoo/action-{action.id}/{self.id}"

    def action_create_repair_order(self):
        """Create a new repair.order from this FSM task and link them.

        Pre-fills customer + product (if equipment has one resolvable via lot)
        + lot/serial. Opens the new repair.order in form view for the user
        to complete (parts, schedule, etc.).
        """
        self.ensure_one()
        if self.x_repair_order_id:
            return self.action_open_repair_order()
        repair_vals = {
            "partner_id": self.partner_id.id if self.partner_id else False,
            "company_id": self.company_id.id,
            "user_id": self.env.user.id,
            "internal_notes": self.x_problem_description or False,
        }
        if self.x_serial_lot_id:
            repair_vals["lot_id"] = self.x_serial_lot_id.id
            repair_vals["product_id"] = self.x_serial_lot_id.product_id.id
        repair = self.env["repair.order"].create(repair_vals)
        self.x_repair_order_id = repair.id
        return {
            "type": "ir.actions.act_window",
            "name": _("Repair Order"),
            "res_model": "repair.order",
            "res_id": repair.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_repair_order(self):
        self.ensure_one()
        if not self.x_repair_order_id:
            raise UserError(_("This task is not linked to any Repair Order."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Repair Order"),
            "res_model": "repair.order",
            "res_id": self.x_repair_order_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_send_repair_protocol(self):
        self.ensure_one()
        if not self.x_customer_signature:
            raise UserError(_("Customer signature is required before sending the protocol."))
        template = self.env.ref(
            "rteam_fsm_repair.mail_template_repair_protocol",
            raise_if_not_found=False,
        )
        if not template:
            raise UserError(_("Protocol email template is missing."))
        compose_form = self.env.ref(
            "mail.email_compose_message_wizard_form",
            raise_if_not_found=False,
        )
        ctx = {
            "default_model": "project.task",
            "default_res_ids": self.ids,
            "default_use_template": True,
            "default_template_id": template.id,
            "default_composition_mode": "comment",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id if compose_form else False, "form")],
            "view_id": compose_form.id if compose_form else False,
            "target": "new",
            "context": ctx,
        }
