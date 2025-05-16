# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    measurements_required = fields.Boolean(string="Measurements Required?", help="If checked, a Measurements tab will appear in the sales order for this product to fill in the necessary measurements.")
    min_price = fields.Monetary(string='Minimum Price')


class ProductInherit(models.Model):
    _inherit = 'product.product'

    measurements_required = fields.Boolean(string="Measurements Required?", related='product_tmpl_id.measurements_required', readonly=False, store=True, help="If checked, a Measurements tab will appear in the sales order for this product to fill in the necessary measurements.")
    min_price = fields.Monetary(string='Minimum Price', related='product_tmpl_id.min_price', readonly=False, store=True)
