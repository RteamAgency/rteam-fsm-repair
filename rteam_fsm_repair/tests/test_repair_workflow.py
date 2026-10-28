# Part of Rteam FSM Repair Workflow. See LICENSE file for full copyright and licensing details.

import base64

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

# Written the way the web client sends it: a base64 string. Odoo 20 refuses
# bytes for a binary field (they could be raw or base64).
PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32).decode()


@tagged("post_install", "-at_install")
class TestRepairWorkflow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.slot = cls.env["planning.slot"].create(
            {
                "start_datetime": "2026-11-02 08:00:00",
                "end_datetime": "2026-11-02 12:00:00",
                "partner_id": cls.partner.id,
                "x_request_type": "repair",
            }
        )

    def test_request_type_persists(self):
        self.assertEqual(self.slot.x_request_type, "repair")

    def test_send_protocol_without_signature_raises(self):
        with self.assertRaises(UserError):
            self.slot.action_send_repair_protocol()

    def test_send_protocol_opens_composer_on_the_visit(self):
        self.slot.x_customer_signature = PNG
        action = self.slot.action_send_repair_protocol()
        self.assertEqual(action["res_model"], "mail.compose.message")
        self.assertEqual(action["context"]["default_model"], "planning.slot")
        self.assertEqual(action["context"]["default_res_ids"], self.slot.ids)

    def test_signed_at_stamps_on_customer_signature(self):
        self.assertFalse(self.slot.x_signed_at)
        self.slot.x_customer_signature = PNG
        self.slot._onchange_customer_signature()
        self.assertTrue(self.slot.x_signed_at)

    def test_action_url_points_at_the_visit(self):
        url = self.slot._action_url()
        self.assertTrue(url.endswith(f"/odoo/planning.slot/{self.slot.id}"))

    def test_create_repair_order_links_both_ways(self):
        action = self.slot.action_create_repair_order()
        repair = self.slot.x_repair_order_id
        self.assertTrue(repair)
        self.assertEqual(action["res_id"], repair.id)
        self.assertEqual(repair.partner_id, self.partner)
        self.assertEqual(repair.fsm_slot_ids, self.slot)
        self.assertEqual(repair.fsm_slot_count, 1)
        visits = repair.action_view_fsm_slots()
        self.assertEqual(visits["res_model"], "planning.slot")
        self.assertEqual(visits["domain"], [("x_repair_order_id", "=", repair.id)])
        # A second click opens the linked order instead of creating another.
        self.assertEqual(self.slot.action_create_repair_order()["res_id"], repair.id)

    def test_protocol_report_renders_for_a_visit(self):
        self.slot.write(
            {
                "x_engineer_signature": PNG,
                "x_customer_signature": PNG,
                "x_signed_by": "Jane Customer",
            }
        )
        html, _type = self.env["ir.actions.report"]._render_qweb_html(
            "rteam_fsm_repair.action_report_repair_protocol", self.slot.ids
        )
        self.assertIn(b"Jane Customer", html)
        self.assertIn(self.partner.name.encode(), html)

    def test_protocol_email_renders_for_a_visit(self):
        template = self.env.ref("rteam_fsm_repair.mail_template_repair_protocol")
        self.assertEqual(template.model, "planning.slot")
        subject = template._render_field("subject", self.slot.ids)[self.slot.id]
        self.assertIn(self.slot.display_name, subject)
        body = template._render_field("body_html", self.slot.ids)[self.slot.id]
        self.assertIn(f"/odoo/planning.slot/{self.slot.id}", body)
