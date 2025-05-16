# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class OEVisitsCompanyProducts(models.Model):
    _name = "oe.visit.comp.products"
    _description = 'OE Visit Company Products'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    visit_id = fields.Many2one('oe.visits', string="Visit")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer('Quantity')
    availability = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available'),
        ('out_of_stock', 'Out of Stock')], string="Stock Availability", default='not_available')
    date_code = fields.Char(related='product_id.date_code', readonly=False)
