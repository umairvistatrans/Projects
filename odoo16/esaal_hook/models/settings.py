import logging
import requests
import hashlib
import base64
import json
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    esaal_merchant_id = fields.Char(string='Merchant ID')
    esaal_pos_id = fields.Char(string='PoS ID')
    esaal_ote_id = fields.Char(string='OTE ID')
    esaal_customer_info = fields.Boolean(string='PoS Warning')
    esaal_auto_send = fields.Boolean(string='Send Receipt Automatically')
    esaal_mapper_mode = fields.Boolean(string='PoS Mapper Mode', default=False)
    esaal_mapper_state = fields.Boolean(string='PoS Mapper State', default=False)
    esaal_branding = fields.Boolean(string='Receipt Branding', default=False)
    esaal_branding_qr = fields.Boolean(string='Receipt QR', default=False)
    esaal_registered = fields.Boolean(string='Registration', readonly=True, default=False)
    esaal_connection_status = fields.Char(string='Connection Status', readonly=True, default='Disconnected')
    esaal_mac_placeholder = fields.Char(string='MAC Addr', readonly=True, default='888888')
    pos_name_id_map_json = fields.Char(string='PoS Mapping', default='[]')

    ESAAL_API_PREFIX = "https://pos.esaal.co"

    # logging key
    esaal_debug = False

    # TODO: Implement actual encryption based on unique identifier to the machine
    def base64_encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def base64_decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')

    def register_api(self):
        self.ensure_one()

        # Fetch settings
        merchant_id = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_merchant_id', default='')
        pos_id = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_pos_id', default='')
        ote_id = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_ote_id', default='')

        if not merchant_id or not pos_id or not ote_id:
            if self.esaal_debug:
                _logger.warning('Merchant ID , PoS ID or OTE ID not set in Esaal Settings')
            return {
                'status': 'MerchErr',
                'message': 'Merchant ID , PoS ID or OTE ID not set in Esaal Settings',
            }

        # Register API call
        register_url = f"{self.ESAAL_API_PREFIX}/api/Auth/register"
        register_payload = {
            "posId": pos_id,
            "merchantId": merchant_id,
            "macId": ote_id
        }

        try:
            headers = {
                'Accept': '*/*',
                'Content-Type': 'application/json'
            }
            response = requests.post(register_url, json=register_payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            if response.status_code == 200:
                response_data = response.json()
                if 'data' in response_data and 'password' in response_data['data']:
                    password = response_data['data']['password']
                    # Hash the password
                    hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()

                    # Login API call
                    login_url = f"{self.ESAAL_API_PREFIX}/api/Auth/login"
                    login_payload = {
                        "posId": pos_id,
                        "merchantId": merchant_id,
                        "password": hashed_password
                    }
                    login_response = requests.post(login_url, json=login_payload, headers=headers)
                    login_response.raise_for_status()

                    if login_response.status_code == 200:
                        login_response_data = login_response.json()
                        if 'token' in login_response_data:
                            token = login_response_data['token']
                            encoded = self.base64_encode(token)
                            self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_token', encoded)
                            self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_registered', True)
                            _logger.info("Successfully Registered with Esaal API.")
                            return {'status': 'success', 'message': 'Registered and Logged in Successfully'}
                        else:
                            if self.esaal_debug:
                                _logger.warning("Login Error.")
                            return {'status': 'error', 'message': 'Login failed'}
                    else:
                        if self.esaal_debug:
                            _logger.warning(f"Failed to login: {login_response.status_code} {login_response.text}")
                        return {'status': 'error', 'message': login_response.json().get('message', 'Unknown login error')}
                else:
                    if self.esaal_debug:
                        _logger.warning("Register Error.")
                    return {'status': 'error', 'message': "Registration failed"}
            else:
                if self.esaal_debug:
                    _logger.warning(f"Failed to register: {response.status_code} {response.text}")
                return {'status': 'error', 'message': response.json().get('message', 'Unknown registration error')}
        except requests.RequestException as e:
            if self.esaal_debug:
                _logger.error(f"Error calling register API: {e}")
            return {'status': 'error', 'message': str(e)}

    def check_connection_status(self):
        try:
            response = requests.get(f"{self.ESAAL_API_PREFIX}/api/Auth/register")
            if response.status_code == 405:
                self.esaal_connection_status = "Connected"
                if self.esaal_debug:
                    _logger.info("Connection Established.")
            else:
                self.esaal_connection_status = "Disconnected"
                _logger.info(f"No Connection. Status Code: {response.status_code}")
        except requests.RequestException as e:
            self.esaal_connection_status = "Disconnected"
            _logger.error(f"Error occurred during connection status check: {e}")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_param = self.env['ir.config_parameter'].sudo()
        res.update(
            esaal_merchant_id=config_param.get_param('esaal_hook.esaal_merchant_id', default=''),
            esaal_pos_id=config_param.get_param('esaal_hook.esaal_pos_id', default=''),
            esaal_ote_id=config_param.get_param('esaal_hook.esaal_ote_id', default=''),
            esaal_customer_info=config_param.get_param('esaal_hook.esaal_customer_info', default=False),
            esaal_auto_send=config_param.get_param('esaal_hook.esaal_auto_send', default=False),
            esaal_registered=config_param.get_param('esaal_hook.esaal_registered', default=False),
            esaal_mapper_mode=config_param.get_param('esaal_hook.esaal_mapper_mode', default=False),
            esaal_mapper_state=config_param.get_param('esaal_hook.esaal_mapper_state', default=False),
            esaal_branding=config_param.get_param('esaal_hook.esaal_branding', default=False),
            esaal_branding_qr=config_param.get_param('esaal_hook.esaal_branding_qr', default=False),
            pos_name_id_map_json=config_param.get_param('esaal_hook.pos_mapping', default='[]')
        )
        self.check_connection_status()
        res.update(esaal_connection_status=self.esaal_connection_status)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('esaal_hook.esaal_merchant_id', self.esaal_merchant_id or '')
        config_param.set_param('esaal_hook.esaal_pos_id', self.esaal_pos_id or '')
        config_param.set_param('esaal_hook.esaal_ote_id', self.esaal_ote_id or '')
        config_param.set_param('esaal_hook.esaal_customer_info', self.esaal_customer_info or False)
        config_param.set_param('esaal_hook.esaal_auto_send', self.esaal_auto_send or False)
        config_param.set_param('esaal_hook.esaal_registered', self.esaal_registered or False)
        config_param.set_param('esaal_hook.esaal_mapper_mode', self.esaal_mapper_mode or False)
        config_param.set_param('esaal_hook.esaal_mapper_state', self.esaal_mapper_state or False)
        config_param.set_param('esaal_hook.esaal_branding', self.esaal_branding or False)
        config_param.set_param('esaal_hook.esaal_branding_qr', self.esaal_branding_qr or False)
        config_param.set_param('esaal_hook.pos_mapping', self.pos_name_id_map_json or '[]')

    def action_register(self):
        self.check_connection_status()
        if self.esaal_connection_status == "Connected":
            result = self.register_api()
            if result['status'] == 'success':
                self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_ote_id', 'oteid123')
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Success',
                    'res_model': 'esaal.register.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': result['message']
                    }
                }
            elif['status' == 'MerchErr']:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Missing information',
                    'res_model': 'esaal.register.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': result['message']
                    }
                }
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Error',
                    'res_model': 'esaal.register.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': result['message']
                    }
                }
        else:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'No Connection to Esaal',
                    'res_model': 'esaal.register.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': 'No Internet connection.'
                    }
                }
        
    def action_unregister(self):
         _logger.warning(f"Unregistering PoS ...")
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_password', '')
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_token', '')
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_merchant_id', '')
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_pos_id', '')
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_ote_id', '')
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.pos_mapping', '[]')
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_registered', False)
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_mapper_mode', False)
         self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_mapper_state', False)


