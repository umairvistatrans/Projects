# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OERankMaster(models.Model):
    _name = "oe.rank.master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rank Master'
    _rec_name = "name"

    name = fields.Char(string='Rank', required=True, tracking=True)
    no_of_visits = fields.Char(string='No of Visits', tracking=True)
    visit_duration = fields.Selection(
        selection=[('weekly', "Weekly"), ('bi_weekly', "Bi-Weekly"), ('monthly', "Monthly"),
                   ('Bi_monthly', "Bi-Monthly"), ('quarterly', "Quarterly")], string="Visit Duration", tracking=True)
