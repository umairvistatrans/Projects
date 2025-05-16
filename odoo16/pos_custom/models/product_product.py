# -*- coding: utf-8 -*-
from odoo import models, fields,api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import datetime


class ProductProduct(models.Model):
    _inherit = 'product.product'
    pos_display_name = fields.Char('Pos Display Name',compute='compute_pos_display_name')
    stock_limit = fields.Integer()

    def compute_pos_display_name(self):
        for rec in self:
            first_25_ch = ''
            if rec.name:
                first_25_ch = rec.name[0:25] or ''
                print(len(first_25_ch))
                if rec.product_template_attribute_value_ids:
                    variants=''
                    for att in rec.product_template_attribute_value_ids.sorted(lambda x:x.name):
                        variants += str(att.name)+', '
                    if variants:
                        variants = variants[:-2]
                        variants ='('+variants+')'
                    first_25_ch +=variants

                rec.pos_display_name = first_25_ch
            else:
                rec.pos_display_name = ''

