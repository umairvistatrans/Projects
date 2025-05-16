# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

MEASUREMENTS_FIELDS = [
    'logo_code_1', 'logo_code_2', 'logo_code_3',
    'button_code_1', 'button_code_2', 'button_code_3', 'external_buttons_available',
    'fabric_code_1', 'fabric_code_2', 'fabric_code_3',
    'thobe_length_total', 'thobe_length_front', 'thobe_length_back',
    'chest_width', 'waist_width', 'middle_width',
    'pocket_start_extension', 'pocket_length', 'pocket_width', 'pocket_shape_id',
    'pocket_additions', 'pocket_padding',
    'muscle_width', 'mid_wrist_width',
    'side_pocket_length', 'side_pocket_width', 'side_pocket_zipper', 'side_pocket_additions',
    'mobile_pocket', 'mobile_pocket_id',
    'bottom_width', 'bottom_pleat',
    'plain_sleeve_length', 'cuff_sleeve_length', 'underarm_length',
    'upper_underarm_width', 'lower_underarm_width',
    'cuff_type', 'cuff_plain_length', 'cuff_plain_width', 'cuff_plain_shape_id',
    'cuff_length', 'cuff_width', 'cufflink_shape_id', 'pleat_padding',
    'collar_width', 'collar_height', 'collar_shape_id', 'collar_padding',
    'zipper_length', 'zipper_width', 'zipper_shape_id', 'zipper_padding',
    'shoulder_width', 'codes_additional_notes',
    'thobe_length_notes',
    'chest_waist_middle_notes',
    'pocket_notes',
    'sleeve_width_notes',
    'bottom_notes',
    'cuff_notes',
    'collar_notes',
    'zipper_notes',
    'shoulder_notes'
]


class DesignTemplate(models.Model):
    _name = 'design.template.ct'
    _description = "Design Templates"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', "unique(name)",
                         "A shape with the same name already exists.")]

    name = fields.Char(string='Name', required=True, tracking=True, translate=True)
    active = fields.Boolean(default=True, tracking=True)
    image = fields.Image(string='Image', required=True)
    shape = fields.Selection([
        ('pocket', 'Pocket'),
        ('mobile_phone_pocket', 'Mobile Phone Pocket'),
        ('plain_cuff', 'Plain Cuff'),
        ('cufflink', 'Cufflink'),
        ('collar', 'Collar'),
        ('zipper', 'Zipper'),
    ], string='Shape', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True, translate=True)


