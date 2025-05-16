# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MdWebsite(models.Model):
    _name = 'home.slider.config'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char()
    active = fields.Boolean(default=False)
    best_selling_ids = fields.Many2many('product.product', 'product_bestselling_rel', string='Best Selling Products',domain=[('type', '=', 'product')])
    new_offer_ids = fields.Many2many('product.product', 'product_newoffer_rel', string='New Offer Products',domain=[('type', '=', 'product')])

    @api.onchange('active')
    def onchange_active(self):
        if self.active:
            # Deactivate all other records
            inactive_records = self.search([('active', '=', True)])
            for record in inactive_records:
                record.write({'active': False})