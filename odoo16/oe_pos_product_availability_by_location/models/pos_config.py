# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    oe_product_availability = fields.Boolean('Product Availability', default=False)
