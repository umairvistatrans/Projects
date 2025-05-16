# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    trn_name = fields.Char(string="Translated Name")

    whatsapp = fields.Char(string="Whatsapp")
    snapchat = fields.Char(string="Snapchat")
    instagram = fields.Char(string="Instagram")
