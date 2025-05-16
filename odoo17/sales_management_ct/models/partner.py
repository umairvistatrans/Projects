# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

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
    collar_shape_id = fields.Many2one('design.template.ct', string="Collar Shape", domain=[('shape', '=', 'collar')], tracking=True)
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
