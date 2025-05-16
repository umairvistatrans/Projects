from odoo import models, fields, _
import xmlrpc.client
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo import api, models
import logging
_logger = logging.getLogger(__name__)

# url_odoo13 = 'https://7md-ae-karan-10027341.dev.odoo.com'
url_odoo13 = 'https://7md-ae.odoo.com'
db_odoo13 = '7md-ae-master-1152146'
username_odoo13 = 'test'
password_odoo13 = '123456'

common_odoo13 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo13))
uid_odoo13 = common_odoo13.authenticate(db_odoo13, username_odoo13, password_odoo13, {})

models_odoo13 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo13))


class POSSession(models.Model):
    _inherit = 'pos.session'

    @api.constrains('config_id')
    def _check_pos_config(self):
        if self.search_count([
            ('state', '!=', 'closed'),
            ('config_id', '=', self.config_id.id),
            ('rescue', '=', False)
        ]) > 1:
            return


class POSOrderSync(models.TransientModel):
    _name = 'pos.order.wizard.syn'

    date = fields.Date(string='Date')

    def import_pos_config(self, conf_id):
        if conf_id:
            search_domain = [('id', '=', conf_id)]
            pos_config_ids_odoo13 = models_odoo13.execute_kw(
                db_odoo13, uid_odoo13, password_odoo13,
                'pos.config', 'search_read', [search_domain]
            )

            if len(pos_config_ids_odoo13):
                for config in pos_config_ids_odoo13:
                    pos_config = self.env['pos.config'].search(
                        [('name', '=', config.get('name'))])
                    if not pos_config and config.get('name'):
                        new_pos_data = {
                            'name': config.get('name'),
                        }
                        return self.env['pos.config'].create(new_pos_data).id
                    return pos_config.id
            else:
                return False
        else:
            return False

    def import_pos_session(self, session_id):
        if session_id:
            search_domain = [('id', '=', session_id)]
            pos_order_ids_odoo13 = models_odoo13.execute_kw(
                db_odoo13, uid_odoo13, password_odoo13,
                'pos.session', 'search_read', [search_domain]
            )
            # raise ValidationError(_("Invalid whatsapp number.%s") % pos_order_ids_odoo13)
            if len(pos_order_ids_odoo13):
                for config in pos_order_ids_odoo13:
                    pos_config = self.env['pos.session'].search(
                        [('name', '=', config.get('name'))])
                    if not pos_config and config.get('name'):
                        new_pos_data = {
                            'name': config.get('name'),
                            'user_id': self.env.user.id,
                            'config_id': self.import_pos_config(config.get('config_id')[0]),
                            'state': 'closing_control'
                        }
                        return self.env['pos.session'].create(new_pos_data)
                    else:
                        return pos_config
            else:
                return False
        else:
            return False

    def perform_action(self):
        try:
            start_date_str = self.date.strftime('%Y-%m-%d 00:00:00')
            end_date_str = self.date.strftime('%Y-%m-%d 23:59:59')
            search_domain = [('date_order', '>=', start_date_str),
                             ('date_order', '<=', end_date_str)]

            batch_size = 200
            offset = 0
            count = 0
            while True:
                pos_order_ids_odoo13 = models_odoo13.execute_kw(
                    db_odoo13, uid_odoo13, password_odoo13,
                    'pos.order', 'search_read', [search_domain],
                    {'limit': batch_size, 'offset': offset}
                )
                if not pos_order_ids_odoo13:
                    break
                # raise ValidationError(_("order.%s") % pos_order_ids_odoo13)
                # if len(pos_order_ids_odoo13):
                for order in pos_order_ids_odoo13:
                    pos_order = self.env['pos.order'].search(
                        [('date_order', '=', order.get('date_order')), ('name', '=', order.get('name'))])

                    if not pos_order:
                        session_id = False
                        employee_id = False
                        partner_id = False
                        fiscal_position_id = False
                        table_id = False
                        if order.get('session_id'):
                            session = self.env['pos.session'].search(
                                [('name', '=', order.get('session_id')[1])])
                            if not session:
                                session = self.import_pos_session(order.get('session_id')[0])
                            session_id = session.id
                        if order.get('employee_id'):
                            employee = self.env['hr.employee'].search(
                                [('name', '=', order.get('employee_id')[1])])
                            if not employee:
                                employee = self.env['hr.employee'].create({
                                    'name': order.get('employee_id')[1]
                                })
                            employee_id = employee[0].id if len(employee) > 1 else employee.id
                        if order.get('partner_id'):
                            partner = self.env['res.partner'].search(
                                [('name', '=', order.get('partner_id')[1])])
                            if not partner:
                                partner = self.env['res.partner'].create({
                                    'name': order.get('partner_id')[1]
                                })
                            partner_id = partner[0].id if len(partner) > 1 else partner.id
                        if order.get('fiscal_position_id'):
                            fiscal = self.env['account.fiscal.position'].search(
                                [('name', '=', order.get('fiscal_position_id')[1])])
                            if not fiscal:
                                fiscal = self.env['account.fiscal.position'].create({
                                    'name': order.get('fiscal_position_id')[1]
                                })
                            fiscal_position_id = fiscal[0].id if len(fiscal) > 1 else fiscal.id

                        new_order_data = {
                            'name': order.get('name'),
                            'date_order': order.get('date_order'),
                            'session_id': session_id,
                            'employee_id': employee_id,
                            'partner_id': partner_id,
                            'fiscal_position_id': fiscal_position_id,
                            'table_id': table_id,
                            'amount_tax': order.get('amount_tax'),
                            'amount_total': order.get('amount_total'),
                            'amount_paid': order.get('amount_paid'),
                            'amount_return': order.get('amount_return'),
                        }
                        pos_order = self.env['pos.order'].create(new_order_data)
                        order_lines = models_odoo13.execute_kw(
                            db_odoo13, uid_odoo13, password_odoo13,
                            'pos.order.line', 'search_read', [[('order_id', '=', order.get('id'))]]
                        )
                        for order_line in order_lines:
                            search_product_domain = [('id', '=', order_line.get('product_id')[0])]
                            product_id_odoo13 = models_odoo13.execute_kw(
                                db_odoo13, uid_odoo13, password_odoo13,
                                'product.product', 'search_read', [search_product_domain]
                            )
                            product_id = self.env['product.product'].search(
                                [('name', '=', product_id_odoo13[0].get('name')),
                                 ('default_code', '=', product_id_odoo13[0].get('default_code'))])
                            if not product_id:
                                vals = {
                                    "name": product_id_odoo13[0].get('name'),
                                    'default_code': product_id_odoo13[0].get('default_code'),
                                    "standard_price": product_id_odoo13[0].get('standard_price'),
                                    "list_price": product_id_odoo13[0].get('list_price'),
                                }
                                product_id = self.env['product.product'].create(vals)
                            new_order_line = self.env['pos.order.line'].create({
                                'product_id': product_id.id,
                                'full_product_name': product_id.name,
                                'name': order_line.get('name'),
                                'qty': order_line.get('qty'),
                                'price_unit': order_line.get('price_unit'),
                                'order_id': pos_order.id,
                                'price_subtotal': order_line.get('price_subtotal'),
                                'price_subtotal_incl': order_line.get('price_subtotal_incl'),
                            })
                        if order.get('state') == 'invoiced':
                            pos_order.action_pos_order_invoice()
                        print("New POS Order created with ID:", pos_order.id)
                        count += 1
                        if count % 10 == 0:
                            _logger.info("order created: %s ", count)
                            self.env.cr.commit()
                offset += batch_size
            return True
        except Exception as e:
            _logger.error("An error occurred: %s", e, exc_info=True)
            raise ValidationError("An error occurred: %s" % e)
