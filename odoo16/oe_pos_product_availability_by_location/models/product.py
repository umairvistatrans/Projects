# -*- coding: utf-8 -*-

from odoo import fields, models, _


class Product(models.Model):
    _inherit = "product.product"

    def oe_get_product_availability_by_location(self, code):
        if code:
            product = self.search([('default_code', '=', code), ('available_in_pos', '=', True)], limit=1)
            if not product:
                return {
                    'error': {
                        'message': _('No Product found for [' + code + '], please try to search another internal reference.')
                    }
                }
            unassigned_quants = self.env['stock.quant'].sudo().search_read([
                ('product_id', '=', product.id), ('lot_id', '=', False),
                ('location_id.usage', '=', 'internal'), ('company_id', '=', self.env.company.id)
            ], ['product_id', 'location_id', 'quantity', 'reserved_quantity', 'product_uom_id'])
            if not unassigned_quants:
                return {
                    'error': {
                        'message': _('Stock Quant not found for [' + code + '], please try to search another internal reference.')
                    }
                }
            return unassigned_quants
        return {
            'error': {
                'message': _("Something went wrong, please try again.")
            }
        }
