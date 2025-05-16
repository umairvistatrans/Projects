# -*- coding: utf-8 -*-

from odoo import api, fields, models
from collections import deque


class StockQuantity(models.Model):
    _inherit = 'stock.quant'

    def write(self, vals):
        res = super().write(vals)
        if self.location_id.usage == 'internal':
            self._notify_pos()
        return res

    @api.model
    def get_qty_available(self, location_id, location_ids=None, product_ids=None):
        if location_id:
            child_location = self.env['stock.location'].search([('id', 'child_of', location_id), ('usage', '=', 'internal')]).ids
            all_location = [location_id]
            if child_location:
                # for sub in root_location.sub_location_ids:
                all_location += child_location
            # queue = deque([])
            stock_quant = self.search_read([('location_id', 'in', all_location), ('product_id', 'in', product_ids)],
                                           ['product_id', 'quantity', 'location_id', 'reserved_quantity','free_qty'])
            return stock_quant
        else:
            stock_quant = self.search_read([('location_id', 'in', location_ids), ('product_id', 'in', product_ids)],
                                           ['product_id', 'quantity', 'location_id', 'reserved_quantity', 'free_qty'])
            return stock_quant

    def location_traversal(self, queue, res, root):
        if root.child_ids:
            for child in root.child_ids:
                if child.usage == 'internal':
                    queue.append(child)
                    res.append(child.id)
            while queue:
                pick = queue.popleft()
                res.append(pick.id)
                self.location_traversal(queue, res, pick)

    def _prepare_pos_message(self, location_id=None):
        """
        Return prepared message to send to POS
        """
        self.ensure_one()
        if location_id:
            res = {"quantity": self.quantity, "product_id": self.product_id.id}
        else:

            location_ids = self.env['stock.location'].search(
                [('usage', '=', 'internal'), ('company_id', '=', self.env.company.id)])
            quant_ids = self.search([('location_id', 'in', location_ids.ids), ('product_id', '=', self.product_id.id)])
            total_qty = sum([q.quantity for q in quant_ids])
            res = {"quantity": total_qty, "product_id": self.product_id.id}
        return res

    def _notify_pos(self):
        """
        Send notification to POS
        """
        pos_session_obj = self.env["pos.session"]
        for quant in self:
            if quant.location_id.usage == 'internal':
                location_id = quant.location_id.id
                configs = pos_session_obj.search(
                    [
                        ("state", "=", "opened"),
                        "|",
                        ("config_id.show_qty_available", "=", True),
                        ("config_id.show_qty_available_res", "=", True),
                        "|",
                        ("config_id.location_id", "=", location_id),
                        "|",
                        ("config_id.iface_available_categ_ids", "=", False),
                        (
                            "config_id.iface_available_categ_ids",
                            "in",
                            [quant.product_id.pos_categ_id.id],
                        ),
                    ],
                ).mapped("config_id")
                if configs:
                    location_only_configs = configs.filtered(lambda config: config.location_only)
                    all_location_configs = configs - location_only_configs
                    if location_only_configs:
                        location_only_configs._notify_available_quantity(quant._prepare_pos_message(location_id))
                    if all_location_configs:
                        all_location_configs._notify_available_quantity(quant._prepare_pos_message())
