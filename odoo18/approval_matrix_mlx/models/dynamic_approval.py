# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DynamicApproval(models.Model):
    _name = 'dynamic.approval'
    _description = 'Dynamic Approval Configuration'

    name = fields.Char(string='Description', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    approval_conf_ids = fields.One2many('dynamic.approval.configuration', 'conf_id')
    process_by = fields.Selection(string='Approval Process By',
                                  selection=[('user', 'Users'),
                                             ('department', 'Departments')],
                                  default='user', required=True)
    approval_medium = fields.Selection([
        ('request', 'Requests'),
    ], string='Approval Medium', required=True, help='Select the approval medium on which the configurations defined will be applied')
    submission_type = fields.Selection([
        ('supplier', 'Supplier'),
        ('factory', 'Factory'),
        ('product', 'Product'),
        ('category', 'Category'),
    ], string="Submission Type", copy=False)

    @api.constrains('approval_medium', 'submission_type')
    def _check_unique_combination(self):
        for record in self:
            # Check if another record with the same pay_group and approval_medium exists
            domain = [
                ('id', '!=', record.id),
                ('approval_medium', '=', record.approval_medium),
                ('company_id', '=', record.company_id.id)
            ]
            if record.approval_medium == 'request':
                domain += [('submission_type', '=', record.submission_type)]
            existing_record = self.search(domain)
            if existing_record:
                raise ValidationError(
                    _("A configuration with the same Approval Medium already exists. Please modify the existing configuration instead of creating a new one."))

    def unlink(self):
        for approval_conf in self:
            for approval in approval_conf.approval_conf_ids:
                msg_pre = "The approval configurations were modified, "
                msg_post = "is automatically approved and moved to the next configuration/stage."
                submission_requests = self.env['submission.request'].search([('ref_approval_id', '=', approval.id)])
                if submission_requests:
                    submission_requests.action_dynamic_approval(msg_pre + " So Submission Request " + msg_post)
        return super(DynamicApproval, self).unlink()

    def write(self, vals):
        res = super(DynamicApproval, self).write(vals)
        if self.process_by == 'department':
            self.approval_conf_ids.write({'user_ids': False})
        else:
            self.approval_conf_ids.write({'department_ids': False})
        return res


class DynamicApprovalConfiguration(models.Model):
    _name = 'dynamic.approval.configuration'
    _description = 'Dynamic Approval Configuration'

    conf_id = fields.Many2one('dynamic.approval')
    company_id = fields.Many2one('res.company', string='Company', related='conf_id.company_id')
    process_by = fields.Selection(related='conf_id.process_by')
    user_ids = fields.Many2many('res.users', string='Users')
    department_ids = fields.Many2many('hr.department', string='Departments')
    sequence = fields.Integer()
    approval_medium = fields.Selection(related='conf_id.approval_medium')
    submission_type = fields.Selection(related='conf_id.submission_type')

    def _get_user_ids(self):
        """Fetch user_ids based on the selected process_by option."""
        if self.process_by == 'department':
            all_departments = self.department_ids

            # Recursively find all child departments
            def fetch_child_departments(departments):
                child_departments = self.env['hr.department'].search([('parent_id', 'in', departments.ids)])
                if child_departments:
                    return child_departments + fetch_child_departments(child_departments)
                return self.env['hr.department']

            all_departments |= fetch_child_departments(self.department_ids)
            # Find employees associated with all collected departments
            employees = self.env['hr.employee'].search([('department_id', 'in', all_departments.ids)])

            # Filter employees with linked users and return their user_ids
            user_ids = employees.mapped('user_id')
            return user_ids

        return self.user_ids

    def unlink(self):
        for approval in self:
            msg_pre = "The approval configurations were modified, "
            msg_post = "is automatically approved and moved to the next configuration/stage."
            submission_requests = self.env['submission.request'].search([('ref_approval_id', '=', approval.id)])
            if submission_requests:
                submission_requests.action_dynamic_approval(msg_pre + " So Submission Request " + msg_post)
        return super(DynamicApprovalConfiguration, self).unlink()
