# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import datetime
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_cod = fields.Boolean('COD')
