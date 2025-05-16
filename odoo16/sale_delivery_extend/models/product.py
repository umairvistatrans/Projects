# -*- coding: utf-8 -*-
from odoo import models, fields,api,exceptions
from datetime import datetime,date

class template(models.Model):
    _inherit = 'product.template'
    price_type = fields.Selection(string="Price Type", selection=[('h', 'Heavy'), ('l', 'light'), ], required=False, default='h')
    price_val = fields.Float('Price Value')