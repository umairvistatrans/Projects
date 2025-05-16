# stock_move.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _update_product_price_on_receipt_validation(self):
        for move in self:
            if move.state == 'done' and move.picking_id.state == 'done' and move.picking_id.picking_type_id.code == 'incoming':
                # Get the product and purchase price from the stock move
                product = move.product_id
                purchase_price = move.price_unit
                # If the product has a supplier, update the supplier's price
                if move.picking_id:
                    supplier_info = product.seller_ids.filtered(lambda s: s.partner_id.id == move.picking_id.partner_id.id)
                    if supplier_info:
                        supplier_info.price = purchase_price

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _add_supplier_to_product(self):
        return False