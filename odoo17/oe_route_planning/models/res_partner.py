# -*- coding: utf-8 -*-
from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    rank_id = fields.Many2one('oe.rank.master', string='Rank', tracking=True)
    route_id = fields.Many2one("oe.route.master", 'Route', tracking=True)
