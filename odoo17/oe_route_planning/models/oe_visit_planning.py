# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import math
from odoo.exceptions import ValidationError
import calendar
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.calendar.models.calendar_recurrence import (
    weekday_to_field,
    RRULE_TYPE_SELECTION,
    END_TYPE_SELECTION,
    MONTH_BY_SELECTION,
    WEEKDAY_SELECTION,
)


class OEVisitPlanning(models.Model):
    _name = "oe.visit.planning"
    _description = 'Visit Planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Name', readonly=True)
    user_id = fields.Many2one('res.users', string="User", tracking=True, required=True, default=lambda self: self.env.user)
    customer_ids = fields.Many2many('res.partner', string="Customers", tracking=True, required=True,)
    route_id = fields.Many2one('oe.route.master', string='Route ID', tracking=True, required=True)
    rrule_type_ui = fields.Selection([
                            ('daily', 'Daily'),
                            ('weekly', 'Weekly'),
                            ('monthly', 'Monthly'),
                            ('yearly', 'Yearly'),
                            ('custom', 'Custom')
                        ], string='Recurrence Type', default='daily', required=True)
    interval = fields.Integer(string='Repeat every', default=1)
    rrule_type = fields.Selection([
                            ('daily', 'Daily'),
                            ('weekly', 'Weekly'),
                            ('monthly', 'Monthly'),
                            ('yearly', 'Yearly')
                        ], string='Rule Type')
    end_type = fields.Selection([
                        ('count', 'Number of repetitions'),
                        ('end_date', 'End Date'),
                    ], default="count", string='Until')
    count = fields.Integer(string='Number of Repetitions', help="Repeat x times", readonly=False)
    until = fields.Date(readonly=False)
    month_by = fields.Selection(MONTH_BY_SELECTION, string='Option', readonly=False)
    day = fields.Integer('Date of month', readonly=False)
    weekday = fields.Selection([
                    ('MO', 'Monday'),
                    ('TU', 'Tuesday'),
                    ('WED', 'Wednesday'),
                    ('TH', 'Thursday'),
                    ('FR', 'Friday'),
                    ('SA', 'Saturday'),
                    ('SU', 'Sunday')
                ], string='Weekday')
    byday = fields.Selection([
            ('1', 'First'),
            ('2', 'Second'),
            ('3', 'Third'),
            ('4', 'Fourth')
        ], string="By day", readonly=False)
    recurrency = fields.Boolean('Recurrent',default=True)
    start_date = fields.Date('Start Date', store=True, tracking=True)
    stop_date = fields.Date('End Date', store=True, tracking=True)
    remarks = fields.Text(string='Remarks')
    allday = fields.Boolean('All Day', default=False)
    mon = fields.Boolean(readonly=False)
    tue = fields.Boolean(readonly=False)
    wed = fields.Boolean(readonly=False)
    thu = fields.Boolean(readonly=False)
    fri = fields.Boolean(readonly=False)
    sat = fields.Boolean(readonly=False)
    sun = fields.Boolean(readonly=False)
    rrule = fields.Char('Recurrent Rule', readonly=False)
    state = fields.Selection(
        selection=[('draft', "Draft"), ('confirmed', "Confirmed")
        ], string="Status", readonly=True, copy=False, index=True, tracking=True, default='draft')
    visit_count = fields.Integer(string='Visits', compute='_compute_visit_count', default=0)


    @api.constrains('until', 'end_type', 'count')
    def _check_until_date(self):
        for record in self:
            if record.until and self.end_type == 'end_date' and record.until < date.today():
                raise ValidationError("The 'Until' date cannot be in the past.")
            if record.end_type == 'count' and record.count <= 0:
                raise ValidationError("The number of repetitions must be greater than 0.")

    @api.constrains('month_by', 'day')
    def _check_day(self):
        for record in self:
            if record.month_by == 'date' and (record.day <= 0 or record.day > 31):
                raise ValidationError(_("Day must be greater than 0 and less than or equal to 31."))

    @api.constrains('start_date', 'until', 'end_type')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.until and self.end_type == 'end_date' and record.start_date > record.until:
                raise ValidationError(_("Start Date must be before End Date."))
            if record.start_date and record.start_date < fields.Date.today():
                raise ValidationError(_("Start Date cannot be in the past."))

    def _compute_visit_count(self):
        for record in self:
            record.visit_count = self.env['oe.visits'].search_count([('visit_planning_id', '=', self.id)])

    def action_view_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'view_mode': 'tree,form',
            'res_model': 'oe.visits',
            'domain': [('visit_planning_id', '=', self.id)],
            'context': dict(self._context, create=False)
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('oe.visit.planning.sequence') or '/'
        return super(OEVisitPlanning, self).create(vals_list)

    def create_recurrences(self):
        recurrences = []
        # If Recurrence Type is Daily
        if self.rrule_type_ui == 'daily':
            if self.end_type == 'count':
                for i in range(self.count):
                    visit_date = self.start_date + timedelta(days=i * self.interval)
                    for customer in self.customer_ids:
                        recurrences.append(self._create_visit(visit_date, customer.id))
            elif self.end_type == 'end_date':
                next_date = self.start_date
                while next_date <= self.until:
                    for customer in self.customer_ids:
                        recurrences.append(self._create_visit(next_date, customer.id))
                    next_date += timedelta(days=self.interval)
        
        # If Recurrence Type is Weekly
        elif self.rrule_type_ui == 'weekly':
            if self.end_type == 'count':
                current_count = 0
                next_date = self.start_date
                while current_count < self.count:
                    if ((self.mon and next_date.weekday() == 0) or
                        (self.tue and next_date.weekday() == 1) or
                        (self.wed and next_date.weekday() == 2) or
                        (self.thu and next_date.weekday() == 3) or
                        (self.fri and next_date.weekday() == 4) or
                        (self.sat and next_date.weekday() == 5) or
                        (self.sun and next_date.weekday() == 6)):
                        for customer in self.customer_ids:
                            recurrences.append(self._create_visit(next_date, customer.id))
                        current_count += 1
                    next_date += timedelta(days=self.interval)
            elif self.end_type == 'end_date':
                next_date = self.start_date
                while next_date <= self.until:
                    if ((self.mon and next_date.weekday() == 0) or
                        (self.tue and next_date.weekday() == 1) or
                        (self.wed and next_date.weekday() == 2) or
                        (self.thu and next_date.weekday() == 3) or
                        (self.fri and next_date.weekday() == 4) or
                        (self.sat and next_date.weekday() == 5) or
                        (self.sun and next_date.weekday() == 6)):
                        for customer in self.customer_ids:
                            recurrences.append(self._create_visit(next_date, customer.id))
                    next_date += timedelta(days=self.interval)

        # If Recurrence Type is Monthly
        if self.rrule_type_ui == 'monthly':
            if self.month_by == 'date':
                try:
                    day_of_month = int(self.day)
                    next_date = self.start_date.replace(day=day_of_month)
                    if self.end_type == 'count':
                        for i in range(self.count):
                            if isinstance(self.until, (date, datetime)) and next_date > self.until:
                                break
                            for customer in self.customer_ids:
                                recurrences.append(self._create_visit(next_date, customer.id))
                            next_date = next_date + relativedelta(months=self.interval)
                    elif self.end_type == 'end_date':
                        while isinstance(self.until, (date, datetime)) and next_date <= self.until:
                            for customer in self.customer_ids:
                                recurrences.append(self._create_visit(next_date, customer.id))
                            next_date = next_date + relativedelta(months=self.interval)
                except ValueError:
                    raise TypeError('Day must be an integer representing the day of the month')

            elif self.month_by == 'day':
                week_index = int(self.byday)
                weekday_abbr_to_full = {
                    'MO': 'monday',
                    'TU': 'tuesday',
                    'WED': 'wednesday',
                    'TH': 'thursday',
                    'FR': 'friday',
                    'SA': 'saturday',
                    'SU': 'sunday'}
                uppercase_weekday = self.weekday.upper()
                if uppercase_weekday in weekday_abbr_to_full:
                    lowercase_weekday = weekday_abbr_to_full[uppercase_weekday]
                    weekday_name_to_num = {name.lower(): num for num, name in enumerate(calendar.day_name)}
                    if lowercase_weekday in weekday_name_to_num:
                        target_weekday_num = weekday_name_to_num[lowercase_weekday]
                        current_start_date = self.start_date
                        for i in range(self.count):
                            month_start = current_start_date.replace(day=1)
                            first_day_of_week = (target_weekday_num - month_start.weekday() + 7) % 7
                            target_day = month_start + timedelta(days=first_day_of_week + (week_index - 1) * 7)
                            if target_day.month != month_start.month:
                                target_day -= timedelta(weeks=1)
                            if self.end_type == 'count':
                                if target_day and target_day.month == month_start.month:
                                    for customer in self.customer_ids:
                                        recurrences.append(self._create_visit(target_day, customer.id))
                            elif self.end_type == 'end_date':
                                if target_day <= self.until and target_day.month == month_start.month:
                                    for customer in self.customer_ids:
                                        recurrences.append(self._create_visit(target_day, customer.id))
                            current_start_date = current_start_date + relativedelta(months=self.interval)

        # If Recurrence Type is Yearly
        elif self.rrule_type_ui == 'yearly':
            if self.end_type == 'count':
                for i in range(self.count):
                    visit_date = self.start_date + relativedelta(years=i * self.interval)
                    for customer in self.customer_ids:
                        recurrences.append(self._create_visit(visit_date, customer.id))
            elif self.end_type == 'end_date':
                next_date = self.start_date
                while next_date <= self.until:
                    for customer in self.customer_ids:
                        recurrences.append(self._create_visit(next_date, customer.id))
                    next_date += relativedelta(years=self.interval)

        # If Recurrence Type is Custom
        elif self.rrule_type_ui == 'custom':
            if self.rrule_type == 'daily':
                if self.end_type == 'count':
                    for i in range(self.count):
                        visit_date = self.start_date + timedelta(days=i * self.interval)
                        for customer in self.customer_ids:
                            recurrences.append(self._create_visit(visit_date, customer.id))
                elif self.end_type == 'end_date':
                    next_date = self.start_date
                    while next_date <= self.until:
                        for customer in self.customer_ids:
                            recurrences.append(self._create_visit(next_date, customer.id))
                        next_date += timedelta(days=self.interval)

            elif self.rrule_type == 'weekly':
                if self.end_type == 'count':
                    current_count = 0
                    next_date = self.start_date
                    while current_count < self.count:
                        if ((self.mon and next_date.weekday() == 0) or
                            (self.tue and next_date.weekday() == 1) or
                            (self.wed and next_date.weekday() == 2) or
                            (self.thu and next_date.weekday() == 3) or
                            (self.fri and next_date.weekday() == 4) or
                            (self.sat and next_date.weekday() == 5) or
                            (self.sun and next_date.weekday() == 6)):
                            for customer in self.customer_ids:
                                recurrences.append(self._create_visit(next_date, customer.id))
                            current_count += 1
                        next_date += timedelta(days=self.interval)
                elif self.end_type == 'end_date':
                    next_date = self.start_date
                    while next_date <= self.until:
                        if ((self.mon and next_date.weekday() == 0) or
                            (self.tue and next_date.weekday() == 1) or
                            (self.wed and next_date.weekday() == 2) or
                            (self.thu and next_date.weekday() == 3) or
                            (self.fri and next_date.weekday() == 4) or
                            (self.sat and next_date.weekday() == 5) or
                            (self.sun and next_date.weekday() == 6)):
                            for customer in self.customer_ids:
                                recurrences.append(self._create_visit(next_date, customer.id))
                        next_date += timedelta(days=self.interval)

            elif self.rrule_type == 'monthly':
                if self.month_by == 'date':
                    try:
                        day_of_month = int(self.day)
                        next_date = self.start_date.replace(day=day_of_month)
                        if self.end_type == 'count':
                            for i in range(self.count):
                                if isinstance(self.until, (date, datetime)) and next_date > self.until:
                                    break
                                for customer in self.customer_ids:
                                    recurrences.append(self._create_visit(next_date, customer.id))
                                next_date = next_date + relativedelta(months=self.interval)
                        elif self.end_type == 'end_date':
                            while isinstance(self.until, (date, datetime)) and next_date <= self.until:
                                for customer in self.customer_ids:
                                    recurrences.append(self._create_visit(next_date, customer.id))
                                next_date = next_date + relativedelta(months=self.interval)
                    except ValueError:
                        raise TypeError('Day must be an integer representing the day of the month')

                elif self.month_by == 'day':
                    week_index = int(self.byday)
                    weekday_abbr_to_full = {
                        'MO': 'monday',
                        'TU': 'tuesday',
                        'WED': 'wednesday',
                        'TH': 'thursday',
                        'FR': 'friday',
                        'SA': 'saturday',
                        'SU': 'sunday'}
                    uppercase_weekday = self.weekday.upper()
                    if uppercase_weekday in weekday_abbr_to_full:
                        lowercase_weekday = weekday_abbr_to_full[uppercase_weekday]
                        weekday_name_to_num = {name.lower(): num for num, name in enumerate(calendar.day_name)}
                        if lowercase_weekday in weekday_name_to_num:
                            target_weekday_num = weekday_name_to_num[lowercase_weekday]
                            current_start_date = self.start_date
                            for i in range(self.count):
                                month_start = current_start_date.replace(day=1)
                                first_day_of_week = (target_weekday_num - month_start.weekday() + 7) % 7
                                target_day = month_start + timedelta(days=first_day_of_week + (week_index - 1) * 7)
                                if target_day.month != month_start.month:
                                    target_day -= timedelta(weeks=1)
                                if self.end_type == 'count':
                                    if target_day and target_day.month == month_start.month:
                                        for customer in self.customer_ids:
                                            recurrences.append(self._create_visit(target_day, customer.id))
                                elif self.end_type == 'end_date':
                                    if target_day <= self.until and target_day.month == month_start.month:
                                        for customer in self.customer_ids:
                                            recurrences.append(self._create_visit(target_day, customer.id))
                                current_start_date = current_start_date + relativedelta(months=self.interval)

            elif self.rrule_type == 'yearly':
                if self.end_type == 'count':
                    for i in range(self.count):
                        visit_date = self.start_date + relativedelta(years=i * self.interval)
                        for customer in self.customer_ids:
                            recurrences.append(self._create_visit(visit_date, customer.id))
                elif self.end_type == 'end_date':
                    next_date = self.start_date
                    while next_date <= self.until:
                        for customer in self.customer_ids:
                            recurrences.append(self._create_visit(next_date, customer.id))
                        next_date += relativedelta(years=self.interval)

        return recurrences

    def action_confirm(self):
        self.create_recurrences()
        self.state = 'confirmed'

    def _create_visit(self, visit_date, customer_id):
        return self.env['oe.visits'].create({
            'user_id': self.user_id.id,
            'scheduled_date': visit_date,
            'route_id': self.route_id.id,
            'customer_id': customer_id,
            'visit_planning_id': self.id,
            'visit_type': 'planned',
            'state': 'planned'
        })

    def unlink(self):
        for rec in self:
            if rec.state not in ("draft"):
                raise ValidationError(
                    _(
                        "You can not delete Planning which is not in Draft state."
                    )
                )
        return super().unlink()
