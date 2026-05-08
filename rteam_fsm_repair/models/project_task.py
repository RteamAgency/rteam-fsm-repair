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
    x_equipment_product_id = fields.Many2one(
        related="x_equipment_id.product_id",
        string="Equipment Product",
        store=False,
        readonly=True,
    )
    x_serial_lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Serial / Lot",
        tracking=True,
        help="Serial number of the unit being serviced (matches Equipment product).",
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

    @api.onchange("x_customer_signature")
    def _onchange_customer_signature(self):
        for rec in self:
            if rec.x_customer_signature and not rec.x_signed_at:
                rec.x_signed_at = fields.Datetime.now()

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