class SaleOrderMeasurementLine(models.Model):
    _name = 'sale.order.measurement.line'
    _description = 'Sale Order Measurement Line'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    sale_order_state = fields.Selection(related='sale_order_id.state')
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Text(string="Description")
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    sequence = fields.Integer(string='Sequence')
    order_type = fields.Selection([
        ('previous', 'Previous'),
        ('customised', 'Customised'),
        ('empty', 'Empty')
    ], default='previous', string='Order Type')

    priority = fields.Selection([('0', 'Normal'), ('1', 'High')], default='0', string='Urgency Level')

    def action_open_measurement_form(self):
        """Button action to open the Measurement form view."""
        self.ensure_one()
        measurements_id = self.env['line.measurement'].search([('measurement_line_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Measurement Details'),
            'view_mode': 'form',
            'res_model': 'line.measurement',
            'res_id': measurements_id.id,  # Pass the ID of the related measurement,
            'context': {'button_hide': 0 if self.sale_order_state == 'draft' else 1, 'button_hide_master': 0 if self.sale_order_state == 'sale' else 1},
            'target': 'new',
        }

    def _reorder_sequences(self):
        """Reorder sequences based on priority."""
        # Fetch all lines of the same sale order, ordered by priority and sequence
        sale_order_lines = self.search([('sale_order_id', '=', self.sale_order_id.id)],
                                       order="priority desc, sequence asc")

        # Assign new sequence numbers, but avoid triggering the write method recursively
        with self.env.cr.savepoint():
            for index, line in enumerate(sale_order_lines, start=1):
                if line.sequence != index:  # Only update if there's a change
                    line.sudo().write({'sequence': index})  # Use sudo to avoid recursive calls

    def write(self, vals):
        """Override the write method to update the sequence based on priority."""
        res = super(SaleOrderMeasurementLine, self).write(vals)

        # Only reorder if the priority or sequence is updated
        if 'priority' in vals or 'sequence' in vals:
            self._reorder_sequences()

        return res


class Measurement(models.Model):
    _name = 'line.measurement'
    _description = 'Measurement Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    measurement_line_id = fields.Many2one('sale.order.measurement.line', ondelete='cascade')
    order_type = fields.Selection([
        ('previous', 'Previous'),
        ('customised', 'Customised'),
        ('empty', 'Empty')
    ], default='previous', string='Order Type')
    ref_pocket_shape = fields.Binary(string='Pocket Shapes', related='company_id.ref_pocket_shape')
    ref_mobile_pocket_shape = fields.Binary(string='Mobile Pocket Shapes', related='company_id.ref_mobile_pocket_shape')
    ref_plain_cuff = fields.Binary(string='Plain Cuff Shapes', related='company_id.ref_plain_cuff')
    ref_cufflink = fields.Binary(string='Cufflink Shapes', related='company_id.ref_cufflink')
    ref_collar = fields.Binary(string='Collar Shapes', related='company_id.ref_collar')
    ref_zipper = fields.Binary(string='Zipper Shapes', related='company_id.ref_zipper')

    # Measurements and Design Fields
    # Logo Codes
    logo_code_1 = fields.Char(string="Logo Code 1", tracking=True)
    logo_code_2 = fields.Char(string="Logo Code 2", tracking=True)
    logo_code_3 = fields.Char(string="Logo Code 3", tracking=True)

    # Button Codes
    button_code_1 = fields.Char(string="Button Code 1", tracking=True)
    button_code_2 = fields.Char(string="Button Code 2", tracking=True)
    button_code_3 = fields.Char(string="Button Code 3", tracking=True)
    external_buttons_available = fields.Selection([
        ('no', 'No'),
        ('yes', 'Yes'),
    ], string="External Buttons", tracking=True)

    # Fabric Codes
    fabric_code_1 = fields.Char(string="Fabric Code 1", tracking=True)
    fabric_code_2 = fields.Char(string="Fabric Code 2", tracking=True)
    fabric_code_3 = fields.Char(string="Fabric Code 3", tracking=True)

    codes_additional_notes = fields.Text(string="Additional Notes", tracking=True)

    # Thobe Length
    thobe_length_total = fields.Char(string="Total Length", tracking=True)
    thobe_length_front = fields.Char(string="Front Length", tracking=True)
    thobe_length_back = fields.Char(string="Back Length", tracking=True)
    thobe_length_notes = fields.Text(string="Additional Notes", tracking=True)

    # Chest + Waist + Middle
    chest_width = fields.Char(string="Chest Width", tracking=True)
    waist_width = fields.Char(string="Waist Width", tracking=True)
    middle_width = fields.Char(string="Middle Width", tracking=True)
    chest_waist_middle_notes = fields.Text(string="Additional Notes", tracking=True)

    # Pocket Measurements
    pocket_start_extension = fields.Char(string="Pocket Start Extension", tracking=True)
    pocket_length = fields.Char(string="Pocket Length", tracking=True)
    pocket_width = fields.Char(string="Pocket Width", tracking=True)
    pocket_shape_id = fields.Many2one('design.template.ct', string="Pocket Shape", domain=[('shape', '=', 'pocket')],
                                      tracking=True)

    pocket_additions = fields.Selection([
        ('no_pen', 'No Pen'),
        ('with_pen', 'With Pen'),
        ('full_pen', 'With Full Pen'),
        ('with_logo', 'With Logo'),
        ('without_logo', 'Without Logo'),
        ('glasses_pocket', 'Glasses Pocket'),
    ], string="Pocket Additions", tracking=True)

    pocket_padding = fields.Selection([
        ('no_padding', 'No Padding'),
        ('heavy_padding', '(D) Heavy Padding'),
        ('very_light_padding', '(P) Very Light Padding'),
        ('light_padding', '(FD) Light Padding'),
    ], string="Pocket Padding", tracking=True)
    pocket_notes = fields.Text(string="Additional Notes", tracking=True)

    # Sleeve Width
    muscle_width = fields.Char(string="Muscle Width", tracking=True)
    mid_wrist_width = fields.Char(string="Mid-Wrist Width", tracking=True)
    sleeve_width_notes = fields.Text(string="Additional Notes", tracking=True)

    # Side Pocket
    side_pocket_length = fields.Char(string="Pocket Length", tracking=True)
    side_pocket_width = fields.Char(string="Pocket Width", tracking=True)
    side_pocket_zipper = fields.Selection([
        ('with_zipper', 'With Zipper'),
        ('without_zipper', 'Without Zipper'),
    ], string="With Zipper", tracking=True)
    side_pocket_additions = fields.Char(string="Side Pocket Additions", tracking=True)
    mobile_pocket = fields.Selection([
        ('no', 'No'),
        ('yes', 'Yes'),
    ], string="Mobile Pocket", tracking=True)
    mobile_pocket_id = fields.Many2one('design.template.ct', string="Mobile Pocket Shape",
                                       domain=[('shape', '=', 'mobile_phone_pocket')], tracking=True)

    # Bottom of the Thobe
    bottom_width = fields.Char(string="Bottom Width", tracking=True)
    bottom_pleat = fields.Char(string="Bottom Pleat", tracking=True)
    bottom_notes = fields.Text(string="Additional Notes", tracking=True)

    # Sleeve & Underarm
    plain_sleeve_length = fields.Char(string="Plain Sleeve Length", tracking=True)
    cuff_sleeve_length = fields.Char(string="Cuff Sleeve Length", tracking=True)
    underarm_length = fields.Char(string="Underarm Length", tracking=True)
    upper_underarm_width = fields.Char(string="Upper Underarm Width", tracking=True)
    lower_underarm_width = fields.Char(string="Lower Underarm Width", tracking=True)
    sleeve_underarm_notes = fields.Text(string="Additional Notes", tracking=True)

    # Cuff
    cuff_type = fields.Selection([
        ('plain', 'Plain'),
        ('cufflink', 'Cufflink'),
    ], string="Cuff Type", tracking=True)

    cuff_plain_length = fields.Char(string="Plain Length", tracking=True)
    cuff_plain_width = fields.Char(string="Plain Width", tracking=True)
    cuff_plain_shape_id = fields.Many2one('design.template.ct', string="Plain Cuff Shape",
                                          domain=[('shape', '=', 'plain_cuff')], tracking=True)

    cuff_length = fields.Char(string="Cuff Length", tracking=True)
    cuff_width = fields.Char(string="Cuff Width", tracking=True)
    cufflink_shape_id = fields.Many2one('design.template.ct', string="Cufflink Shape",
                                        domain=[('shape', '=', 'cufflink')], tracking=True)

    pleat_padding = fields.Selection([
        ('no_padding', 'No Padding'),
        ('heavy_padding', '(D) Heavy Padding'),
        ('very_light_padding', '(P) Very Light Padding'),
        ('light_padding', '(FD) Light Padding'),
    ], string="Pleat Padding", tracking=True)
    cuff_notes = fields.Text(string="Additional Notes", tracking=True)

    # Collar
    collar_width = fields.Char(string="Collar Width", tracking=True)
    collar_height = fields.Char(string="Collar Height", tracking=True)
    collar_shape_id = fields.Many2one('design.template.ct', string="Collar Shape", domain=[('shape', '=', 'collar')],
                                      tracking=True)
    collar_padding = fields.Selection([
        ('no_padding', 'No Padding'),
        ('heavy_padding', '(D) Heavy Padding'),
        ('light_padding', '(FD) Light Padding'),
    ], string="Collar Padding", tracking=True)

    collar_notes = fields.Text(string="Additional Notes", tracking=True)

    # Zipper
    zipper_length = fields.Char(string="Zipper Length", tracking=True)
    zipper_width = fields.Char(string="Zipper Width", tracking=True)
    zipper_shape_id = fields.Many2one('design.template.ct', string="Zipper Shape", domain=[('shape', '=', 'zipper')],
                                      tracking=True)
    zipper_padding = fields.Selection([
        ('no_padding', 'No Padding'),
        ('heavy_padding', '(D) Heavy Padding'),
        ('very_light_padding', '(P) Very Light Padding'),
        ('light_padding', '(FD) Light Padding'),
    ], string="Zipper Padding", tracking=True)
    zipper_notes = fields.Text(string="Additional Notes", tracking=True)

    # Shoulder
    shoulder_width = fields.Char(string="Shoulder Width", tracking=True)
    shoulder_notes = fields.Text(string="Additional Notes", tracking=True)

    @api.onchange('mobile_pocket')
    def _onchange_mobile_pocket(self):
        self.mobile_pocket_id = False

    @api.onchange('cuff_type')
    def _onchange_cuff_type(self):
        self.cuff_plain_length = False
        self.cuff_plain_width = False
        self.cuff_plain_shape_id = False
        self.cuff_length = False
        self.cuff_width = False
        self.cufflink_shape_id = False

    def action_apply_measurements(self):
        """Button action to apply current measurements to the relevant sales order."""
        self.ensure_one()

        # Get the relevant measurement lines for the sale order, excluding the current one
        related_measurement_line_id = self.measurement_line_id
        sale_order_measurement_lines = related_measurement_line_id.sale_order_id.measurement_lines.filtered(
            lambda x: x.id != related_measurement_line_id.id)

        # Get all related measurements for the other measurement lines of the sale order
        related_measurements = self.search([
            ('measurement_line_id', 'in', sale_order_measurement_lines.ids)
        ])

        # Fields to copy (excluding any fields that shouldn't be copied, such as IDs or relational fields)

        # Prepare the values to be copied
        values_to_copy = {field: getattr(self, field) for field in MEASUREMENTS_FIELDS}

        # Update all the related measurements with the copied values
        for related_measurement in related_measurements:
            related_measurement.write(values_to_copy)

    def action_apply_measurements_partner(self):
        """Button action to apply current measurements to the related partner."""
        self.ensure_one()

        # Fetch the related partner record
        partner = self.measurement_line_id.sale_order_id.partner_id

        # Prepare the values to be copied from the measurement to the partner
        values_to_copy = {field: getattr(self, field) for field in MEASUREMENTS_FIELDS}

        # Update the partner with the copied values
        partner.write(values_to_copy)

    def _compute_order_type(self):
        """Compute the order type based on field comparisons."""
        # Fetch the related partner record
        partner = self.measurement_line_id.sale_order_id.partner_id

        # Flag to check if all fields are empty
        all_fields_empty = True
        # Flag to check if any field value is different
        is_customised = False

        for field_name in MEASUREMENTS_FIELDS:
            # Get field values for comparison
            self_value = getattr(self, field_name)
            partner_value = getattr(partner, field_name)

            # Check if all fields are empty
            if self_value:
                all_fields_empty = False
            # Check if any field value is different
            if self_value != partner_value:
                is_customised = True

        # Determine the order type based on field comparisons
        if all_fields_empty:
            return 'empty'

        return 'customised' if is_customised else 'previous'

    def write(self, vals):
        # Compute the order type
        res = super(Measurement, self).write(vals)
        order_type = self._compute_order_type()
        # Update the order type in vals
        vals['order_type'] = order_type
        self.measurement_line_id.order_type = order_type

        return res

    def create(self, vals):
        # Create the record
        record = super(Measurement, self).create(vals)
        # Compute and set the order type after creation
        order_type = record._compute_order_type()
        record.order_type = order_type
        record.measurement_line_id.order_type = order_type

        return record
