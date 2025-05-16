# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    has_service_charge = fields.Boolean('Has Service Charge', default=False)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_spotii = fields.Boolean(string='Allow Spotii', help='Allow the cashier to give spotii on the order.')
    spotii_pc = fields.Float(string='Spotii Percentage', help='The default spotii percentage')
    spotii_product_id = fields.Many2one('product.product', string='Spotii Service',
                                        domain="[('available_in_pos', '=', True), ('sale_ok', '=', True)]",
                                        help='The product used to model the spotii.')


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'] += ['has_service_charge']
        return result
