# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    trn_name = fields.Char(related='pos_config_id.trn_name', string="Translated Name", readonly=False)
    whatsapp = fields.Char(related='pos_config_id.whatsapp', string="Whatsapp", readonly=False)
    snapchat = fields.Char(related='pos_config_id.snapchat', string="Snapchat", readonly=False)
    instagram = fields.Char(related='pos_config_id.instagram', string="Instagram", readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: