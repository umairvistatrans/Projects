# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_qty_available = fields.Boolean(string='Display On Hand Stock in POS')
    show_qty_available_res = fields.Boolean(string='Display Available Stock in POS')
    location_only = fields.Boolean(string='Only in POS Location')
    allow_out_of_stock = fields.Boolean(string='Allow Out-of-Stock')
    limit_qty = fields.Integer(string='Deny Order when Quantity Available lower than', default=0)
    location_id = fields.Many2one('stock.location', related="picking_type_id.default_location_src_id")

    @api.onchange('show_qty_available')
    def show_qty_available_change(self):
        if self.show_qty_available:
            self.show_qty_available_res = False

    @api.onchange('show_qty_available_res')
    def show_qty_available_res_change(self):
        if self.show_qty_available_res:
            self.show_qty_available = False

    def _get_channel_name(self):
        """
        Return full channel name as combination, POS Config ID and const CHANNEL
        """
        self.ensure_one()
        return '["{}","{}"]'.format("pos_stock_quantity", self.id)

    def _notify_available_quantity(self, message):
        """
        Notify POSes about product updates
        """
        if not isinstance(message, list):
            message = [message]
        notifications = []
        for config in self:
            notifications.append(
                [config._get_channel_name(), "pos.config/product_update", message]
            )
        if notifications:
            self.env["bus.bus"]._sendmany(notifications)
            _logger.debug("POS notifications for %s: %s", self.ids, notifications)
