# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_preorder = fields.Boolean(string="Available for Pre-order", related='product_tmpl_id.is_preorder')
    is_default = fields.Boolean(string="Override Default Pre-order Configuration", related='product_tmpl_id.is_default')
    preorder_expiry = fields.Date(string='Expiry Date', related='product_tmpl_id.preorder_expiry')
    preorder_payment_type = fields.Selection(string='Payment Type', related='product_tmpl_id.preorder_payment_type')
    percent = fields.Float(string='Amount', related='product_tmpl_id.percent')
    allowed_preorder_qty = fields.Float(string='Allow preorder when quantity Less then or Equal',
                                        related='product_tmpl_id.allowed_preorder_qty')
    minimum_preorder_qty = fields.Float(string='Minimum Quantity', related='product_tmpl_id.minimum_preorder_qty')
    maximum_preorder_qty = fields.Float(string='Maximum Quantity', related='product_tmpl_id.maximum_preorder_qty')

    @api.onchange('is_preorder')
    def onchange_is_preorder(self):
        for rec in self:
            if rec.is_preorder:
                preorder = self.env['website.preorder'].search([('status', '=', True)])
                rec.preorder_payment_type = preorder.preorder_payment_type
                rec.percent = preorder.percent
                rec.allowed_preorder_qty = preorder.allowed_preorder_qty
                rec.minimum_preorder_qty = preorder.minimum_preorder_qty
                rec.maximum_preorder_qty = preorder.maximum_preorder_qty
                rec.preorder_expiry = preorder.preorder_expiry

    def write(self, vals):
        preorder = self.env['website.preorder'].search([('status', '=', True)])
        if 'is_default' in vals:
            if not vals['is_default']:
                vals['preorder_payment_type'] = preorder.preorder_payment_type
                vals['percent'] = preorder.percent
                vals['allowed_preorder_qty'] = preorder.allowed_preorder_qty
                vals['minimum_preorder_qty'] = preorder.minimum_preorder_qty
                vals['maximum_preorder_qty'] = preorder.maximum_preorder_qty
                vals['preorder_expiry'] = preorder['preorder_expiry']
        if 'is_preorder' in vals:
            if vals['is_preorder'] and 'is_default' not in vals:
                vals['preorder_payment_type'] = preorder.preorder_payment_type
                vals['percent'] = preorder.percent
                vals['allowed_preorder_qty'] = preorder.allowed_preorder_qty
                vals['minimum_preorder_qty'] = preorder.minimum_preorder_qty
                vals['maximum_preorder_qty'] = preorder.maximum_preorder_qty
                vals['preorder_expiry'] = preorder['preorder_expiry']
        return super(ProductProduct, self).write(vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_preorder = fields.Boolean(string="Available for Pre-order")
    is_default = fields.Boolean(string="Override Default Pre-order Configuration")
    preorder_expiry = fields.Date(string='Expiry Date')
    preorder_payment_type = fields.Selection([('partial', 'Percentage of price'),
                                              ('full', 'Fixed Amount(Full payment)'),
                                              ], string='Payment Type')
    percent = fields.Float(string='Percent Payment')
    allowed_preorder_qty = fields.Float(string='Allow preorder when quantity Less then or Equal')
    minimum_preorder_qty = fields.Float(string='Minimum Quantity')
    maximum_preorder_qty = fields.Float(string='Maximum Quantity')
    allowed_preorder = fields.Char(string="Alled preorder")
    on_hand_qty = fields.Float(string="Qty")

    @api.onchange('is_preorder')
    def onchange_is_preorder(self):
        for rec in self:
            if rec.is_preorder:
                preorder = self.env['website.preorder'].search([('status', '=', True)])
                rec.preorder_payment_type = preorder.preorder_payment_type
                rec.percent = preorder.percent
                rec.allowed_preorder_qty = preorder.allowed_preorder_qty
                rec.minimum_preorder_qty = preorder.minimum_preorder_qty
                rec.maximum_preorder_qty = preorder.maximum_preorder_qty
                rec.preorder_expiry = preorder.preorder_expiry

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            preorder = self.env['website.preorder'].search([('status', '=', True)])
            if 'is_default' in vals:
                if not vals['is_default']:
                    vals['preorder_payment_type'] = preorder.preorder_payment_type
                    vals['percent'] = preorder.percent
                    vals['allowed_preorder_qty'] = preorder.allowed_preorder_qty
                    vals['minimum_preorder_qty'] = preorder.minimum_preorder_qty
                    vals['maximum_preorder_qty'] = preorder.maximum_preorder_qty
                    vals['preorder_expiry'] = preorder['preorder_expiry']
            if 'is_preorder' in vals:
                if vals['is_preorder'] and 'is_default' not in vals:
                    vals['preorder_payment_type'] = preorder.preorder_payment_type
                    vals['percent'] = preorder.percent
                    vals['allowed_preorder_qty'] = preorder.allowed_preorder_qty
                    vals['minimum_preorder_qty'] = preorder.minimum_preorder_qty
                    vals['maximum_preorder_qty'] = preorder.maximum_preorder_qty
                    vals['preorder_expiry'] = preorder['preorder_expiry']
        return super(ProductTemplate, self).create(vals_list)

    def write(self, vals):
        preorder = self.env['website.preorder'].search([('status', '=', True)])
        if 'is_default' in vals:
            if not vals['is_default']:
                vals['preorder_payment_type'] = preorder.preorder_payment_type
                vals['percent'] = preorder.percent
                vals['allowed_preorder_qty'] = preorder.allowed_preorder_qty
                vals['minimum_preorder_qty'] = preorder.minimum_preorder_qty
                vals['maximum_preorder_qty'] = preorder.maximum_preorder_qty
                vals['preorder_expiry'] = preorder['preorder_expiry']
        if 'is_preorder' in vals:
            if vals['is_preorder'] and 'is_default' not in vals:
                vals['preorder_payment_type'] = preorder.preorder_payment_type
                vals['percent'] = preorder.percent
                vals['allowed_preorder_qty'] = preorder.allowed_preorder_qty
                vals['minimum_preorder_qty'] = preorder.minimum_preorder_qty
                vals['maximum_preorder_qty'] = preorder.maximum_preorder_qty
                vals['preorder_expiry'] = preorder['preorder_expiry']
        return super(ProductTemplate, self).write(vals)

    @api.constrains('minimum_preorder_qty')
    def _check_minimum_preorder_qty(self):
        if self.minimum_preorder_qty <= 0.0:
            raise ValidationError(_("You can not add minimum quantity less than 1.0 !!...."))

    @api.constrains('maximum_preorder_qty')
    def _check_maximum_preorder_qty(self):
        if self.maximum_preorder_qty < self.minimum_preorder_qty:
            raise ValidationError(_("You can not add maximum quantity less than minimum quantity !!...."))

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        combination_info = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty,
                                                                              pricelist, parent_combination,
                                                                              only_template)
        # combination_info = super(ProductTemplate, self)._get_combination_info(
        #     combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
        #     parent_combination=False, only_template=False)
        combination_info['product_quant'] = self.env['product.template'].sudo().browse(
            combination_info['product_template_id']).qty_available
        return combination_info

    def get_preorder_date_validation(self):
        if self.is_preorder and self.preorder_expiry:
            return self.preorder_expiry >= (datetime.now().date())
        else:
            return True

    def get_preorder_label(self):
        preorder = self.env['website.preorder'].search([('status', '=', True)])
        if preorder:
            if self.is_preorder:
                if self.get_preorder_date_validation():
                    if self.on_hand_qty != self.qty_available and self.on_hand_qty <= self.allowed_preorder_qty:
                        self.allowed_preorder = "preorder"
                        return "preorder"
                    elif self.qty_available > self.allowed_preorder_qty:
                        self.allowed_preorder = "in_stock"
                        return "in_stock"
                    elif self.qty_available <= self.allowed_preorder_qty:
                        self.allowed_preorder = "preorder"
                        return "preorder"
                else:
                    if (self.qty_available > 0):
                        self.allowed_preorder = "in_stock"
                        return "in_stock"
                    elif (self.qty_available <= 0):
                        self.allowed_preorder = "out_stock"
                        return "out_stock"
            else:
                if (self.qty_available > 0):
                    self.allowed_preorder = "in_stock"
                    return "in_stock"
                elif (self.qty_available <= 0):
                    self.allowed_preorder = "out_stock"
                    return "out_stock"

        else:
            if (self.qty_available > 0):
                self.allowed_preorder = "in_stock"
                return "in_stock"
            elif (self.qty_available <= 0):
                self.allowed_preorder = "out_stock"
                return "out_stock"
