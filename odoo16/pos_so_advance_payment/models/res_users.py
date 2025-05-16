# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api, _

class res_users(models.Model):
    _inherit = 'res.users'

    display_sale_widget = fields.Boolean(default=True)
    warehouse_ids = fields.Many2many('stock.warehouse')
    pos_config_ids = fields.Many2many('pos.config')
    default_config_id = fields.Many2one('pos.config', domain="[('id', 'in', pos_config_ids)]")