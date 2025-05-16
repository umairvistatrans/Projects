# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import requests
from ftplib import FTP_TLS
import base64


class ImportRsrProduct(models.TransientModel):
    _name = 'rsr.product.import.wizard'
    _description = 'RSR Import Wizard'

    name = fields.Char(default=_('New'))
    keywords = fields.Char(string="Keywords", help="Keywords to search the catalog.")
    related_sku = fields.Char(string="Related SKU", help="RSR Stock # for related items.")
    department_ids = fields.Many2many(
        comodel_name='rsr.department',
        string="Departments",
        help="Select departments to search within."
    )
    manufacturer_ids = fields.Many2many(
        comodel_name='rsr.manufacturer',
        string="Manufacturers",
        help="Select manufacturers to search within."
    )
    search_favorites = fields.Boolean(string="Search Favorites", default=False, help="Search within favorite items.")
    with_attributes = fields.Boolean(string="Include Attributes", default=False,
                                     help="Include item attributes in the results.")
    sort_by = fields.Selection([
        ('price-low', 'Price Low to High'),
        ('price-high', 'Price High to Low'),
        ('featured', 'Featured Items'),
        ('relevance', 'Relevance'),
        ('available-quantity', 'Available Quantity'),
    ], string="Sort By", help="Sorting criteria for results.")
    limit = fields.Integer(
        string="Limit",
        default=9999,
        help="Maximum number of items to return. Cannot exceed 9999."
    )
    offset = fields.Integer(string="Offset", default=0, help="Number of items to skip in results.")
    modified_since = fields.Datetime(string="Modified Since", help="Return items modified after this date.")
    with_restrictions = fields.Boolean(string="Include Restrictions", default=False, help="Include item restrictions.")

    import_rule_id = fields.Many2one('rsr.import.rule', string="Import Rule", ondelete="set null", help='Selecting a rule will apply the rule on all products to be imported.')
    import_product_ids = fields.Many2many('rsr.product.data')

    def _get_or_create_manufacturer(self, code, name):
        """
        Helper to get or create a manufacturer.
        """
        if not code:
            return False
        manufacturer = self.env['rsr.manufacturer'].search([('rsr_id', '=', code)], limit=1)
        if not manufacturer:
            manufacturer = self.env['rsr.manufacturer'].create({'rsr_id': code, 'name': name})
        return manufacturer.id

    def _get_or_create_category(self, code, name):
        """
        Helper to get or create a category.
        """
        if not code:
            return False
        category = self.env['rsr.category'].search([('rsr_id', '=', code)], limit=1)
        if not category:
            category = self.env['rsr.category'].create({'rsr_id': code, 'name': name})
        return category.id

    def _generate_rsr_data(self, response):
        """
        Processes the response from the RSR API and generates or updates rsr.product.data records in the database.

        :param response: dict, JSON response from the RSR API
        """
        rsr_product_data_ids = []
        status_code = response.get("StatusCode", "")
        status_message = response.get("StatusMssg", "")

        # Check if the API call was successful
        if status_code != "00":
            raise ValueError(f"API call failed with StatusCode {status_code}: {status_message}")

        # Extract items
        items = response.get("Items", [])
        for item in items:
            # Prepare manufacturer
            manufacturer_code = item.get("ManufacturerCode")
            manufacturer_name = item.get("ManufacturerName")
            manufacturer_id = self._get_or_create_manufacturer(manufacturer_code, manufacturer_name)

            # Prepare category
            category_code = item.get("CategoryId")
            category_name = item.get("CategoryName")
            category_id = self._get_or_create_category(category_code, category_name)

            product_vals = {
                "sku": item.get("SKU"),
                "last_modified": item.get("LastModifiedDate"),
                "upc": item.get("UPC"),
                "product_title": item.get("Title"),
                "manufacturer_id": manufacturer_id,
                "manufacturer_part_number": item.get("ManufacturerPartNumber"),
                "description": item.get("Description"),
                "category_id": category_id,
                "subcategory_name": item.get("SubcategoryName"),
                "exclusive": item.get("Exclusive", 'N'),
                "talo_exclusive": item.get("TaloExclusive", 'N'),
                "coming_soon": item.get("ComingSoon", 'N'),
                "new_item": item.get("NewItem", 'N'),
                "le_resale_only": item.get("LEResaleOnly", 'N'),
                "unit_of_measure": item.get("UnitOfMeasure"),
                "items_per_unit": item.get("ItemsPerUnit"),
                "items_per_case": item.get("ItemsPerCase"),
                "units_per_case": item.get("UnitsPerCase"),
                "nfa": item.get("NFA", "N"),
                "hazard_warning": item.get("HazardWarning"),
                "image_count": item.get("ImageCount"),
                "msrp": item.get("MSRP"),
                "retail_map": item.get("RetailMAP"),
                "inventory_on_hand": item.get("InventoryOnHand"),
                "ground_only": item.get("GroundOnly", 'N'),
                "closeout": item.get("Closeout", 'N'),
                "drop_ship_block": item.get("DropShipBlock", 'N'),
                "drop_shippable": item.get("DropShippable", 'N'),
                "dealer_price": item.get("DealerPrice"),
                "dealer_case_price": item.get("DealerCasePrice"),
                "unit_weight": item.get("UnitWeight"),
                "unit_width": item.get("UnitWidth"),
                "unit_height": item.get("UnitHeight"),
                "unit_length": item.get("UnitLength"),
                "case_weight": item.get("CaseWeight"),
                "case_width": item.get("CaseWidth"),
                "case_height": item.get("CaseHeight"),
                "case_length": item.get("CaseLength"),
            }

            # Process Shipping Restrictions into structured data
            shipping_restrictions = item.get("ShippingRestrictions", [])
            restriction_vals = []
            for restriction in shipping_restrictions:
                restriction_vals.append((0, 0, {
                    "shipping_restriction_state": restriction.get("State", ""),
                    "shipping_restriction_municipality": restriction.get("Municipality", ""),
                    "shipping_restriction_territory": restriction.get("TerritoryRestriction", ""),
                    "shipping_restriction_detail": restriction.get("RestrictionDetail", "")
                }))

            product_vals["shipping_restrictions"] = restriction_vals

            # Process Attributes into structured data
            attributes = item.get("Attributes", [])
            attribute_vals = []
            for attribute in attributes:
                attribute_vals.append((0, 0, {
                    "name": attribute.get("Name", ""),
                    "value": attribute.get("Value", "")
                }))

            product_vals["product_attributes"] = attribute_vals

            new_product = self.env["rsr.product.data"].create(product_vals)
            rsr_product_data_ids.append(new_product.id)

        self.import_product_ids = [(6, 0, rsr_product_data_ids)]
        # Fetch images for products with positive image count
        # self._fetch_images_for_products(rsr_product_data_ids)

    def _make_api_request(self):
        """
        Make the request to the RSR API and return the response.

        :return: JSON response from the RSR API
        """
        # Get credentials and configuration
        api_url = "https://test.rsrgroup.com/api/rsrbridge/1.0/pos/get-items"  # Replace with config parameter URL.
        username = '99901' # Replace with config parameter.
        password = 'webuser1' # Replace with config parameter.

        # Prepare headers and payload
        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "Username": username,
            # Retrieve the RSR username from config parameters
            "Password": password,
            # Retrieve the RSR password from config parameters
            "POS": "I",  # RSR POS (can be configured similarly if needed)
            "Keywords": self.keywords or "",  # If no keyword is provided, it's sent as an empty string
            "RelatedSKU": self.related_sku or "",  # Related SKU, if any
            "Departments": ",".join([dept.rsr_id for dept in self.department_ids]) or "",
            # Department codes as a comma-separated list
            "Manufacturers": ",".join([manufacturer.rsr_id for manufacturer in self.manufacturer_ids]) or "",
            # Manufacturer codes as a comma-separated list
            "SearchFavorites": self.search_favorites,  # Whether to search within the customer's favorites list
            "WithAttributes": self.with_attributes,  # Whether to include attributes in the results
            "SortBy": self.sort_by or "relevance",  # Default sort is by relevance, or user-selected option
            "Limit": self.limit,  # Maximum number of items to return
            "Offset": self.offset,  # Number of items to skip
            "ModifiedSince": self.modified_since.strftime("%Y-%m-%d %H:%M:%S") if self.modified_since else "",
            # Date for modified items, formatted properly
            "WithRestrictions": self.with_restrictions,  # Whether to include item restrictions
        }

        # Print the payload to debug
        print("API Request Payload:", payload)

        # Make the API request
        try:
            print("Making API request to:", api_url)
            print("Using credentials - Username:", username, "Password:", password)
            response = requests.post(api_url, json=payload, headers=headers, auth=(username, password), timeout=30)

            # Print the response status code and body to debug
            print("API Response Status Code:", response.status_code)
            print("API Response Body:", response.text)

            if response.status_code == 200:
                return response.json()
            else:
                raise UserError(f"Failed to fetch data from RSR API: {response.status_code} {response.text}")

        except requests.exceptions.RequestException as e:
            print("Error while making request to RSR API:", str(e))
            raise UserError(f"Error while making request to RSR API: {str(e)}")

    def _fetch_images_for_products(self, product_ids):
        """
        Navigate through FTPS directories and print the contents of
        category-specific folders for products with a positive image count.
        """
        host = "ftps.rsrgroup.com"
        port = 2222
        username = "99901"
        password = "1FgOFpWr"

        try:
            # Establish FTPS connection
            ftps = FTP_TLS()
            ftps.connect(host, port)
            ftps.login(user=username, passwd=password)
            ftps.prot_p()

            # Navigate to the base image folder
            ftps.cwd('/ftp_images/categories')
            print("Connected to FTPS and navigated to /ftp_images/categories")

            # Get products
            products = self.env['rsr.product.data'].browse(product_ids)

            for product in products:
                if product.image_count > 0 and product.category_id:
                    # Derive the folder name from the product category
                    category_folder = product.category_id.name.lower()
                    category_folder = category_folder.replace('and ', '').replace('& ', '').replace(' ', '-')

                    try:
                        # Navigate to the category folder
                        ftps.cwd(category_folder)
                        print(f"Navigated to category folder: {category_folder}")

                        # List and print the contents of the folder
                        file_list = ftps.nlst()
                        print(f"Contents of folder '{category_folder}': {file_list}")

                        # Navigate back to the base category folder for the next product
                        ftps.cwd('..')

                    except Exception as e:
                        print(f"Error navigating to folder '{category_folder}': {str(e)}")
                        # Continue to the next product if folder navigation fails
                        continue

        except Exception as e:
            print(f"Error while connecting to FTPS server: {str(e)}")
            raise UserError(f"Error while connecting to FTPS server: {str(e)}")

        finally:
            ftps.quit()
            print("FTPS connection closed.")

    def action_generate_products(self):
        """Button action to fetch products from RSR API and generate records."""
        self.env['rsr.product.data'].search([]).unlink()
        response = self._make_api_request()
        self._generate_rsr_data(response)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Products Received"),
                'message': f'{len(self.import_product_ids)} Products received successfully from RSR',
                'next': {
                    'type': 'ir.actions.act_window_close'
                },
            }
        }

    def action_open_import_confirmation_wizard(self):
        """Open the confirmation wizard with products marked for import."""
        marked_products = self.import_product_ids.filtered(lambda p: p.status == 'marked')

        # If no products are marked, raise a validation error
        if not marked_products:
            raise ValidationError("Please select products to import first.")

        # Open the confirmation wizard
        wizard = self.env['rsr.product.import.confirm.wizard'].create({'product_ids': [(6, 0, marked_products.ids)]})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import RSR Products',
            'res_model': 'rsr.product.import.confirm.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('rsr_product.view_rsr_product_import_confirm_wizard_form').id,
            'res_id': wizard.id,
            'target': 'new',
            'context': {'main_wizard_id': self.id}
        }

    @api.constrains('limit')
    def _check_limit(self):
        """Ensure that the limit does not exceed 9999."""
        for record in self:
            if record.limit > 9999:
                raise ValidationError(_("The 'Limit' field cannot be greater than 9999."))

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = f'RSR Products Import - {str(fields.Date.today())}'

        res = super().create(vals)

        if res.import_rule_id:
            res.import_product_ids.write({'import_rule_id': res.import_rule_id.id})

        return res

    def write(self, vals):
        res = super(ImportRsrProduct, self).write(vals)
        if 'import_rule_id' in vals:
            self.import_product_ids.write({'import_rule_id': self.import_rule_id.id if self.import_rule_id else False})
        return res


class ConfirmImportRsrProduct(models.TransientModel):
    _name = 'rsr.product.import.confirm.wizard'
    _description = 'RSR Product Import Confirmation Wizard'

    product_ids = fields.Many2many('rsr.product.data', string="Products to Import", domain=[('status', '=', 'marked')])

    def action_import(self):
        """Placeholder for importing the products."""
        # You can add the logic to import products here
        return {'type': 'ir.actions.act_window_close'}
