# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_spotii = fields.Boolean(related='pos_config_id.allow_spotii', string='Allow Spotii',
                                  help='Allow the cashier to give spotii on the order.', readonly=False)
    spotii_pc = fields.Float(related='pos_config_id.spotii_pc', string='Spotii Percentage',
                             help='The default spotii percentage', readonly=False)
    spotii_product_id = fields.Many2one('product.product', related='pos_config_id.spotii_product_id',
                                        string='Spotii Service',
                                        domain="[('available_in_pos', '=', True), ('sale_ok', '=', True)]",
                                        help='The product used to model the spotii.', readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
