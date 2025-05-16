# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    allow_validate = fields.Boolean(default=False)
    allow_validate_related = fields.Boolean(related='allow_validate')

    def action_confirm(self):
        result = super(StockPicking, self).action_confirm()
        if self.env.user.has_group('point_of_sale.group_pos_user') and not self.env.user.has_group('point_of_sale.group_pos_manager'):
            for picking in self:
                if picking.picking_type_id.code == 'internal':
                    if picking.location_id.warehouse_id.id in self.env.user.warehouse_ids.ids and picking.location_dest_id.id == self.env.user.default_config_id.picking_type_id.default_location_src_id.id:
                        print("hello")
                    else:
                        raise ValidationError(_('You Do Not Have Permissions To Create Internal Transfer To Other Locations'))

        return result

    def button_validate(self):
        # Add validation for purchase admin or inventory admin
        if not (self.env.user.has_group('purchase.group_purchase_manager') or self.env.user.has_group(
                'stock.group_stock_manager')):
            raise ValidationError(_('Only Purchase Admin or Inventory Admin can validate a delivery.'))

        # Your existing logic for button validation
        result = super(StockPicking, self).button_validate()

        return result