# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ApprovalRefuseNotification(models.TransientModel):
    _name = "approval.refuse.notification"
    _description = "Approval Refuse Notification"

    reason = fields.Text(string="Reason", required=True)

    def action_refuse(self):
        active_model = self.env.context.get('active_model')
        application = self.env[active_model].browse(self.env.context.get('active_id'))
        application = application.sudo()
        application._action_refuse()

        template = self.env.ref('portal_management_mlx.email_template_submission_refused')
        if template:
            template.with_context(refusal_reason=self.reason).send_mail(application.id, force_send=True)
