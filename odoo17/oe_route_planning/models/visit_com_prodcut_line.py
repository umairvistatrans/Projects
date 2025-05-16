# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class OEVisitsCompetitorProducts(models.Model):
    _name = "oe.visit.com.products"
    _description = 'OE Visit Competitor Products'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    visit_id = fields.Many2one('oe.visits', string="Visit")
    product_id = fields.Many2one('product.template', string="Product")
    comment = fields.Text('Comment')
    photo = fields.Binary('Photo', attachment=True)
