# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.external_id:
                order._create_invoices()
                for invoice in self.invoice_ids:
                    invoice.action_post()
        return res
