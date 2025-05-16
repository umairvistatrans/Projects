# -*- coding: utf-8 -*-

from odoo import fields, models,api


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_picking_names(self):
        if self.invoice_line_ids:
            sale_order_id = self.invoice_line_ids.mapped('sale_line_ids').order_id
            if sale_order_id.picking_ids:
                picking_ids = sale_order_id.picking_ids.filtered(
                    lambda picking: picking.state in ('draft', 'waiting', 'confirmed', 'assigned', 'done')
                )
                return [picking.name for picking in picking_ids]
        return False


# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"

#     total_tax_amt = fields.Float(string="Tax total",compute='_compute_total_tax_amt')
#     @api.depends("total_tax_amt")
#     def _compute_total_tax_amt(self):
#         for rec in self:
#             total_tax=0.0
#             if rec.tax_ids:
#                 for line in rec.tax_ids:
#                     total_tax=total_tax + ((rec.price_subtotal / 100) * line.amount)
#             rec.total_tax_amt=total_tax
    
