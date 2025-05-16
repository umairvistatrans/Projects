# -*- coding: utf-8 -*-

from odoo import api, fields, models
import pytz
import re

class PosOrders(models.Model):
    _inherit = 'pos.order'

    is_pos_refund = fields.Boolean(string="Created from POS")

    def refund(self):
        # # Modify the context before calling super
        # context = self.env.context.copy()
        # context.update({
        #     'is_pos_refund': True,  # Add your custom key-value pairs here
        # })
        # self = self.with_context(context)
        #
        # # Call the refund method
        res = super(PosOrders, self).refund()
        refund_orders = self.env['pos.order'].browse(res['res_id'])
        refund_orders.write({'is_pos_refund': True})

        return res

    def write(self, vals):
        trigger_custom_method = False
        if 'name' in vals and 'refund' in vals['name'].lower() and vals.get('state') == 'draft':
            # Update the state to 'paid'
            vals['state'] = 'paid'
            trigger_custom_method = True
        res = super(PosOrders, self).write(vals)
        if trigger_custom_method:
            # Call the custom method for each record in self
            for record in self:
                record.action_pos_order_invoice()
        return res
    def _export_for_ui(self, order):
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')

        pos_reference_str = str(order.pos_reference)

        # Apply regular expression if pos_reference_str is a string
        if isinstance(pos_reference_str, str):
            uid_match = re.search('([0-9-]){14}', pos_reference_str)
            uid = uid_match.group(0) if uid_match else None
        else:
            uid = None
        return {
            'lines': [[0, 0, line] for line in order.lines.export_for_ui()],
            'statement_ids': [[0, 0, payment] for payment in order.payment_ids.export_for_ui()],
            'name': order.pos_reference,
            'uid': uid,
            'amount_paid': order.amount_paid,
            'amount_total': order.amount_total,
            'amount_tax': order.amount_tax,
            'amount_return': order.amount_return,
            'pos_session_id': order.session_id.id,
            'pricelist_id': order.pricelist_id.id,
            'partner_id': order.partner_id.id,
            'user_id': order.user_id.id,
            'sequence_number': order.sequence_number,
            'creation_date': str(order.date_order.astimezone(timezone)),
            'fiscal_position_id': order.fiscal_position_id.id,
            'to_invoice': order.to_invoice,
            'to_ship': order.to_ship,
            'state': order.state,
            'account_move': order.account_move.id,
            'id': order.id,
            'is_tipped': order.is_tipped,
            'tip_amount': order.tip_amount,
            'access_token': order.access_token,
        }


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    note = fields.Char(string="Note")
    full_product_display = fields.Char('Full Product Name', related='product_id.display_name')
