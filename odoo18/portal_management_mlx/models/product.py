# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    product_image_1 = fields.Binary(string="Product Image 1", copy=False)
    product_image_2 = fields.Binary(string="Product Image 2", copy=False)
    product_image_3 = fields.Binary(string="Product Image 3", copy=False)
    product_image_4 = fields.Binary(string="Product Image 4", copy=False)
    product_image_5 = fields.Binary(string="Product Image 5", copy=False)
    product_image_6 = fields.Binary(string="Product Image 5", copy=False)
    product_image_7 = fields.Binary(string="Product Image 5", copy=False)
