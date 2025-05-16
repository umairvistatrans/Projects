from odoo import models, fields, api
import datetime

class SyncOdooLogs(models.Model):
    _name = 'sync.ecommerce.logs'
    _rec_name = 'date'
    _order = "date desc"
    _description = "Model to store log of every record being synced"

    user_id = fields.Many2one("res.users", default=lambda self: self.env.user, required=True)
    date = fields.Datetime("Log Date",default=lambda x:datetime.date.today())
    status = fields.Selection([("success", "Success"), ("failed", "Failed")], string="Status")
    message = fields.Text("Message")
