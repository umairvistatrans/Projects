# -*- coding: utf-8 -*-
import base64
import calendar as cal
import json
import logging
from collections import OrderedDict
from datetime import datetime, date
from datetime import timedelta
from io import BytesIO

from babel.dates import format_datetime, format_date
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

from odoo import http, _
from odoo.http import request, route
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from odoo.tools.misc import babel_locale_parse, get_lang

_logger = logging.getLogger(__name__)


def _formated_weekdays(locale):
    """ Return the weekdays' name for the current locale
        from Mon to Sun.
        :param locale: locale
    """
    formated_days = [
        format_date(date(2021, 3, day), 'EEE', locale=locale)
        for day in range(1, 8)
    ]
    # Get the first weekday based on the lang used on the website
    first_weekday_index = int(request.env['res.lang'].search([('code', '=',request.env.lang)],limit=1).week_start)
    # Reorder the list of days to match with the first weekday
    formated_days = list(formated_days[first_weekday_index:] + formated_days)[:7]
    return formated_days


class OeRoutePlanningPortal(CustomerPortal):

    @http.route('/get_states', type='http', auth='public', methods=['GET'], csrf=False)
    def get_states(self, country_id):
        states = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
        states_list = [{'id': state.id, 'name': state.with_context(lang='en_US').name} for state in states]
        return request.make_response(json.dumps(states_list), headers=[('Content-Type', 'application/json')])

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        user = request.env.user
        values = self._prepare_portal_layout_values()
        values.update({'user_type': user.user_type, })
        return request.render("portal.portal_my_home", values)

    def _get_appointment_slots(self, timezone, filter_users=None, filter_resources=None, asked_capacity=1,
                               reference_date=None):
        """ Fetch available slots to book a visit.

        :param str timezone: timezone string e.g.: 'Europe/Brussels' or 'Etc/GMT+1'
        :param <res.users> filter_users: filter available slots for those users
        :param <appointment.resource> filter_resources: filter available slots for those resources
        :param int asked_capacity: the capacity the user want to book.
        :param datetime reference_date: starting datetime to fetch slots. If not given, use now.

        :returns: list of dicts (1 per month) containing available slots per week
        """

        if not reference_date:
            reference_date = datetime.now()

        start_of_month = reference_date.replace(day=1)
        end_of_month = (start_of_month + timedelta(
            days=cal.monthrange(reference_date.year, reference_date.month)[1])).replace(hour=23, minute=59, second=59)

        domain = [('scheduled_date', '>=', start_of_month.strftime(dtf)),
                  ('scheduled_date', '<=', end_of_month.strftime(dtf))]

        if filter_users:
            domain.append(('user_id', 'in', filter_users.ids))
        if filter_resources:
            domain.append(('resource_id', 'in', filter_resources.ids))

        visits = request.env['oe.visits'].search(domain)

        months = []
        while start_of_month.month <= end_of_month.month:
            month_visits = visits.filtered(lambda v: start_of_month.month == v.scheduled_date.month)
            weeks = self._generate_weeks(start_of_month)
            months.append(
                {'id': start_of_month.month, 'month': format_datetime(start_of_month, 'MMMM Y'), 'weeks': weeks,
                 'visits': month_visits, })
            start_of_month = start_of_month + timedelta(
                days=cal.monthrange(start_of_month.year, start_of_month.month)[1])
            months.append({
                'id': start_of_month.month,
                'month': format_datetime(start_of_month, 'MMMM Y'),
                'weeks': weeks,
                'visits': month_visits,
            })
            start_of_month = start_of_month + timedelta(
                days=cal.monthrange(start_of_month.year, start_of_month.month)[1])
        month_id = 0
        for month in months:
            month['seq_id'] = month_id
            month_id += 1

        return months

    def _generate_weeks(self, start_date):
        """Generate the weeks for a given month."""
        weeks = []
        month_calendar = cal.Calendar().monthdatescalendar(start_date.year, start_date.month)
        for week_dates in month_calendar:
            week = []
            for date in week_dates:
                week.append({'date': date, })
            weeks.append(week)
        return weeks

    @http.route('/my/visits', type='http', auth='user', website=True)
    def portal_my_visits(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='name', groupby=None, **kw):
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
        start_of_month = today.replace(day=1)  # First day of the current month
        end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1)).day

        search_filters = {'all': {'domain': [], 'label': 'All'},
                          'today': {'domain': [('scheduled_date', '=', today)], 'label': 'Today'},
                          'yesterday': {'domain': [('scheduled_date', '=', today - timedelta(days=1))],
                                        'label': 'Yesterday'},
                          'tomorrow': {'domain': [('scheduled_date', '=', today + timedelta(days=1))],
                                       'label': 'Tomorrow'},
                          'this_week': {'domain': [('scheduled_date', '>=', start_of_week),
                                                   ('scheduled_date', '<=',
                                                    today + timedelta(days=6 - today.weekday()))],
                                        'label': 'This Week'},
                          'this_month': {'domain': [('scheduled_date', '>=', start_of_month),
                                                    (
                                                    'scheduled_date', '<=', today.replace(day=28) + timedelta(days=4))],
                                         'label': 'This Month'},  # Handling month end dates
                          }
        domain_user = ('user_id', '=', request.env.user.id)
        visit_object = request.env['oe.visits']
        if not filterby:
            filterby = 'today'
        if filterby == 'custom':
            search_filters['custom'] = {'domain': [('scheduled_date', '=', date_begin)]}
        domain = search_filters.get(filterby, search_filters.get('all'))['domain']
        domain.append(domain_user)
        if search_in == 'name':
            n_domain = ('name', 'ilike', search)
            domain.append(n_domain)
        elif search_in == 'users':
            user_id = request.env['res.users'].sudo().search([('name', 'ilike', search)], limit=1)
            u_domain = ('user_id', '=', user_id.id)
            domain.append(u_domain)
        elif search_in == 'customer':
            cust_id = request.env['res.partner'].sudo().search([('name', 'ilike', search)], limit=1)
            c_domain = ('customer_id', '=', cust_id.id)
            domain.append(c_domain)
        elif search_in == 'Route':
            r_id = request.env['oe.route.master'].sudo().search([('name', 'ilike', search)], limit=1)
            r_domain = ('route_id', '=', r_id.id)
            domain.append(r_domain)
        if 'timezone' not in request.session:
            request.session['timezone'] = 'UTC'

        visits = visit_object.search(domain)
        values = self._prepare_tasks_values(page, date_begin, date_end, sortby, search, search_in, groupby,
                                            domain=False)
        formated_days = _formated_weekdays(get_lang(request.env).code)
        today_date = datetime.today().date()
        slots = self._get_appointment_slots(request.session['timezone'], filter_users=request.env.user, )
        # pager
        pager_vals = values['pager']
        # pager_vals['url_args'].update(filterby=filterby)
        pager = portal_pager(**pager_vals)
        search_input_values = {'visit_name': {'input': 'name', 'label': _('Search in Visit Name'), 'order': 1},
                               'users': {'input': 'users', 'label': _('Search in Users'), 'order': 2},
                               'customer': {'input': 'customer', 'label': _('Search in Customer'), 'order': 3},
                               'route_id': {'input': 'Route', 'label': _('Search in Route'), 'order': 4}, }
        values.update(
            {'my_visits': visits, 
            'pager': pager, 
            'default_url': '/my/visits', 
            'searchbar_inputs': search_input_values,
             # need to add here
             # 'searchbar_filters': '/my/visits',   # need to add here
             'searchbar_filters': OrderedDict(sorted(search_filters.items())), 
             'filterby': filterby,
             'page_name': 'Visits',  # 'task_url': 'visits',
             'slots': slots, 
             'formatted_days': formated_days, 
             'today_date': today_date,
             'month_first_available': today.month,
             'capacity': 1,
             'month_kept_from_update': today.month,
             'timezone': request.session['timezone'],

             })
        return request.render("oe_route_planning_portal.portal_my_visits", values)

    @http.route('/get_routes_by_partner/<int:partner_id>', type='http', auth='user', website=True, csrf=False)
    def get_routes_by_partner(self, partner_id):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        routes = request.env['oe.route.master'].sudo().search([])
        default_route_id = partner.route_id.id if partner.route_id else None
        # Return JSON response indicating success or error
        if routes:
            # Record creation was successful
            return json.dumps({'success': True, 'routes': [{'id': route.id, 'name': route.name} for route in routes],
                               'default_route_id': default_route_id or False})
        else:
            # Record creation failed
            return json.dumps({'success': False, 'message': 'Failed to create visit'})

    @http.route('/unplanned_visit/submit_form', type='http', auth='user', website=True, csrf=False)
    def unplanned_submit_form(self, **post):
        partner_id = post.get('partner_id')
        current_date = post.get('current_date')
        route_id = post.get('route_id')

        # Create a record in the oe_visit table
        visit = request.env['oe.visits'].sudo().create(
            {'user_id': request.env.user.id, 'customer_id': partner_id, 'scheduled_date': current_date,
             'route_id': int(route_id), 'visit_type': 'unplanned',
             # Add any additional fields you need to set for the visit record
             })

        # Return JSON response indicating success or error
        if visit:
            # Record creation was successful
            return json.dumps({'success': True, 'message': 'Visit %s created' % visit.name})
        else:
            # Record creation failed
            return json.dumps({'success': False, 'message': 'Failed to create visit'})

    @http.route('/my/visits/<int:visit_id>', type='http', auth='user', website=True)
    def visit_detail(self, visit_id, **kwargs):
        # Fetch the visit record from the database
        visit = request.env['oe.visits'].sudo().browse(visit_id)
        if not visit.exists():
            return request.not_found()

        # Render the visit details using a template
        company_product = visit.customer_id.product_ids
        material_product = visit.customer_id.material_ids
        competitor_product = visit.customer_id.competitor_ids
        competitor_material = visit.customer_id.competitor_material_ids
        partners = http.request.env['res.partner'].sudo().search([])
        current_date = datetime.now().date()
        return request.render('oe_route_planning_portal.portal_my_visit', {
            'visit': visit,
            'access_token': request.env['oe.visits'].sudo().with_user(request.env.user),
            'company_product': company_product,
            'material_product': material_product,
            'competitor_product': competitor_product,
            'competitor_material': competitor_material,
            'partners': partners,
            'current_date': current_date

        })

    @http.route('/update_status', type='http', auth='user', website=True, csrf=False)
    def update_status(self, visit_id=None, access_token=None, **kwargs):
        if visit_id:
            try:
                visit = http.request.env['oe.visits'].sudo().browse(int(visit_id))
                if visit and kwargs.get('status') == 'reschedule':
                    visit.state = 're_scheduled'
                    return "Request Re-Schedule successfully"
                elif visit and kwargs.get('status') == 'cancel':
                    visit.state = 'cancelled'
                    return "Request Canceled successfully"
                else:
                    return "Error: Visit not found"
            except Exception as e:
                return str(e)
        return "Error: Invalid Visit ID"

    @http.route('/update_latitude', type='http', auth='user', website=True)
    def update_latitude(self, **kwargs):
        # Extract latitude, longitude, and task_id from the request parameters
        latitude = kwargs.get('latitude')
        longitude = kwargs.get('longitude')
        visit_id = kwargs.get('visit_id')
        action = kwargs.get('action')
        response = {'success': False, 'message': 'Unknown error occurred'}
        visit = request.env['oe.visits'].sudo().browse(int(visit_id))
        if visit:
            today = datetime.now().date()
            if action == 'checkin':
                if visit.scheduled_date != today:
                    response['message'] = "You can only check in on the scheduled date."
                    return request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                distance = visit.get_distance_meter(lat1=float(latitude), lon1=float(longitude))
                if distance >= request.env.company.distance_meters:
                    response['message'] = "You can't check in from a remote location"
                    return request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                visit.write({
                    'start_latitude': latitude,
                    'start_longitude': longitude,
                    'start_date_time': datetime.now(),
                    'state': 'in_progress'
                })
                response['success'] = True
                response['message'] = "Checkin Successfully"
            else:
                visit.write({
                    'end_latitude': latitude,
                    'end_longitude': longitude,
                    'end_date_time': datetime.now()
                })
                response['success'] = True
                response['message'] = "Checkout Successfully"
        else:
            response['message'] = "Visit not found"
        return request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})

    def _decode_base64(self, data):
        if data:
            decoded_data = base64.b64decode(data.split(',')[1])
            return base64.b64encode(BytesIO(decoded_data).getvalue()).decode('utf-8')
        return None

    def _create_attachment(self, visit, image_data):
        attachment = request.env['ir.attachment'].create({
            'name': 'Image',
            'type': 'binary',
            'datas': self._decode_base64(image_data),
            'res_model': 'oe.visits',
            'res_id': visit.id,
        })
        return attachment.id

    @http.route('/save_quantity', type='http', auth='user', website=True, csrf=False)
    def save_quantity(self, visit_id=None, feedback=None, access_token=None, **kwargs):
        if visit_id:
            try:
                visit = http.request.env['oe.visits'].sudo().browse(int(visit_id))
                if not visit:
                    return "Error: Visit not found"

                visit.remarks = feedback
                visit.state = 'completed'
                quantities = json.loads(kwargs.get('quantities', '{}'))
                availabilities = json.loads(kwargs.get('availability', '{}'))
                company_material_comments = json.loads(kwargs.get('company_material_comments', '{}'))
                competitor_products_comments = json.loads(kwargs.get('competitor_products_comments', '{}'))
                competitor_materials_comments = json.loads(kwargs.get('competitor_materials_comments', '{}'))
                company_material_images = json.loads(kwargs.get('company_material_images', '{}'))
                competitor_products_images = json.loads(kwargs.get('competitor_products_images', '{}'))
                competitor_materials_images = json.loads(kwargs.get('competitor_materials_images', '{}'))
                multiple_images_data = json.loads(kwargs.get('multiple_images_data'))
                # _logger.error(_('ERROR: Something really bad happened!:: %s')%multiple_images_data)
                attachment_list = []
                for image_data in multiple_images_data:
                    base64_data = image_data.split(',')[1]
                    decoded_data = base64.b64decode(base64_data)

                    attachment_vals = {'name': 'image.png', 'type': 'binary', 'mimetype': 'image/png', }
                    attachment_file = BytesIO(decoded_data)
                    attachment_vals['datas'] = base64.b64encode(attachment_file.getvalue()).decode('utf-8')
                    attachment_id = http.request.env['ir.attachment'].sudo().create(attachment_vals).id
                    visit.photo_ids = [(4, attachment_id)]

                for product_id, quantity in quantities.items():
                    if product_id and quantity:
                        product = http.request.env['product.product'].sudo().browse(int(product_id))
                        if not product:
                            return f"Error: Product with ID {product_id} not found"
                        existing_product = visit.comp_products_line_ids.filtered(
                            lambda p: p.product_id.id == product.id)
                        if existing_product:
                            existing_product.quantity = int(quantity)
                            existing_product.availability = 'available'
                        else:
                            visit.write({'comp_products_line_ids': [(0, 0, {'product_id': product.id,
                                                                            'quantity': int(quantity),
                                                                            'availability': 'available'})]})
                for product_id, availability in availabilities.items():
                    if product_id and availability:
                        product = http.request.env['product.product'].sudo().browse(int(product_id))
                        if not product:
                            return f"Error: Product with ID {product_id} not found"
                        existing_product = visit.comp_products_line_ids.filtered(
                            lambda p: p.product_id.id == product.id)
                        if existing_product:
                            if availability == 'out_of_stock':
                                existing_product.quantity = 0
                                existing_product.availability = availability
                        else:
                            if availability == 'out_of_stock':
                                visit.write({'comp_products_line_ids': [(0, 0, {'product_id': product.id,
                                                                                'availability': availability if availability == 'out_of_stock' else False})]})

                for product_id, comment in company_material_comments.items():
                    if product_id and comment:
                        product = http.request.env['product.product'].sudo().browse(int(product_id))
                        if not product:
                            return f"Error: Product with ID {product_id} not found"
                        existing_product = visit.comp_material_line_ids.filtered(
                            lambda p: p.product_id.id == product.id)
                        if existing_product:
                            existing_product.comment = comment
                            if product_id in company_material_images:
                                existing_product.photo = self._decode_base64(company_material_images[product_id])
                        else:
                            visit.write({'comp_material_line_ids': [(0, 0,
                                                                     {'product_id': product.id, 'comment': comment,
                                                                      'photo': self._decode_base64(
                                                                          company_material_images.get(product_id,
                                                                                                      ''))})]})

                for product_id, comment in competitor_products_comments.items():
                    if product_id and comment:
                        product = http.request.env['product.product'].sudo().browse(int(product_id))
                        if not product:
                            return f"Error: Product with ID {product_id} not found"
                        existing_product = visit.com_products_line_ids.filtered(lambda p: p.product_id.id == product.id)
                        if existing_product:
                            existing_product.comment = comment
                            if product_id in competitor_products_images:
                                existing_product.photo = self._decode_base64(competitor_products_images[product_id])
                        else:
                            visit.write({'com_products_line_ids': [(0, 0, {'product_id': product.id, 'comment': comment,
                                                                           'photo': self._decode_base64(
                                                                               competitor_products_images.get(
                                                                                   product_id, ''))})]})

                for product_id, comment in competitor_materials_comments.items():
                    if product_id and comment:
                        product = http.request.env['product.product'].sudo().browse(int(product_id))
                        if not product:
                            return f"Error: Product with ID {product_id} not found"
                        existing_product = visit.com_material_line_ids.filtered(lambda p: p.product_id.id == product.id)
                        if existing_product:
                            existing_product.comment = comment
                            if product_id in competitor_materials_images:
                                existing_product.photo = self._decode_base64(competitor_materials_images[product_id])
                        else:
                            visit.write({'com_material_line_ids': [(0, 0, {'product_id': product.id, 'comment': comment,
                                                                           'photo': self._decode_base64(
                                                                               competitor_materials_images.get(
                                                                                   product_id, ''))})]})

                return "Quantity Updated Successfully"
            except Exception as e:
                return str(e)
        return "Error: Invalid Visit ID"

    @http.route('/my/products', type='http', auth='user', website=True)
    def portal_my_products(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                           search_in='content', groupby=None, **kw):

        search_filters = {
            'all': {'domain': [], 'label': 'All'},
        }
        domain_user = ('create_uid', '=', request.env.user.id)

        product_object = request.env['oe.new.products']
        if not filterby:
            filterby = 'today'
        domain = search_filters.get(filterby, search_filters.get('all'))['domain']

        domain.append(domain_user)
        if search_in == 'product_name':
            p_domain = ('product_name', 'ilike', search)
            domain.append(p_domain)
        elif search_in == 'brand_id':
            brand_id = request.env['product.brand'].sudo().search([('name', 'ilike', search)], limit=1)
            b_domain = ('brand_id', 'in', brand_id.ids)
            domain.append(b_domain)

        if 'timezone' not in request.session:
            request.session['timezone'] = 'UTC'

        products = product_object.search(domain)

        #
        values = self._prepare_tasks_values(page, date_begin, date_end, sortby, search, search_in, groupby,
                                            domain=False)
        formated_days = _formated_weekdays(get_lang(request.env).code)
        today_date = datetime.today().date()
        slots = self._get_appointment_slots(
            request.session['timezone'],
            filter_users=request.env.user,
        )
        # pager
        pager_vals = values['pager']
        pager = portal_pager(**pager_vals)
        search_input_values = {
            'product_name': {'input': 'product_name', 'label': _('Search by Product Name'), 'order': 1},
            # 'type': {'input': 'product_type', 'label': _('Search by Type'), 'order': 2},
            'brand': {'input': 'brand_id', 'label': _('Search by Brand'), 'order': 2},
        }

        search_in = request.params.get('search_in', 'product_name')

        values.update({
            'my_products': products,
            'pager': pager,
            'default_url': '/my/products',
            'searchbar_inputs': search_input_values,  # need to add here
            # 'searchbar_filters': '/my/visits',   # need to add here
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(search_filters.items())),
            'filterby': filterby,
            'page_name': 'Products',
            # 'task_url': 'visits',
            'slots': slots,
            'formatted_days': formated_days,
            'today_date': today_date,
            'month_first_available': 0,  # Assuming the first month is available
            'capacity': 1,  # Assuming capacity of 1 for simplicity
            'month_kept_from_update': False,
            'timezone': request.session['timezone'],

        })
        return request.render("oe_route_planning_portal.portal_my_products", values)

    @http.route('/new_product/submit_form', type='http', auth='user', website=True, csrf=False)
    def new_product_submit_form(self, update_product=False, **post):
        data = json.loads(request.httprequest.data)
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        product_image = data.get('product_image')
        product_type = data.get('product_type')
        brand = data.get('brand')
        notes = data.get('notes')
        internal_reference = data.get('internal_reference')
        decoded_data = False
        if product_image:
            decoded_data = base64.b64decode(product_image)

        if not product_image and not product_id:
            _logger.error('Product image is missing')
            return {'success': False, 'message': 'Product image is required'}

        brand_id = False

        if brand:
            brand_search = request.env['product.brand'].sudo().search([('name', '=', brand)], limit=1)
            if brand_search:
                brand_id = brand_search
            else:
                brand_id = request.env['product.brand'].sudo().create({'name': brand})
        _logger.error(_('Product brand: %s') % brand)

        # Create a record in the oe_visit table
        if not product_id:
            product = request.env['oe.new.products'].sudo().create({
                'product_name': product_name,
                'product_type': product_type,
                'brand_id': brand_id.id if brand_id else False,
                'notes': notes,
                'default_code': internal_reference,
                'photo': base64.b64encode(BytesIO(decoded_data).getvalue()).decode('utf-8'),
            })
            if product:
                return json.dumps({'success': True, 'message': f'New Product {product.product_name} created'})
            else:
                return json.dumps({'success': False, 'message': 'Failed to create Product'})
        elif product_id:
            product = request.env['oe.new.products'].browse(int(product_id))
            product.sudo().write({
                'product_name': product_name,
                'product_type': product_type,
                'brand_id': brand_id.id if brand_id else False,
                'notes': notes,
                'default_code': internal_reference,
            })
            if decoded_data and product_image:
                product.sudo().write({
                    'photo': base64.b64encode(BytesIO(decoded_data).getvalue()).decode('utf-8'),
                })

            if product:
                return json.dumps({'success': True, 'message': f'Product {product.product_name} Updated'})
            else:
                return json.dumps({'success': False, 'message': 'Failed to Update Product'})

        # Return JSON response indicating success or error

    @http.route('/get/product/values', type='http', auth='user', methods=['POST'], csrf=False)
    def get_product_values_custom(self, **post):
        data = json.loads(request.httprequest.data)
        product_id = data.get('product_id')
        # Fetch product information from database
        product = request.env['oe.new.products'].browse(int(product_id))

        if product.photo:
            photo_base64 = base64.b64encode(product.photo).decode('utf-8')

        if product:
            response_data = {
                'success': True,
                'product_name': product.product_name,
                'product_type': product.product_type,
                'brand': product.brand_id.name,
                'internal_reference': product.default_code,
                'notes': product.notes,
                'product_image_url': '/web/image/oe.new.products/' + str(product.id) + '/photo',
                'product_id': str(product.id),
            }
            return json.dumps(response_data)

        else:
            return json.dumps({'success': False, 'message': 'Failed to create Product'})

    @http.route('/my/customers', type='http', auth='user', website=True)
    def portal_my_customers(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                            search_in='content', groupby=None, **kw):

        search_filters = {
            'all': {'domain': [], 'label': 'All'},
        }
        domain_user = ('create_uid', '=', request.env.user.id)

        custoemr_object = request.env['oe.new.customer']
        if not filterby:
            filterby = 'today'
        domain = search_filters.get(filterby, search_filters.get('all'))['domain']

        domain.append(domain_user)
        if search_in == 'customer_name':
            c_domain = ('customer_name', 'ilike', search)
            domain.append(c_domain)

        if 'timezone' not in request.session:
            request.session['timezone'] = 'UTC'

        customers = custoemr_object.search(domain)


        #
        values = self._prepare_tasks_values(page, date_begin, date_end, sortby, search, search_in, groupby,
                                            domain=False)
        formated_days = _formated_weekdays(get_lang(request.env).code)
        today_date = datetime.today().date()
        slots = self._get_appointment_slots(
            request.session['timezone'],
            filter_users=request.env.user,
        )
        # pager
        pager_vals = values['pager']
        pager = portal_pager(**pager_vals)
        search_input_values = {
            'customer_name': {'input': 'customer_name', 'label': _('Search by Customer Name'), 'order': 1},
        }

        search_in = request.params.get('search_in', 'customer_name')


        values.update({
            'my_customers': customers,
            'pager': pager,
            'default_url': '/my/customers',
            'searchbar_inputs': search_input_values,  # need to add here
            # 'searchbar_filters': '/my/visits',   # need to add here
            'search_in':search_in,
            'searchbar_filters': OrderedDict(sorted(search_filters.items())),
            'filterby': filterby,
            'page_name': 'Customers',
            # 'task_url': 'visits',
            'slots': slots,
            'formatted_days': formated_days,
            'today_date': today_date,
            'month_first_available': 0,  # Assuming the first month is available
            'capacity': 1,  # Assuming capacity of 1 for simplicity
            'month_kept_from_update': False,
            'timezone': request.session['timezone'],

        })
        return request.render("oe_route_planning_portal.portal_my_customers", values)

    @http.route('/new_customer/submit_form', type='http', auth='user', website=True, csrf=False)
    def new_customer_submit_form(self, update_customer=False, **post):
        data = json.loads(request.httprequest.data)
        customer_id = data.get('customer_id')
        customer_name = data.get('customer_name')
        customer_image = data.get('customer_image')
        taxid = data.get('taxid')
        city = data.get('city')
        licence = data.get('licence')
        street = data.get('street')
        street2 = data.get('street2')
        country = data.get('country')
        state = data.get('state')
        zip = data.get('zip')
        notes = data.get('notes')
        decoded_data = False
        if customer_image:
            decoded_data = base64.b64decode(customer_image)

        if not customer_image and not customer_id:
            _logger.error('customer image is missing')
            return {'success': False, 'message': 'customer image is required'}

        brand_id = False

        # Create a record in the oe_visit table
        if not customer_id:
            customer = request.env['oe.new.customer'].sudo().create({
                'customer_name': customer_name,
                'taxid': taxid,
                'licence': licence,
                'street': street,
                'street2': street2,
                'city': city,
                'country_id': int(country),
                'state_id': int(state),
                'zip': zip,
                'notes': notes,
                'photo': base64.b64encode(BytesIO(decoded_data).getvalue()).decode('utf-8'),
            })
            if customer:
                return json.dumps({'success': True, 'message': f'New customer {customer.customer_name} created'})
            else:
                return json.dumps({'success': False, 'message': 'Failed to create customer'})
        elif customer_id:
            customer = request.env['oe.new.customer'].browse(int(customer_id))
            customer.sudo().write({
                'customer_name': customer_name,
                'taxid': taxid,
                'licence': licence,
                'street': street,
                'street2': street2,
                'city': city,
                'country_id': int(country),
                'state_id': int(state),
                'zip': zip,
            })
            if decoded_data and customer_image:
                customer.sudo().write({
                    'photo': base64.b64encode(BytesIO(decoded_data).getvalue()).decode('utf-8'),
                })

            if customer:
                return json.dumps({'success': True, 'message': f'customer {customer.customer_name} Updated'})
            else:
                return json.dumps({'success': False, 'message': 'Failed to Update customer'})

        # Return JSON response indicating success or error

    @http.route('/get/customer/values', type='http', auth='user', methods=['POST'], csrf=False)
    def get_customer_values_custom(self, **post):
        data = json.loads(request.httprequest.data)
        customer_id = data.get('customer_id')
        # Fetch customer information from database
        customer = request.env['oe.new.customer'].browse(int(customer_id))
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        if customer:
            response_data = {
                'success': True,
                'customer_name': customer.customer_name,
                'customer_image_url': '/web/image/oe.new.customer/' + str(customer.id) + '/photo',
                'customer_id': str(customer.id),
                'taxid': customer.taxid,
                'licence': customer.licence,
                'street': customer.street,
                'street2': customer.street2,
                'country_id': customer.country_id.id,
                'state_id': customer.state_id.id,
                'zip': customer.zip,
                'city': customer.city,
                'notes': customer.notes,
                'countries': [{'id': country.id, 'name': country.name} for country in countries],
                'states': [{'id': state.id, 'name': state.name} for state in states]
            }
            return json.dumps(response_data)

        else:
            return json.dumps({'success': False, 'message': 'Failed to create customer'})
