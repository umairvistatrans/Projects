# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    arabic_name = fields.Char(string="Arabic Name")

    # Override Create Function
    @api.model_create_multi
    def create(self,values):
        product_ids = super(ProductTemplate,self).create(values)

        # Check if there is variants
        for product_id in product_ids:
            if product_id.product_variant_id:
                product_id.product_variant_id.arabic_name = product_id.arabic_name

        return product_ids
