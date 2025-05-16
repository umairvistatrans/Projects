# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    arabic_name = fields.Char(string="Arabic Name")
    product_attrs_name = fields.Char(compute='_get_full_attrs_name',store=True)

    @api.depends('product_template_attribute_value_ids')
    def _get_full_attrs_name(self):
        for rec in self:
            rec.product_attrs_name=','.join(str(item.name) for item in rec.product_template_attribute_value_ids)