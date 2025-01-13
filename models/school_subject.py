from odoo import fields, models, api, _ , Command

    
class Subject(models.Model):
    _name = 'school.subject'
    _description = 'Subjects'

    name = fields.Char(string="Subject", required=True)

    teacher_ids = fields.Many2many('res.partner', string="Teachers",
        domain=[('is_teacher', '=', True)])

