# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class DeliveryPayPeriods(models.Model):
    _name = 'delivery.carrier.address'
    _rec_name = 'carrier_id'
    carrier_id = fields.Many2one(comodel_name='delivery.carrier')
    country_id = fields.Many2one(comodel_name='res.country', string='Country',
                                 default=lambda self: self.env.company.country_id)
    state_id = fields.Many2one(comodel_name="res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    to_country_id = fields.Many2one(comodel_name='res.country', string='To Country',)
    to_state_id = fields.Many2one(comodel_name="res.country.state", string='To State', ondelete='restrict',
                                  domain="[('country_id', '=?', to_country_id)]")
    value = fields.Float(string='Amount', required=True)

    @api.constrains('value')
    def _check_line_amount(self):
        for rec in self:
            if rec.value <= 0:
                raise UserError(_("Value can't be less than 0."))

    @api.constrains('carrier_id', 'country_id', 'state_id', 'to_country_id', 'to_state_id', 'value')
    def _check_address_duplicate(self):
        for rec in self:
            period_ids = self.search_count([('carrier_id', '=', rec.carrier_id.id),
                                            ('country_id', '=', rec.country_id.id),
                                            ('state_id', '=', rec.state_id.id),
                                            ('to_country_id', '=', rec.to_country_id.id),
                                            ('to_state_id', '=', rec.to_state_id.id),
                                            ('value', '=', rec.value)
                                            ])
            if period_ids > 1:
                raise UserError(_("You can't duplicate rows,please check the rows again."))


# DeliveryPayPeriods()


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    partner_id = fields.Many2one(comodel_name='res.partner', tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 string='Partner', change_default=True)
    delivery_pay_type = fields.Selection(selection=[('hide_and_po', 'Hide Product And Create Po'),
                                                    ('normal', 'Normal')], default='normal',string='Delivery Handle')

    vendor_days = fields.Integer(string='Po Valid Value', required=True,
                                 help="If you didn't set the value of the days the system will not check the po created date")

    delivery_period_ids = fields.One2many(comodel_name='delivery.carrier.address',
                                          inverse_name='carrier_id', string='Vendor Delivery Prices')
    journal_id = fields.Many2one(comodel_name="account.journal", string="COD Journal",domain=[('type','in',['bank','cash'])], required=False, )

    portal_user_id = fields.Many2one(comodel_name="res.users", string="Portal User", required=False, )


# DeliveryCarrier()
