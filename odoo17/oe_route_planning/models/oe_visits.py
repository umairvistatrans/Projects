# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError
from math import radians, sin, cos, acos
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta


class OEVisits(models.Model):
    _name = "oe.visits"
    _description = 'Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Visit', readonly=True)
    user_id = fields.Many2one('res.users', string="User", tracking=True)
    customer_id = fields.Many2one('res.partner', string="Customer", tracking=True)
    pasi_code = fields.Char(related='customer_id.pasi_code', tracking=True)
    route_id = fields.Many2one('oe.route.master', string='Route ID', tracking=True, required=True)
    visit_type = fields.Selection(selection=[('planned', "Planned"), ('unplanned', "Un Planned")], string="Visit Type",
                                  tracking=True)
    scheduled_date = fields.Date(string='Scheduled Date', tracking=True)
    photo_ids = fields.Many2many('ir.attachment', string='Photos')
    remarks = fields.Text(string='Remarks')
    cancelled_remarks = fields.Text(string='Cancelled Remarks', tracking=True)
    state = fields.Selection(
        selection=[('planned', "Planned"), ('in_progress', "In Progress"), ('re_scheduled', "Re-Scheduled"),
                   ('completed', "Completed"), ('cancelled', "Cancelled")], string="Status", readonly=True, copy=False,
        index=True, tracking=True, default='planned')
    visit_planning_id = fields.Many2one('oe.visit.planning',string="Visit Planning")

    # Latitude fields
    start_latitude = fields.Float(string='Start Latitude', digits=(10, 7), tracking=True)
    end_latitude = fields.Float(string='End Latitude', digits=(10, 7), tracking=True)
    start_longitude = fields.Float(string='Start longitude', digits=(10, 7), tracking=True)
    end_longitude = fields.Float(string='End longitude', digits=(10, 7), tracking=True)
    start_date_time = fields.Datetime(string="Start Date Time", tracking=True, copy=False)
    end_date_time = fields.Datetime(string="End Date Time", tracking=True, copy=False)

    # Merchandiser Related
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    customer_latitude = fields.Float(related='customer_id.partner_latitude')
    customer_longitude = fields.Float(related='customer_id.partner_longitude')
    meters = fields.Float('Meter', compute='_calculate_distance')

    comp_products_line_ids = fields.One2many("oe.visit.comp.products", 'visit_id', string="Company Products")
    comp_material_line_ids = fields.One2many("oe.visit.comp.material", 'visit_id', string="Company Materials")
    com_products_line_ids = fields.One2many("oe.visit.com.products", 'visit_id', string="Competitor Products")
    com_material_line_ids = fields.One2many("oe.visit.com.material", 'visit_id', string="Competitor Materials")


    @api.constrains('scheduled_date')
    def _check_scheduled_date(self):
        for record in self:
            if record.scheduled_date and record.scheduled_date < date.today():
                raise ValidationError("Scheduled Date cannot be in the past.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            route = self.env['oe.route.master'].browse(vals['route_id'])
            user = self.env['res.users'].browse(vals['user_id'])
            route_code = route.code or ''
            user_code = user.code or ''
            
            scheduled_date = fields.Date.from_string(vals.get('scheduled_date'))
            scheduled_month = scheduled_date.strftime('%m')
            scheduled_year = scheduled_date.strftime('%y')
            
            # Check if there are existing records for the month of the scheduled_date
            start_of_month = scheduled_date.replace(day=1)
            end_of_month = (start_of_month + relativedelta(months=1)).replace(day=1)

            # Check if there are existing records for the scheduled_date
            existing_records = self.search([('scheduled_date', '>=', start_of_month), 
                                            ('scheduled_date', '<', end_of_month)],
                                            limit=1, order='id desc')
            sequence = self.env['ir.sequence'].search([('code', '=', 'oe.visit.sequence')], limit=1)
            if not existing_records:
                if sequence:
                    sequence.write({'number_next_actual': 1})
            else:
                new_seq = int(existing_records.name[-4:])
                sequence.write({'number_next_actual': new_seq + 1 })
            sequence_code = self.env['ir.sequence'].next_by_code('oe.visit.sequence') or '/'
            vals['name'] = f'{route_code}/{scheduled_year}{scheduled_month}/{user_code}/{sequence_code}'
        return super(OEVisits, self).create(vals_list)

    def create_re_schedule_activity(self, visit):
        manager_name = visit.user_id.manager_id.name
        user_name = visit.user_id.name
        visit_name = visit.name
        note = f"Dear <b>{manager_name},</b><br/><br/><b>{user_name}</b> requested <b>{visit_name}</b> to reschedule.<br/><br/>Thanks."
        self.env['mail.activity'].create({
            'res_id': visit.id,
            'res_model_id': self.env['ir.model'].search([('model', '=', 'oe.visits')], limit=1).id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Requested for Re-Schedule',
            'user_id': visit.user_id.manager_id.id,
            'date_deadline': datetime.now().date(),
            'note': note,
        })

    def write(self, vals):
        res = super(OEVisits, self).write(vals)
        if 'state' in vals and vals['state'] == 're_scheduled':
            for visit in self:
                if visit.user_id.manager_id:
                    self.create_re_schedule_activity(visit)
        return res

    @api.model
    def add_customer_into_today_plan(self, partner_id, user_id):
        #create un-planned visit with customer & user given by portal user.
        today_date = datetime.today().date()
        visit_vals = {
            'customer_id': partner_id,
            'user_id': user_id,
            'visit_type': 'unplanned',
            'scheduled_date': today_date,
            'state': 'planned',}
        new_visit = self.create(visit_vals)
        return new_visit.id

    @api.depends('latitude', 'longitude', 'customer_latitude', 'customer_longitude')
    def _calculate_distance(self):
        dist_in_mt = self.get_distance_meter(self.latitude, self.longitude)
        self.meters = float("%.4f" % dist_in_mt)

    def get_distance_meter(self, lat1, lon1):
        slat = radians(lat1)
        slon = radians(lon1)
        elat = radians(self.customer_latitude)
        elon = radians(self.customer_longitude)

        dist = 6371.01 * acos(sin(slat) * sin(elat) + cos(slat) * cos(elat) * cos(slon - elon))
        dist_in_mt = dist * 1000
        return dist_in_mt

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_completed(self):
        self.state = 'completed'

    def action_re_schedule(self):
        self.state = 're_scheduled'

    def unlink(self):
        for rec in self:
            if rec.state not in ["cancelled"]:
                raise ValidationError(_("You can not delete Visits which is not in Cancelled state."))
        return super().unlink()

    def button_cancel(self):
        form_view = self.env.ref('oe_route_planning.cancel_remark_view_id')
        return {
            'name': "Cancel Remarks",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view.id,
            'res_model': 'oe.cancel.remark',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_rescheduled(self):
        # self.state = 'planned'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reschedule Visit',
            'res_model': 'oe.reschedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_reschedule_date': fields.Date.today(),
            },
        }