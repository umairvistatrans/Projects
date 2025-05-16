# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_qty_available = fields.Boolean(related='pos_config_id.show_qty_available', string="Display On Hand Stock in POS", readonly=False)
    show_qty_available_res = fields.Boolean(related='pos_config_id.show_qty_available_res', string="Display Available Stock in POS", readonly=False)
    location_only = fields.Boolean(related='pos_config_id.location_only', string="Only in POS Location'", readonly=False)
    allow_out_of_stock = fields.Boolean(related='pos_config_id.allow_out_of_stock', string="Allow Out-of-Stock", readonly=False)
    limit_qty = fields.Integer(related='pos_config_id.limit_qty', string="Deny Order when Quantity Available lower than", readonly=False)


    @api.onchange('show_qty_available')
    def show_qty_available_change(self):
        if self.show_qty_available:
            self.show_qty_available_res = False

    @api.onchange('show_qty_available_res')
    def show_qty_available_res_change(self):
        if self.show_qty_available_res:
            self.show_qty_available = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: