from odoo import fields, models, api, _ , Command
from odoo.exceptions import UserError, ValidationError
import uuid
from datetime import timedelta, datetime


class StudentContract(models.Model):
    _name = 'student.contract'
    _description = 'Student Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'
    
    code = fields.Char(string="Code", required=True, copy=False, default="NEW")

    student_id = fields.Many2one('res.partner', string="Student", 
        domain=[('is_student', '=', True)], required=True)

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),('paid', 'Paid'), ('canceled', 'Canceled')], string="State", default='draft')
    
    line_ids = fields.One2many('student.contract.line', 'contract_id', string="Contract Lines")
    
    total_amount = fields.Float(string="Total Amount", compute="_compute_total")

    period_id = fields.Many2one('school.period', string="Period", required=True,
         domain="[('state', '=', 'active')]")

    date_end = fields.Date(string="End Date", related='period_id.end_date', store=True)

    date_start = fields.Date(string="Start Date", related='period_id.start_date', store=True)

    payment_id = fields.Many2one('account.payment', string="Payment")
    
    payment_state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string="Payment State", default='draft')
 
    selected_subject_ids = fields.Many2many('school.subject', compute="_compute_selected_subjects",string="Selected Subjects")
    
    dashboard_id = fields.Many2one('contract.dashboard', string="Dashboard")

    url = fields.Char(string="Unique URL", readonly=True, related='dashboard_id.url')

    expiration_date = fields.Datetime(string="Expiration Date", readonly=True, related='dashboard_id.expiration_date')

    payment_ids = fields.One2many('account.payment', 'contract_id', string="Payments")

    payment_count = fields.Integer(string="Payment Count", compute="_compute_payment_count", store=True)

    amount_paid = fields.Float(string="Amount Paid", compute="_compute_amount_paid", store=True)

    balance_due = fields.Float(string="Balance Due", compute="_compute_balance_due", store=True)

    journal_id = fields.Many2one('account.journal',string="Payment Journal", required=True,
        domain="[('type', 'in', ['bank', 'cash'])]")

    def action_generate_dashboard(self):
        return {
            'name': _('Generate Dashboard Link'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.dashboard.wizard',
            'target': 'new',
            'context': {
                'default_expiration_type': 'on_access',
                'default_student_contract_id':  self.id,
            },
        }

    @api.model
    def create(self, values):
        result = super().create(values)
        
        return result
    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)
            
    @api.depends('payment_ids.amount', 'payment_ids.state')
    def _compute_amount_paid(self):
        for record in self:
            record.amount_paid = sum(payment.amount for payment in record.payment_ids if payment.state == 'posted')

    @api.depends('total_amount', 'amount_paid')
    def _compute_balance_due(self):
        for record in self:
            record.balance_due = record.total_amount - record.amount_paid

    def action_view_payments(self):
        return {
            'name': _('Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'target': 'current',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.payment_ids.ids)],
        }
    def register_payment(self, amount):
        payment_obj = self.env['account.payment']
        for record in self:
            payment = payment_obj.create({
                'partner_id': record.student_id.id,
                'amount': amount,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'journal_id': record.journal_id.id,
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                'ref': f"Payment for Contract #{record.id}",
                'contract_id': record.id,
            })
            payment.action_post()
            return payment

    @api.depends('line_ids.subject_id')
    def _compute_selected_subjects(self):
        for record in self:
            record.selected_subject_ids = record.line_ids.mapped('subject_id')

    @api.onchange('student_id')
    def onchange_student_id(self):
        if self.line_ids:
            self.line_ids.unlink()
    
    @api.depends('line_ids.price')
    def _compute_total(self):
        for record in self:
            record.total_amount = sum(line.price for line in record.line_ids)
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        
    def action_cancel(self):
        self.write({'state': 'canceled'})   

    def action_draft(self):
        self.write({'state': 'draft'})
    
    
    @api.constrains('student_id', 'period_id', 'state')
    def _check_diplucate(self):
        for record in self:
            if record.student_id and record.period_id and record.state:
                if self.search([
                        ('student_id', '=', record.student_id.id), 
                        ('period_id', '=', record.period_id.id), 
                        ('id', '!=', record.id),
                        ('state', 'not in', ['paid', 'canceled'])
                    ]):
                    raise ValidationError(_('The contract for this student and period already exists and is still active.'))
            
    def register_payment_action(self):
        for record in self:
            if record.balance_due <= 0:
                raise UserError("The contract is already fully paid.")
            payment = record.register_payment(record.balance_due)
            record.message_post(body=f"Payment of {payment.amount} registered for the contract.")
            return {
                'name': _('Payment'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'target': 'new',
                'res_id': payment.id,
            }

class StudentContractLine(models.Model):
    _name = 'student.contract.line'
    _description = 'Contract Line'

    contract_id = fields.Many2one('student.contract', string="Contract")

    selected_subject_ids = fields.Many2many('school.subject', related='contract_id.selected_subject_ids', string="Selected Subjects")

    student_id = fields.Many2one('res.partner', string="Student", related='contract_id.student_id')
     
    subject_ids = fields.Many2many('school.subject', string="Subjects", related='student_id.subject_ids')

    period_id = fields.Many2one('school.period', string="Period", related='contract_id.period_id')
    
    subject_id = fields.Many2one('school.subject', string="Subject", required=True,
        domain="[('id', 'in', subject_ids), ('id', 'not in', selected_subject_ids)]"
    )

    teacher_ids = fields.Many2many('res.partner', string="Teachers", related='subject_id.teacher_ids')

    teacher_id = fields.Many2one('res.partner', string="Teacher", required=True,
        domain="[('id', 'in', teacher_ids)]")

    price = fields.Float(string="Price", required=True)

    
class ContractDashboard(models.Model):
    _name = 'contract.dashboard'
    _description = 'Contract Dashboard'

    unique_url = fields.Char(string="Unique URL", readonly=True, copy=False)
    
    expiration_date = fields.Datetime(string="Expiration Date", required=True)
    url = fields.Char(string="URL", readonly=True, copy=False)
    active = fields.Boolean(string="Active", default=True)

    expiration_type = fields.Selection([
        ('on_access', 'Expire on Access'),
        ('time_based', 'Expire After a Period'),
    ], string="Expiration Type", default='time_based')

    view_count = fields.Integer(string="View Count", default=0, readonly=True)

    @api.model
    def create_unique_url(self):
        return f"/dashboard/{uuid.uuid4()}"

    @api.model
    def create_dashboard_entry(self, expiration_type='time_based', expiration_hours=24):
        expiration = (
            datetime.now() + timedelta(hours=expiration_hours)
            if expiration_type == 'time_based'
            else datetime.now()
        )
        url = self.create_unique_url()
        return self.create({
            'unique_url': url,
            'url': self.env['ir.config_parameter'].get_param('web.base.url') + url,
            'expiration_date': expiration,
            'expiration_type': expiration_type,
        })


    @api.model
    def delete_expired_links(self):
        expired_links = self.search([('expiration_date', '<', datetime.now()), ('active', '=', True)])
        for link in expired_links:
            link.active = False
        expired_links.unlink() 

    def increment_view_count(self):
        for record in self:
            if record.expiration_type == 'on_access' and record.view_count >= 1:
                record.unlink() 
                return
            if record:
                record.view_count += 1

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    contract_id = fields.Many2one('student.contract', string="Related Contract")