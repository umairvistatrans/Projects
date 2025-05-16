from odoo import models, fields, api

class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    is_restock = fields.Boolean(compute='_compute_is_restock', store=True)

    @api.depends('available_quantity', 'product_id.stock_limit')
    def _compute_is_restock(self):
        for quant in self:
            quant.is_restock = quant.available_quantity <= quant.product_id.stock_limit
