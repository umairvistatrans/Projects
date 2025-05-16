# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    dynamic_approval_ids = fields.One2many('dynamic.approval', 'company_id', string='Dynamic Approval')
