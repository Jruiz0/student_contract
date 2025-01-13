from odoo import fields, models, api, _ , Command
from odoo.exceptions import ValidationError

class SchoolPeriod(models.Model):
    _name = 'school.period'

    name = fields.Char(string="Name", required=True)

    start_date = fields.Date(string="Start Date", required=True)

    end_date = fields.Date(string="End Date", required=True)

    state = fields.Selection([('draft', 'Draft'), ('active', 'Active')],
        string="State", default='draft')

    def action_active(self):
        self.write({'state': 'active'})
    
    def action_draft(self):
        self.write({'state': 'draft'})

        
class SchoolGrade(models.Model):
    _name = 'school.grade'
    
    name = fields.Char(string="Grade", required=True)
    
    active = fields.Boolean(string="Active", default=True)

    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if self.search[('name', '=', record.name), ('id', '!=', record.id)]:
                raise ValidationError(_('The name must be unique!'))
            
    