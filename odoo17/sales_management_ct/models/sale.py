# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .models import MEASUREMENTS_FIELDS


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    measurements_order = fields.Boolean()
    measurement_lines = fields.One2many(
        'sale.order.measurement.line',
        'sale_order_id',
        string='Measurement Lines'
    )

    def _compute_measurements_order(self):
        self.ensure_one()
        # Only compute the value if the state is 'draft'
        measurements_required = False

        for line in self.order_line:
            if line.product_id.measurements_required:
                measurements_required = True
                break

        return measurements_required

    def _assign_measurements(self):
        """
        Creates measurement lines for products that require measurements.
        Also, creates Measurement records and copies values from the related res.partner.
        """
        self.ensure_one()
        self.measurement_lines.unlink()

        measurement_lines = []
        partner = self.partner_id

        for line in self.order_line:
            # Check if the product requires measurements
            if line.product_id.measurements_required:
                for i in range(int(line.product_uom_qty)):
                    # Create a new measurement line
                    measurement_line = self.env['sale.order.measurement.line'].create({
                        'sale_order_id': self.id,
                        'product_id': line.product_id.id,
                        'sale_line_id': line.id,
                        'sequence': i + 1,
                        'priority': '0',
                        'order_type': 'previous'
                    })
                    measurement_lines.append(measurement_line.id)

                    # Create a new measurement record and copy values from res.partner
                    self._create_line_measurements(partner, measurement_line)

        # Assign the measurement lines to the sale order
        self.measurement_lines = [(6, 0, measurement_lines)]

    def _create_line_measurements(self, partner, measurement_line):
        self.env['line.measurement'].create({
            'measurement_line_id': measurement_line.id,
            'product_id': measurement_line.sale_line_id.product_id.id,

            # Copy fields from res.partner
            'logo_code_1': partner.logo_code_1,
            'logo_code_2': partner.logo_code_2,
            'logo_code_3': partner.logo_code_3,
            'button_code_1': partner.button_code_1,
            'button_code_2': partner.button_code_2,
            'button_code_3': partner.button_code_3,
            'external_buttons_available': partner.external_buttons_available,
            'fabric_code_1': partner.fabric_code_1,
            'fabric_code_2': partner.fabric_code_2,
            'fabric_code_3': partner.fabric_code_3,
            'codes_additional_notes': partner.codes_additional_notes,

            # Thobe Length
            'thobe_length_total': partner.thobe_length_total,
            'thobe_length_front': partner.thobe_length_front,
            'thobe_length_back': partner.thobe_length_back,
            'thobe_length_notes': partner.thobe_length_notes,

            # Chest + Waist + Middle
            'chest_width': partner.chest_width,
            'waist_width': partner.waist_width,
            'middle_width': partner.middle_width,
            'chest_waist_middle_notes': partner.chest_waist_middle_notes,

            # Pocket Measurements
            'pocket_start_extension': partner.pocket_start_extension,
            'pocket_length': partner.pocket_length,
            'pocket_width': partner.pocket_width,
            'pocket_shape_id': partner.pocket_shape_id.id,
            'pocket_additions': partner.pocket_additions,
            'pocket_padding': partner.pocket_padding,
            'pocket_notes': partner.pocket_notes,

            # Sleeve Width
            'muscle_width': partner.muscle_width,
            'mid_wrist_width': partner.mid_wrist_width,
            'sleeve_width_notes': partner.sleeve_width_notes,

            # Side Pocket
            'side_pocket_length': partner.side_pocket_length,
            'side_pocket_width': partner.side_pocket_width,
            'side_pocket_zipper': partner.side_pocket_zipper,
            'side_pocket_additions': partner.side_pocket_additions,
            'mobile_pocket': partner.mobile_pocket,
            'mobile_pocket_id': partner.mobile_pocket_id.id,

            # Bottom of the Thobe
            'bottom_width': partner.bottom_width,
            'bottom_pleat': partner.bottom_pleat,
            'bottom_notes': partner.bottom_notes,

            # Sleeve & Underarm
            'plain_sleeve_length': partner.plain_sleeve_length,
            'cuff_sleeve_length': partner.cuff_sleeve_length,
            'underarm_length': partner.underarm_length,
            'upper_underarm_width': partner.upper_underarm_width,
            'lower_underarm_width': partner.lower_underarm_width,
            'sleeve_underarm_notes': partner.sleeve_underarm_notes,

            # Cuff
            'cuff_type': partner.cuff_type,
            'cuff_plain_length': partner.cuff_plain_length,
            'cuff_plain_width': partner.cuff_plain_width,
            'cuff_plain_shape_id': partner.cuff_plain_shape_id.id,
            'cuff_length': partner.cuff_length,
            'cuff_width': partner.cuff_width,
            'cufflink_shape_id': partner.cufflink_shape_id.id,
            'pleat_padding': partner.pleat_padding,
            'cuff_notes': partner.cuff_notes,

            # Collar
            'collar_width': partner.collar_width,
            'collar_height': partner.collar_height,
            'collar_shape_id': partner.collar_shape_id.id,
            'collar_padding': partner.collar_padding,
            'collar_notes': partner.collar_notes,

            # Zipper
            'zipper_length': partner.zipper_length,
            'zipper_width': partner.zipper_width,
            'zipper_shape_id': partner.zipper_shape_id.id,
            'zipper_padding': partner.zipper_padding,
            'zipper_notes': partner.zipper_notes,

            # Shoulder
            'shoulder_width': partner.shoulder_width,
            'shoulder_notes': partner.shoulder_notes
        })

    def _check_unit_price_against_min_price(self):
        # Check unit price against min_price for all order lines
        for line in self.order_line:
            product = line.product_id
            min_price = product.min_price

            if line.price_unit < min_price:
                raise ValidationError(_("Unit price for product %(product_display_name) is less than the minimum price of %(min_price).", product_display_name=product.display_name, min_price=min_price))

    def action_confirm(self):
        if self.measurement_lines:
            # Fetch all measurement lines
            measurement_lines = self.env['line.measurement'].browse(self.measurement_lines.ids)

            # Convert measurement lines into a list of dictionaries
            measurements_list = [{field: getattr(line, field) for field in MEASUREMENTS_FIELDS} for line in
                                 measurement_lines]

            # Check if all dictionaries in the list are the same
            all_same = all(measurements_list[0] == measurement for measurement in measurements_list)

            # Assign the flag based on comparison result
            measurements_match_flag = all_same

            if measurements_match_flag:
                measurement_lines[0].action_apply_measurements_partner()

        # Call the method to validate unit prices
        self._check_unit_price_against_min_price()

        return super(SaleOrderInherit, self).action_confirm()

    def write(self, vals):
        # Fetch previous states of measurements_order for all records
        prev_order_statuses = self.mapped('measurements_order')

        # Call super() once for the entire recordset
        res = super(SaleOrderInherit, self).write(vals)

        for order, prev_order_status in zip(self, prev_order_statuses):
            # Recompute measurements_order after write operation
            if ('order_line' in vals or 'partner_id' in vals) and order.state == 'draft':
                order.measurements_order = order._compute_measurements_order()

                # Case 1: Measurements were False and now True
                if (not prev_order_status and order.measurements_order) or (
                        prev_order_status and order.measurements_order):
                    order._assign_measurements()

                # Case 2: Measurements were True and now False
                elif prev_order_status and not order.measurements_order:
                    order.measurement_lines.unlink()

        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrderInherit, self).create(vals)
        res.measurements_order = res._compute_measurements_order()

        # Case 1: Measurements were False and now True
        if res.measurements_order:
            res._assign_measurements()

        return res
