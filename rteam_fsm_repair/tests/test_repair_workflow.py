# Part of Rteam FSM Repair Workflow. See LICENSE file for full copyright and licensing details.

import base64

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRepairWorkflow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test FSM Repair",
                "is_fsm": True,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "T-001 Test Repair",
                "project_id": cls.project.id,
                "partner_id": cls.partner.id,
                "x_request_type": "repair",
            }
        )

    def test_request_type_persists(self):
        self.assertEqual(self.task.x_request_type, "repair")

    def test_send_protocol_without_signature_raises(self):
        with self.assertRaises(UserError):
            self.task.action_send_repair_protocol()

    def test_signed_at_stamps_on_customer_signature(self):
        self.assertFalse(self.task.x_signed_at)
        png = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
        self.task.x_customer_signature = png
        self.task._onchange_customer_signature()
        self.assertTrue(self.task.x_signed_at)

    def test_action_url_returns_string(self):
        url = self.task._action_url()
        self.assertIsInstance(url, str)
        self.assertIn("/odoo/", url)
