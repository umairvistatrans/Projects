# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import fields, models, api


class ResConfigSettingsPosPayment(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_payment_method_ids = fields.Many2many(related='pos_config_id.sale_payment_method_ids', readonly=False)
