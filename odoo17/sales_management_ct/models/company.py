# -*- coding: utf-8 -*-

from odoo import models, fields


class CompanyInherit(models.Model):
    _inherit = 'res.company'

    ref_pocket_shape = fields.Binary(string='Pocket Shapes')
    ref_mobile_pocket_shape = fields.Binary(string='Mobile Pocket Shapes')
    ref_plain_cuff = fields.Binary(string='Plain Cuff Shapes')
    ref_cufflink = fields.Binary(string='Cufflink Shapes')
    ref_collar = fields.Binary(string='Collar Shapes')
    ref_zipper = fields.Binary(string='Zipper Shapes')
