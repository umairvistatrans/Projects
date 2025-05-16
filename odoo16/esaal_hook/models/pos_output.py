import os
import logging
import requests
import base64
from datetime import datetime
from odoo import models, api, fields
import json
import re

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    # TODO: Implement actual encryption based on unique identifier to the machine
    def base64_encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def base64_decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')
    
    ESAAL_API_PREFIX = "https://pos.esaal.co"

    # logging key
    esaal_debug = False

    # Esaal Print command from POS checkout screen
    @api.model
    def print_receipt_Esaal(self, partner_name, partner_phone, gender, partner_email):

        if self.esaal_debug:
            _logger.info(f"Received partner_name={partner_name}, partner_phone={partner_phone}, gender={gender}, email={partner_email}")

        # Decode the token
        token = self.base64_decode(self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_token', default=''))

        # Format phone number to +9715xxxxxxxx if it starts with 05 and is 10 digits long
        # If the phone number is already in +9715xxxxxxxx format (13 digits), use it as is
        # If the phone number is in xxxxxxxxx format (9 digits), add +971 to it
        #partner_phone = partner_phone.lstrip('+')

        if partner_phone.startswith('05') and len(partner_phone) == 10:
            partner_phone = '+971' + partner_phone[1:]  # Format to +9715xxxxxxxx
        elif partner_phone.startswith('+971') and len(partner_phone) == 13:
            pass  # Use as is
        elif partner_phone.startswith('00971') and len(partner_phone) == 14:
            partner_phone = '+971' + partner_phone[5:] # Strip and append
        elif len(partner_phone) == 9:
            partner_phone = '+971' + partner_phone  # Format to +971xxxxxxxxx
        elif len(partner_phone) == 6 and gender == "AutoPrint":
            pass  # Use as is for AutoPrint
        else:
            if self.esaal_debug:
                _logger.warning("Invalid phone number provided.")
            return {
                "success": False,
                "type": "invalid",
                "status": "Esaal configuration error",
                "message": "Invalid phone format provided"
            }
        
        # Check if customer exists and register
        # Handle auto detection / print for existing customers
        if gender == "AutoPrint":
            esaal_id = partner_phone
            esaal_name = partner_name
        else:
            esaal_id, esaal_name = self.get_customer_info_and_register(partner_name, partner_phone, gender, partner_email, token)

        if self.esaal_debug:
            _logger.info(f"Customer Info: esaalId={esaal_id}, partner_name={esaal_name}")
        
        # Retrieve the most recent order and generate receipt data
        recent_order = self.search([], order='id desc', limit=1)
        if self.esaal_debug:
            _logger.info(f"Processing order ID: {recent_order.pos_reference}")

        try:
            receipt_data = self._generate_receipt_data(recent_order, recent_order.pos_reference, esaal_id)
            if receipt_data == "MerErr":
                return {
                    "success": False,
                    "type": "MerErr",
                    "status": "Esaal configuration error",
                    "message": "Esaal not properly set-up"
                }
            elif receipt_data == "receipt_data":
                return {
                    "success": False,
                    "type": "receipt_data",
                    "status": "Esaal Receipt Error",
                    "message": "Failed to read receipt items."
                }
        except Exception as e:
            return {
                "success": False,
                "status": "failure",
                "message": str(e),
            }

        if self.esaal_debug:
            _logger.info(f"Name: {esaal_name}")
            _logger.info(f"Phone: {partner_phone}")
            _logger.info(f"Gender: {gender}")
            _logger.info(f"Receipt: {json.dumps(receipt_data, indent=2)}")
        # Send Receipt to customer
        result = self.send_receipt(receipt_data, token)
        #result = {
        #    'status_code': 500,
        #    'status': 'success',
        #    'content': {
        #    'status': 'success',
        #    'message': 'Receipt created',
        #    'data': None
        #    }
        #}

        try:
            if result['status'] == 'success':
                return {
                    "success": True,
                    "status": "success",
                    "message": "Receipt created"
                }
            elif (result['type'] == "AuthErr"):
               return {
                    "type": "AuthErr",
                    "status": "error",
                    "message": "Authorization Error"
                }
            else:
                return {
                    "success": False,
                    "status": "error",
                    "message": result.get('message', 'Failed to send receipt')
                }
        except Exception as e:
            return {
                "success": False,
                "status": "failure",
                "message": str(e),
            }
    
    @api.model
    def _generate_receipt_data(self, order, pos_reference, partner_phone):
        try:
            # Fetch settings
            merchant_id = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_merchant_id', default='')
            pos_id = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_pos_id', default='')
            if not merchant_id or not pos_id:
                if self.esaal_debug:
                    _logger.warning('Merchant ID or PoS ID not set in Esaal Settings')
                return "MerErr"

            # Fetch payment methods and their names
            payment_method_mapping = {}
            for payment in order.payment_ids:
                payment_method_id = payment.payment_method_id.id
                payment_method_name = payment.payment_method_id.name
                payment_method_mapping[payment_method_id] = payment_method_name.lower()

            # Format pos_reference for merchantReceiptNo
            merchant_receipt_no = pos_reference.replace("Order ", "")

            # Initialize receipt data
            net_amount_with_tax = round(order.amount_total, 2)
            tax = round(sum(round(line.price_unit * line.qty * line.tax_ids.amount / 100, 2) for line in order.lines if line.tax_ids), 2)
            total_amount = round(net_amount_with_tax - tax, 2)

            # PoS ID
            pos_mapping_json = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.pos_mapping', default='[]')
            pos_mapping_mode = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_mapper_mode', default=False)
            pos_name = re.sub(r'\s*\(.*?\)\s*', '', order.session_id.config_id.display_name).strip()
            config_id = order.session_id.config_id.id
            branch_name = order.session_id.config_id.warehouse_id.name

            if pos_mapping_mode:
                try:
                    pos_mapping = json.loads(pos_mapping_json)
                except json.JSONDecodeError:
                    pos_mapping = []
                
                for entry in pos_mapping:
                    if entry.get('pos_name') == pos_name and entry.get('branch_name') == branch_name and entry.get('config_id') == config_id:
                        pos_id_map = entry.get('pos_id')
                        if pos_id_map and isinstance(pos_id_map, str) and re.match(r'^[A-Z]{3}\d{7}$', pos_id_map):
                            pos_id = pos_id_map
                        else:
                            return "mapper_not_found"
            
            receipt_data = {
                "customerUniqueID": partner_phone,
                "posID": pos_id,
                "paymentMethod": "",
                "merchantReceiptNo": merchant_receipt_no,
                "totalAmount": total_amount,
                "netAmountWithTax": net_amount_with_tax,
                "tax": tax,
                "createdDateTime": fields.Datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                "receiptItems": [],
                "paymentMethods": []
            }

            # Extract payment method details and quantities
            payment_methods = {}
            for statement in order.payment_ids:
                payment_method_id = statement.payment_method_id.id
                payment_amount = statement.amount
                if payment_method_id in payment_methods:
                    payment_methods[payment_method_id]["amount"] += payment_amount
                else:
                    mode = payment_method_mapping.get(payment_method_id, "Other")
                    if mode == "bank":
                        mode = "Other"
                    payment_methods[payment_method_id] = {
                        "mode": mode,
                        "amount": round(statement.amount, 2)
                    }

            # Sort payment methods by amount (descending)
            sorted_payment_methods = sorted(payment_methods.values(), key=lambda x: x["amount"], reverse=True)

            # Set the primary payment method based on the largest quantity
            if sorted_payment_methods:
                primary_payment_method = sorted_payment_methods[0]
                receipt_data["paymentMethod"] = primary_payment_method["mode"]

                # Add payment methods to receipt data
                for method in sorted_payment_methods:
                    payment_entry = {
                        "mode": method["mode"],
                        "amount": method["amount"]
                    }
                    receipt_data["paymentMethods"].append(payment_entry)

            # Extract order lines details
            for line in order.lines:
                product_name = line.product_id.name
                product_description = line.product_id.description_sale or product_name
                
                # Per item tax
                item_cost = round(line.price_unit, 2)
                item_tax = round(line.price_subtotal_incl - line.price_subtotal, 2)

                item = {
                    "itemName": product_name,
                    "itemCode": line.product_id.default_code or "0",
                    "itemCost": item_cost,
                    "quantity": line.qty,
                    "tax": item_tax,
                    "productDescription": product_description
                }
                if self.esaal_debug:
                    _logger.info(f"Item Data: {item}")
                receipt_data["receiptItems"].append(item)

            if not receipt_data["receiptItems"]:
                if self.esaal_debug:
                    _logger.warning('Error building receipt_data')
                return "receipt_data"
            return receipt_data

        except Exception as e:
            if self.esaal_debug:
                _logger.error(f"Error generating receipt data: {e}")
            return {}

    def get_customer_info_and_register(self, partner_name, partner_phone, gender, partner_email, token):
        # Validate if the customer exists and register if not
        esaal_id, esaal_name, esaal_lname, esaal_phone, esaal_email = self.validate_api(partner_phone)
        if not esaal_id:
            esaal_id, esaal_name = self.register_customer(partner_name, partner_phone, gender, partner_email, token)
        return esaal_id, esaal_name

    def validate_api(self, partner_phone):
        # Decode the token
        token = self.base64_decode(self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_token', default=''))
        validate_url = f"{self.ESAAL_API_PREFIX}/api/Customer/validate"
        validate_payload = {
            "searchParam": partner_phone
        }

        headers = {'Accept': '*/*', 
                    'Content-Type': 'application/json', 
                    'Authorization': f'Bearer {token}'
        }

        response = requests.get(validate_url, params=validate_payload, headers=headers, verify=True)

        if response.status_code == 201 or response.status_code == 200:
            response_data = response.json()
            esaal_id = response_data['data']['esaalId'] or None
            esaal_name = response_data['data']['firstName'] or None
            esaal_lname = response_data['data']['lastName'] or None
            esaal_phone = response_data['data']['phone'] or None
            esaal_email = response_data['data']['email'] or None
            if self.esaal_debug:
                _logger.info(f"Stored esaalId: {esaal_id} {esaal_name}")
            return esaal_id, esaal_name, esaal_lname, esaal_phone, esaal_email
            
        elif response.status_code == 404:
            if self.esaal_debug:
                _logger.warning(f"Customer Not Found: {response.status_code} {response.text}")
            return None, None, None, None, None
            
        else:
            if self.esaal_debug:
                _logger.warning(f"Validation Error: {response.status_code} {response.text}")
            return None, None, None, None, None

    def register_customer(self, partner_name, partner_phone, gender, partner_email, token):
        # Translate gender to 'M' or 'F'
        gender_code = 'M' if gender.lower() == 'male' else 'F' if gender.lower() == 'female' else ''

        if partner_email:
            pass
        else:
            partner_email = ''

        register_url = f"{self.ESAAL_API_PREFIX}/api/Customer"
        register_payload = {
            "firstName": partner_name.split()[0],
            "lastName": " ".join(partner_name.split()[1:]),
            "phone": partner_phone,
            "email": partner_email,
            "gender": gender_code
        }

        try:
            headers = {'Accept': '*/*', 
                       'Content-Type': 'application/json', 
                       'Authorization': f'Bearer {token}'
            }
            
            response = requests.post(register_url, json=register_payload, headers=headers)
            response.raise_for_status()

            if response.status_code == 201 or response.status_code == 200:
                if self.esaal_debug:
                    _logger.warning(f"Customer Registration Successful: {response.json()}")
                esaal_id, partner_name = self.process_customer_information(partner_phone, token)
                if self.esaal_debug:
                    _logger.warning(f"Received Data from Registration {esaal_id} {partner_name}")
                return esaal_id, partner_name
            else:
                if self.esaal_debug:
                    _logger.warning(f"Customer Registration Error: {response.status_code} {response.text}")
                return None, None

        except requests.RequestException as e:
            if self.esaal_debug:
                _logger.error(f"Error registering customer: {e}")
            return None, None

    def process_customer_information(self, partner_phone, token):
        # Process and retrieve customer information post-registration
        validate_url = f"{self.ESAAL_API_PREFIX}/api/Customer/validate"
        validate_payload = {
            "searchParam": partner_phone
        }

        try:
            headers = {
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(validate_url, params=validate_payload, headers=headers)

            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                esaal_id = response_data['data']['esaalId']
                partner_name = response_data['data']['firstName']

                return esaal_id, partner_name

            response.raise_for_status()

        except requests.RequestException as e:
            if self.esaal_debug:
                _logger.error(f"Error processing customer information: {e}")

        return None, None
    
    def send_receipt(self, receipt_data, token):

        receipt_url = f"{self.ESAAL_API_PREFIX}/api/Customer/receipt"

        try:
            headers = {'Accept': '*/*', 
                       'Content-Type': 'application/json', 
                       'Authorization': f'Bearer {token}'
            }
            
            response = requests.post(receipt_url, json=receipt_data, headers=headers)
            response.raise_for_status()

            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                return response.json()

        except requests.RequestException as e:
            if self.esaal_debug:
                _logger.error(f"Error sending receipt to customer: {e}")
            return {
                "type": "AuthErr",
                "status": "error",
                "message": "Authorization Error"
            }
        
    def validate_mapper(self, order):
        # PoS ID
        pos_mapping_json = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.pos_mapping', default='[]')
        pos_mapping_mode = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_mapper_mode', default=False)
        pos_name = re.sub(r'\s*\(.*?\)\s*', '', order.session_id.config_id.display_name).strip()
        config_id = order.session_id.config_id.id
        branch_name = order.session_id.config_id.warehouse_id.name

        if pos_mapping_mode:
            try:
                pos_mapping = json.loads(pos_mapping_json)
            except json.JSONDecodeError:
                _logger.info("Invalid Mapping")
            
            for entry in pos_mapping:
                if entry.get('pos_name') == pos_name and entry.get('branch_name') == branch_name and entry.get('config_id') == config_id:
                    pos_id_map = entry.get('pos_id')
                    if pos_id_map and isinstance(pos_id_map, str) and re.match(r'^[A-Z]{3}\d{7}$', pos_id_map):
                        return True
                    else:
                        return False

    @api.model
    def create_from_ui(self, orders, *args, **kwargs):
        if self.esaal_debug:
            _logger.info("create_from_ui called with orders: %s", orders)
        
        order_ids = super(PosOrder, self).create_from_ui(orders, *args, **kwargs)
        
        if self.esaal_debug:
            _logger.info("order_ids: %s", order_ids)

        # Fetch existing pos_mapping
        pos_mapping_json = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.pos_mapping', default='[]')
        
        try:
            pos_mapping = json.loads(pos_mapping_json)
        except json.JSONDecodeError:
            _logger.info("Invalid Mapping")
            pos_mapping = []

        for order_dict in order_ids:
            order_id = order_dict['id']
            order = self.browse(order_id)
            
            if order:
                company_name = self.env.user.company_id.name
                pos_name = re.sub(r'\s*\(.*?\)\s*', '', order.session_id.config_id.display_name).strip()
                branch_name = order.session_id.config_id.warehouse_id.name
                config_id = order.session_id.config_id.id
                if self.esaal_debug:
                    _logger.warning(f'Company information Company : {company_name} Branch {branch_name} PoS {pos_name} Number {config_id}')
                
                # Check if pos_name, branch_name, and config_id already exist in pos_mapping
                pos_entry = next((entry for entry in pos_mapping if entry.get('pos_name') == pos_name and entry.get('branch_name') == branch_name and entry.get('config_id') == config_id), None)

                if not pos_entry:
                    # If pos_name, branch_name, and config_id do not exist, add it with a placeholder pos_id
                    pos_mapping.append({
                        'company': company_name,
                        'branch_name': branch_name,
                        'pos_name': pos_name,
                        'config_id': config_id,
                        'pos_id': f'{branch_name} - {pos_name} - {config_id}'  # Placeholder value
                    })

                if self.esaal_debug:
                    _logger.info(f"Processing order ID: {order_id}")
                    _logger.info(f"Mapping: {pos_mapping}")
            else:
                if self.esaal_debug:
                    _logger.warning(f"Order ID {order_id} not found.")
        
        # Store updated pos mapping in JSON format
        self.env['ir.config_parameter'].sudo().set_param('esaal_hook.pos_mapping', json.dumps(pos_mapping))

        pos_mapping_mode = self.env['ir.config_parameter'].sudo().get_param('esaal_hook.esaal_mapper_mode', default=False)

        if pos_mapping_mode:
            if self.validate_mapper(order):
                self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_mapper_state', True)
                if self.esaal_debug:
                    _logger.warning(f"Mapper State enabled")
            else:
                self.env['ir.config_parameter'].sudo().set_param('esaal_hook.esaal_mapper_state', False)
                if self.esaal_debug:
                    _logger.warning(f"Mapper State disabled")

        return order_ids
