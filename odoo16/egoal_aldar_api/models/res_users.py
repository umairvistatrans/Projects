# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import string
from secrets import choice

import logging
_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    egoal_aldar_token = fields.Char(string="E-GOAL – ALDAR Token", readonly=1)
    odoo_server_url = fields.Char(
        string="Server URL", default=lambda self: self.env.company.get_base_url(), readonly=1
    )
    oe_config_ids = fields.Many2many('pos.config',  'oe_res_users_pos_config_rel', string='Point of Sale')

    def _check_egoal_aldar_token(self, token):
        return self.env['res.users'].search([('egoal_aldar_token', '=', token)], limit=1)

    def generate_egoal_aldar_token(self, length=120):
        token = 'odoo_' + ''.join(choice(string.ascii_letters + string.digits) for _i in range(length))
        res_users = self.env['res.users'].search([('egoal_aldar_token', '=', token)])
        if res_users:
            self.generate_egoal_aldar_token()
        else:
            self.egoal_aldar_token = token
