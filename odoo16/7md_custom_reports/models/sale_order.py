# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_picking_names(self):
        if self.picking_ids:
            picking_ids = self.picking_ids.filtered(
                lambda picking: picking.state in ('draft', 'waiting', 'confirmed', 'assigned')
            )
            return [picking.name for picking in picking_ids]
        return False
