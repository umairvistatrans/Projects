# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class OEVisitsCompanyMaterial(models.Model):
    _name = "oe.visit.comp.material"
    _description = 'OE Visit Company Material'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    visit_id = fields.Many2one('oe.visits', string="Visit")
    product_id = fields.Many2one('product.product', string="Material")
    comment = fields.Text('Comment')
    photo = fields.Binary('Photo', attachment=True)
