# Part of Rteam FSM Repair Workflow. See LICENSE file for full copyright and licensing details.

from . import models


def _post_init_hook(env):
    """Link the repair protocol report to the email template.

    Done in a hook (not in XML) because Odoo's ref() inside <field eval="...">
    cannot reliably resolve xmlids defined in a sibling data file that was
    loaded earlier in the same install pass (cached _xmlid_to_res_id stays cold).
    Hooks run after all data files load, so both xmlids are committed.
    """
    template = env.ref(
        "rteam_fsm_repair.mail_template_repair_protocol",
        raise_if_not_found=False,
    )
    report = env.ref(
        "rteam_fsm_repair.action_report_repair_protocol",
        raise_if_not_found=False,
    )
    if template and report:
        template.report_template_ids = [(4, report.id)]
