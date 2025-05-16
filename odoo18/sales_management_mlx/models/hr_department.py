# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_type = fields.Selection([
        ('sourcing', 'Sourcing'),
        ('merchandise', 'Merchandise'),
        ('sales', 'Sales'),
        ('quality_control', 'Quality Control'),
        ('logistics', 'Logistics'),
    ], string="Type", tracking=True, copy=False)
