# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UsersInherit(models.Model):
    _inherit = 'res.users'

    is_merchandiser = fields.Boolean(default=False)