from odoo import http
from odoo.http import request
from odoo import fields
from datetime import datetime

class ContractDashboardController(http.Controller):

    @http.route('/dashboard/<string:unique_id>', type='http', auth='public', website=True)
    def view_dashboard(self, unique_id, **kwargs):
        print("unique_id")
        print(unique_id)
        dashboard = request.env['contract.dashboard'].sudo().search(
            [('unique_url', '=', f"/dashboard/{unique_id}"), ('active', '=', True)], limit=1
        )
        print("dashboard")
        print(dashboard)
        if not dashboard:
            return request.render("student_contract.contract_dashboard_not_found")
        if dashboard.expiration_type == 'on_access' :

            if dashboard.view_count >= 1:
                dashboard.unlink()
                return request.render("student_contract.contract_dashboard_not_found")
            dashboard.view_count += 1
            
        if dashboard.expiration_type == 'time_based':
            if dashboard.expiration_date < datetime.now():
                dashboard.unlink() 
                return request.render("student_contract.contract_dashboard_not_found")
        if not dashboard:
            return request.render("student_contract.contract_dashboard_not_found")
        contracts = request.env['student.contract'].sudo().search([])
        return request.render('student_contract.contract_dashboard_template', {
            'contracts': contracts,
        })