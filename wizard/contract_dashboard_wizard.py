from odoo import models, fields, api
from datetime import datetime, timedelta
import uuid

class ContractDashboardWizard(models.TransientModel):
    _name = 'contract.dashboard.wizard'
    _description = 'Wizard to Generate Dashboard Links'

    expiration_type = fields.Selection([
        ('on_access', 'Expire on Access'),
        ('time_based', 'Expire After a Period'),
    ], string="Expiration Type", required=True, default='time_based')

    expiration_hours = fields.Integer(
        string="Expiration Period (in Hours)",
        default=24,
        help="Specify the expiration period if 'Expire After a Period' is selected."
    )

    student_contract_id = fields.Many2one('student.contract', string="Student Contract")

    def generate_link(self):
        dashboard_model = self.env['contract.dashboard']
        expiration_hours = self.expiration_hours if self.expiration_type == 'time_based' else 0
        new_dashboard = dashboard_model.create_dashboard_entry(
            expiration_type=self.expiration_type,
            expiration_hours=expiration_hours,
        )
        self.student_contract_id.dashboard_id = new_dashboard
        return 