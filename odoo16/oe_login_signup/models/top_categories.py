from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings1(models.TransientModel):
    _inherit = 'res.config.settings'

    top_categories_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_top_product_category_rel',
        column1='config_id',
        column2='product_category_id',
        string='Top categories'
    )

    # -----------------------------------------------------------------------------------------------------------------

    sidecards_product_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
        ], string="Side Cards Product Selection Criteria")

    sidecards_product_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_sidecard_category_rel',
        column1='config_id',
        column2='sidecard_category_id',
        string='Side Cards Categories'
    )

    sidecards_products = fields.Many2many(
        comodel_name='product.product',
        relation='res_config_settings_sidecard_products_rel',
        column1='config_id',
        column2='sidecard_products_id',
        string='Side Cards'
    )

    # -----------------------------------------------------------------------------------------------------------------

    sidecards_product_r_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
        ], string="Side Cards Product Selection Criteria")

    sidecards_product_r_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_sidecard_category_r_rel',
        column1='config_id',
        column2='sidecard_r_category_id',
        string='Side Cards Categories'
    )

    sidecards_products_r = fields.Many2many(
        comodel_name='product.product',
        relation='res_config_settings_sidecard_products_r_rel',
        column1='config_id',
        column2='sidecard_products_r_id',
        string='Right Side Cards'
    )

    # -----------------------------------------------------------------------------------------------------------------

    second_sidecards_product_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
        ], string="Second Side Cards Product Selection Criteria")

    second_sidecards_product_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_second_sidecard_category_rel',
        column1='config_id',
        column2='second_sidecard_category_id',
        string='Second Side Cards Categories'
    )
    second_sidecards_products = fields.Many2many(
        comodel_name='product.product',
        relation='res_config_settings_second_sidecard_products_rel',
        column1='config_id',
        column2='second_sidecard_products_id',
        string='Second Side Cards'
    )

    # -----------------------------------------------------------------------------------------------------------------

    second_sidecards_product_r_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
        ], string="Second Side Cards Product Selection Criteria")

    second_sidecards_product_r_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_second_sidecard_category_r_rel',
        column1='config_id',
        column2='second_sidecard_category_r_id',
        string='Second Side Cards Right Categories'
    )
    second_sidecards_products_r = fields.Many2many(
        comodel_name='product.product',
        relation='res_config_settings_second_sidecard_products_r_rel',
        column1='config_id',
        column2='second_sidecard_products_r_id',
        string='Second Side Cards Right'
    )
    
    
    shop_products_three = fields.Many2many(
        comodel_name='product.product',
        relation='res_config_settings_shop_products',
        column1='config_id',
        column2='shop_products_three_id',
        string='Shop page three products'
    )

    @api.constrains('sidecards_products')
    def _cards_products(self):
        for record in self:
            if len(record.sidecards_products) < 0 != len(record.sidecards_products) > 2:
                raise ValidationError(_("The Products must be less than 2 and greater than 0"))

    def set_values(self):
        super(ResConfigSettings1, self).set_values()
        param_env = self.env['ir.config_parameter'].sudo()
        param_env.set_param('oe_login_signup.top_categories_ids', ','.join(map(str, self.top_categories_ids.ids)))
        # ----------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.sidecards_product_type', self.sidecards_product_type)
        param_env.set_param('oe_login_signup.sidecards_product_category_ids',
                            ','.join(map(str, self.sidecards_product_category_ids.ids)))
        param_env.set_param('oe_login_signup.sidecards_products', ','.join(map(str, self.sidecards_products.ids)))
        # ----------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.sidecards_product_r_type', self.sidecards_product_r_type)
        param_env.set_param('oe_login_signup.sidecards_product_r_category_ids',
                            ','.join(map(str, self.sidecards_product_r_category_ids.ids)))
        param_env.set_param('oe_login_signup.sidecards_products_r', ','.join(map(str, self.sidecards_products_r.ids)))
        # ----------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.second_sidecards_product_type', self.second_sidecards_product_type)
        param_env.set_param('oe_login_signup.second_sidecards_product_category_ids',
                            ','.join(map(str, self.second_sidecards_product_category_ids.ids)))
        param_env.set_param('oe_login_signup.second_sidecards_products',
                            ','.join(map(str, self.second_sidecards_products.ids)))
        # ----------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.second_sidecards_product_r_type', self.second_sidecards_product_r_type)
        param_env.set_param('oe_login_signup.second_sidecards_product_r_category_ids',
                            ','.join(map(str, self.second_sidecards_product_r_category_ids.ids)))
        param_env.set_param('oe_login_signup.second_sidecards_products_r',
                            ','.join(map(str, self.second_sidecards_products_r.ids)))
        # ----------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.shop_products_three', ','.join(map(str, self.shop_products_three.ids)))
        
    def get_values(self):
        res = super(ResConfigSettings1, self).get_values()
        param_env = self.env['ir.config_parameter'].sudo()

        top_categories_ids = [int(i) for i in param_env.get_param('oe_login_signup.top_categories_ids', '').split(',')
                              if
                              i.isdigit()]
        res['top_categories_ids'] = [(6, 0, top_categories_ids)]

        # ----------------------------------------------------------------------------------------------------------

        sidecards_product_category_ids = [int(i) for i in
                                     param_env.get_param('oe_login_signup.sidecards_product_category_ids', '').split(',') if
                                     i.isdigit()]
        res['sidecards_product_category_ids'] = [(6, 0, sidecards_product_category_ids)]
        res['sidecards_product_type'] = param_env.get_param('oe_login_signup.sidecards_product_type', '')
        sidecards_products = [int(i) for i in param_env.get_param('oe_login_signup.sidecards_products', '').split(',')
                              if
                              i.isdigit()]
        res['sidecards_products'] = [(6, 0, sidecards_products)]

        # ----------------------------------------------------------------------------------------------------------

        sidecards_product_r_category_ids = [int(i) for i in
                                          param_env.get_param('oe_login_signup.sidecards_product_r_category_ids',
                                                              '').split(',') if
                                          i.isdigit()]
        res['sidecards_product_r_category_ids'] = [(6, 0, sidecards_product_r_category_ids)]
        res['sidecards_product_r_type'] = param_env.get_param('oe_login_signup.sidecards_product_r_type', '')

        sidecards_products_r = [int(i) for i in
                                param_env.get_param('oe_login_signup.sidecards_products_r', '').split(',') if
                                i.isdigit()]
        res['sidecards_products_r'] = [(6, 0, sidecards_products_r)]

        # ----------------------------------------------------------------------------------------------------------
        second_sidecards_product_category_ids = [int(i) for i in
                                          param_env.get_param('oe_login_signup.second_sidecards_product_category_ids',
                                                              '').split(',') if
                                          i.isdigit()]
        res['second_sidecards_product_category_ids'] = [(6, 0, second_sidecards_product_category_ids)]
        res['second_sidecards_product_type'] = param_env.get_param('oe_login_signup.second_sidecards_product_type', '')

        second_sidecards_products = [int(i) for i in
                                     param_env.get_param('oe_login_signup.second_sidecards_products', '').split(',') if
                                     i.isdigit()]
        res['second_sidecards_products'] = [(6, 0, second_sidecards_products)]

        # ----------------------------------------------------------------------------------------------------------

        second_sidecards_product_r_category_ids = [int(i) for i in
                                                 param_env.get_param(
                                                     'oe_login_signup.second_sidecards_product_r_category_ids',
                                                     '').split(',') if
                                                 i.isdigit()]
        res['second_sidecards_product_r_category_ids'] = [(6, 0, second_sidecards_product_r_category_ids)]
        res['second_sidecards_product_r_type'] = param_env.get_param('oe_login_signup.second_sidecards_product_r_type', '')
        second_sidecards_products_r = [int(i) for i in
                                       param_env.get_param('oe_login_signup.second_sidecards_products_r', '').split(',')
                                       if
                                       i.isdigit()]
        res['second_sidecards_products_r'] = [(6, 0, second_sidecards_products_r)]

        # ----------------------------------------------------------------------------------------------------------
        
        shop_products_three = [int(i) for i in param_env.get_param('oe_login_signup.shop_products_three', '').split(',') if
                        i.isdigit()]
        res['shop_products_three'] = [(6, 0, shop_products_three)]
        
        return res
