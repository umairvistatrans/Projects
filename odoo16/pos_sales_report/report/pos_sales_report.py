# This software and associated files (the “Software”) can only be used (executed)
# with a valid Numla Enterprise Subscription for the correct number of users.
# It is forbidden to modify, publish, distribute, sublicense,
# or sell copies of the Software or modified copies of the Software.
#
# See LICENSE for full licensing information.
# Copyright (c) 2021-2023 Numla Limited <az@numla.com>
# All rights reserved.
from odoo import models, fields, api
import datetime
import pytz

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'
    is_bank_count = fields.Boolean(string='Bank')


class Pos_Sales_Report(models.AbstractModel):
    _name = 'report.pos_sales_report.sales_report_document'
    _description = 'Sales Report'



    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["pos.config"].search([("id", "in", data['pos_ids'])])
        datetime_form = datetime.datetime.strptime(data['date_from'], '%Y-%m-%d %H:%M:%S')
        datetime_to = datetime.datetime.strptime(data['date_to'], '%Y-%m-%d %H:%M:%S')
        d1 = datetime_form.astimezone(pytz.timezone(self.env.user.tz)).replace(tzinfo=None)
        d2 = datetime_to.astimezone(pytz.timezone(self.env.user.tz)).replace(tzinfo=None)
        print(docids)
        print(data)

        def _get_sales(pos, date_from, date_to):
            domain = [
                ('order_id.config_id', '=', pos.id),
                ('order_id.date_order', '>=', date_from),
                ('order_id.date_order', '<=', date_to),
                ('order_id.state', 'not in', ['draft', 'cancel']),

            ]
            order_line = self.env['pos.order.line'].search(
                domain
            )

            # self.invoices[partner] = {}

            return order_line
        date_value = {
            'date_from': str(d1),
            'date_to': str(d2)
        }
        val = {
            'doc_ids': docids,
            'docs': docs,
            'data': data,
            'date_value':date_value,
            '_get_sales': _get_sales,
        }
        return val