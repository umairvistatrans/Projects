# -*- coding: utf-8 -*-

import markupsafe
import datetime

# Odoo imports
from odoo.exceptions import UserError
from odoo import _


def _compute_dynamic_approver(self, user):
    """
    this compute method will set a Boolean check if logged in user exists in dynamic approval configuration line users.
    """
    for order in self:
        order.is_dynamic_approver = False
        if order.ref_approval_id:
            approval_id = order.get_dynamic_approvals(('sequence', '=', order.approval_sequence))
            users = self.get_approver_users(approval_id)
            if users:
                if user.id in users.ids:
                    order.is_dynamic_approver = True

def get_dynamic_approvals(self, medium, submission_type, domain=[]):
    for order in self:
        if order.company_id and order.company_id.dynamic_approval_ids:
            domains = [
                ('company_id', '=', order.company_id.id),
                ('approval_medium', '=', medium),
            ]
            if medium == 'request':
                domains += [('submission_type', '=', submission_type)]
            if len(domain):
                domains += [domain]
            return self.env['dynamic.approval.configuration'].search(domains, order='sequence ASC')
        return False

def action_reset_history(self):
    for order in self:
        order.ref_approval_id = None
        order.approval_sequence = None
        order.approval_activity_ids = None

def action_roll_approvers(self, approval_id, user_id):
    """
    this method actually rolls a user if logged in user exist in next configuration line users.
    """
    is_generating_approval_history = False
    while True:
        users = self.get_approver_users(approval_id)
        if users:
            if user_id not in users.ids:
                is_generating_approval_history = True
                break
            approval_id = self.get_dynamic_approvals(('sequence', '=', approval_id.sequence + 1))
            if not approval_id:
                break
    if is_generating_approval_history:
        return approval_id
    else:
        return False

def set_approval_history(order, approval_id, approve):
    """
    this method saves some history, for the different approval stages.
    """
    order.action_reset_history()
    approval_id = order.action_roll_approvers(approval_id)
    if approval_id:
        activities = order.get_activities(approval_id)
        order.sudo().write({
            'ref_approval_id': approval_id.id,
            'approval_sequence': approval_id.sequence,
            'approval_activity_ids': [(6, 0, activities)],
        })
    else:
        return approve()

def get_approver_users(self, approval_id):
    """
    this method gets all user for a approval line and return those users object.
    """
    if approval_id:
        return approval_id._get_user_ids()
    return False

def _mark_approvers(self):
    current_user = self.env.user
    def update_pending_approver(pending_approvers):
        for i in range(len(pending_approvers)):
            if current_user in pending_approvers[i].user_ids:
                pending_approvers[i].approved_by = current_user.id
                pending_approvers[i].approval_date = datetime.datetime.now()
                pending_approvers[i].state = 'approved'
            else:
                break

    pending_approvers = self.approver_ids.sorted(key=lambda r: r.id).filtered(lambda r: r.state == 'pending')
    if pending_approvers:
        update_pending_approver(pending_approvers)

def get_activities(self, approval_id):
    """
    this method creates all required activities in the system for approver users.
    """
    type_id = self.env['mail.activity.type'].search([('name', '=', 'To-Do')], limit=1)
    if not type_id:
        raise UserError("Unable to create activity for users, Please create a type with 'To-Do' name.")
    users = self.get_approver_users(approval_id)
    msg = ''
    if self._name == 'purchase.order':
        msg = 'RFQ'
    if self._name == 'account.move':
        msg = 'Invoice'
    if self._name == 'account.payment':
        msg = 'Payment'
    reference = self.rfq_reference if self._name == 'purchase.order' else self.name
    note = 'Please Approve ' + msg + ' (' + reference + ').'
    activities = []
    if users:
        for user in users:
            activity_vals = {
                'activity_type_id': type_id.id,
                'res_id': self.id,
                'res_model_id': self.env['ir.model']._get(self._name).id,
                'user_id': user.id,
                'automated': True,
                'note': note,
            }
            activity = self.env['mail.activity'].create(activity_vals)
            activities.append(activity.id)
    return activities

def action_dynamic_approval(order, approve, msg=False):
    """
    this is the actual method which being called and executed for dynamic approval flow.
    """
    _mark_approvers(order)

    if msg:
        order.action_log_note(msg)
    if order.ref_approval_id:
        order.action_done_activity(order.approval_activity_ids)
        approval_id = order.get_dynamic_approvals(('sequence', '=', order.approval_sequence + 1))
        if approval_id:
            order.set_approval_history(approval_id)
        else:
            order.action_reset_history()
            return approve()
    else:
        order.action_reset_history()
        return approve()

def action_log_note(self, note):
    """
    this method will create a log note from odoobot.
    """
    for order in self:
        msg = _('%(note)s <br></br>', note=note)
        order.message_post(
            body=markupsafe.Markup(msg),
            message_type='comment',
            author_id=self.env.ref('base.partner_root').id
        )

def action_refuse(self):
    """
    this method will refuse and reset to draft the record.
    """
    for order in self:
        order.button_cancel()
        order.button_draft()
        if order.ref_approval_id:
            activities = order.approval_activity_ids
            order.action_done_activity(activities)
        order.action_reset_history()

def action_done_activity(self, activities):
    """
    this method will mark all activities done.
    """
    if activities:
        activities.action_done()
