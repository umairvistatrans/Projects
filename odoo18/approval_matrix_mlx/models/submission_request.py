# -*- coding: utf-8 -*-

from . import approval_core

# Odoo imports
from odoo import models, fields, api, _


class SubmissionRequest(models.Model):
    _inherit = 'submission.request'

    is_dynamic_approver = fields.Boolean(string='Dynamic Approver', compute='_compute_dynamic_approver')
    approval_sequence = fields.Integer()
    approval_activity_ids = fields.Many2many(
        string="Activities",
        comodel_name='mail.activity',
        relation='rel_account_activity',
        column1='account_ref',
        column2='activity_ref',
        copy=False
    )
    ref_approval_id = fields.Many2one('dynamic.approval.configuration', string="Approval Reference")
    approver_ids = fields.One2many('approval.approver.submission.request', 'submission_request_id', string="Approvers")

    def _compute_dynamic_approver(self):
        """
        this compute method will set a Boolean check if logged in user exists in dynamic approval configuration line users.
        """
        user = self.env.user
        for order in self:
            approval_core._compute_dynamic_approver(order, user)

    def get_dynamic_approvals(self, domain=[]):
        """
        this method will reads the configuration lines for approval flow.
        """
        for order in self:
            return approval_core.get_dynamic_approvals(order, 'request', self.submission_type, domain)

    def action_reset_history(self):
        for order in self:
            approval_core.action_reset_history(order)

    def action_roll_approvers(self, approval_id):
        """
        this method actually rolls a user if logged in user exist in next configuration line users.
        """
        user_id = self.env.user.id
        return approval_core.action_roll_approvers(self, approval_id, user_id)

    def set_approval_history(self, approval_id):
        """
        this method saves some history, for the different approval stages.
        """
        for order in self:
            approval_core.set_approval_history(order, approval_id, order._action_confirm)

    def get_approver_users(self, approval_id):
        """
        this method gets all user for a approval line and return those users object.
        """
        return approval_core.get_approver_users(self, approval_id)

    def get_activities(self, approval_id):
        """
        this method creates all required activities in the system for approver users.
        """
        return approval_core.get_activities(self, approval_id)

    def action_confirm(self):
        self.ensure_one()
        approval_id = self.get_dynamic_approvals()
        if approval_id:
            for appr_conf in approval_id:
                self.env['approval.approver.submission.request'].create({
                    'submission_request_id': self.id,
                    'user_ids': [(6, 0, appr_conf._get_user_ids().ids)],
                    'state': 'pending'
                })

            approval_core._mark_approvers(self)

            approval_id = approval_id[0]
            self.state = 'in_approval'
            return self.set_approval_history(approval_id)
        return self._action_confirm()

    def action_dynamic_approval(self, msg=False):
        """
        this is the actual method which being called and executed for dynamic approval flow.
        """
        for order in self:
            approval_core.action_dynamic_approval(order, order._action_confirm, msg)

    def action_log_note(self, msg):
        """
        this method will create a log note from odoobot.
        whenever approval configuration line is deleted from company form.
        """
        approval_core.action_log_note(self, msg)

    @api.model_create_multi
    def create(self, vals_list):
        requests = super(SubmissionRequest, self).create(vals_list)
        for request in requests:
            request.action_confirm()
        return requests

    # def action_refuse(self):
    #     """
    #     this method will refuse and reset to draft the record.
    #     """
    #     self.ensure_one()
    #     self.state = 'draft'
    #     self.button_cancel()
    #     self.button_draft()
    #     if self.ref_approval_id:
    #         self.action_done_activity(self.approval_activity_ids)
    #     self.action_reset_history()
    #     self.approver_ids.unlink()
    #
    # def button_draft(self):
    #     for order in self:
    #         order.approver_ids.unlink()
    #     return super().button_draft()
    #
    # def button_cancel(self):
    #     for order in self:
    #         order.approver_ids.unlink()
    #     return super().button_cancel()

    def action_done_activity(self, activities):
        return approval_core.action_done_activity(self, activities)


class ApprovalApproverSubmission(models.Model):
    _name = 'approval.approver.submission.request'
    _description = 'Approvers Submission Request'

    submission_request_id = fields.Many2one('submission.request', string='Submission Request', ondelete='cascade')
    user_ids = fields.Many2many('res.users')
    approved_by = fields.Many2one('res.users')
    approval_date = fields.Datetime()
    state = fields.Selection([
        ('pending', 'To Approve'),
        ('approved', 'Approved')], string="Status", default="new", readonly=True)
