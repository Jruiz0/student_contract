from odoo import fields, models, api, _ , Command



class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_student = fields.Boolean(string="Is a Student")
    
    is_teacher = fields.Boolean(string="Is a Teacher")

    subject_ids = fields.Many2many('school.subject', string="Subjects")
