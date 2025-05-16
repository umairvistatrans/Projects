# This software and associated files (the “Software”) can only be used (executed)
# with a valid Numla Enterprise Subscription for the correct number of users.
# It is forbidden to modify, publish, distribute, sublicense,
# or sell copies of the Software or modified copies of the Software.
#
# See LICENSE for full licensing information.
# Copyright (c) 2021-2023 Numla Limited <az@numla.com>
# All rights reserved.
from odoo import api, fields, models, _


class Pos_SalesWizard(models.TransientModel):
    _name = 'pos.sales.wizard'
    _description = "POS Sales Wizard"

    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        # restrict to configs available to the user
        config_ids = self.env['pos.config'].search([]).ids
        # exclude configs has not been opened for 2 days
        self.env.cr.execute("""
            SELECT
            max(start_at) as start,
            config_id
            FROM pos_session
            WHERE config_id = ANY(%s)
            AND start_at > (NOW() - INTERVAL '2 DAYS')
            GROUP BY config_id
        """, (config_ids,))
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    date_from = fields.Datetime(string='Start Date', required=True, default=_default_start_date)
    date_to = fields.Datetime(string='End Date', required=True, default=fields.Datetime.now)
    pos_ids = fields.Many2many(comodel_name="pos.config", string="Point of Sale", required=True,
                               default=lambda s: s.env['pos.config'].search([]))

    def print_report(self):
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'pos_ids': self.pos_ids.ids,
                }
        return self.env.ref('pos_sales_report.action_pos_sales_report').report_action(self, data=data)
