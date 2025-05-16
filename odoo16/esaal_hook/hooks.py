import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def uninstall_hook(cr, registry):
    _logger.warning("Uninstalling Esaal ...")
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_password', '')
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_token', '')
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_merchant_id', '')
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_pos_id', '')
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_ote_id', '')
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_registered', False)
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_auto_send', False)
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_customer_info', False)
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_mapper_mode', False)
    env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_mapper_state', False)
    env['ir.config_parameter'].sudo().set_param('esaal_hook.pos_mapping', '[]')
