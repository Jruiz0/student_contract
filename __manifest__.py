# -*- coding: utf-8 -*-a
{
    'name': 'Student Contract Management',
    'version': '17.0.0.0.1',
    'category': 'Education',
    'summary': 'Manage student contracts, subjects, and payments',
    'description': """
        A module to handle student contracts in educational institutions.
    """,
    'author': 'Junior Ruiz [<juniorruiz2203000@gmail.com>,<https://github.com/Jruiz0>]',
    'website': 'https://github.com/jruiz0/student_contract',
    'depends': ['base','contacts', 'account', 'website'],
    'data': [
        ## Data
            'data/ir_sequencen_data.xml',
            'data/ir_cron_data.xml',
            'data/school_teacher_data.xml',
            'data/school_subject_data.xml',
            'data/school_period_data.xml',
            'data/ir_module_category_data.xml',
        ## Security
            'security/res_groups.xml',
            'security/group_control_school/ir.model.access.csv',
        ## Views
            'views/school_subject_view.xml',
            'views/res_partner_view.xml',
            'views/student_contract_view.xml',
            'views/school_period_view.xml',
            'views/dashboard_template.xml',
            # 'views/school_grade_view.xml',
            'views/menu_view.xml',
        ## Report
            # 'report/report_student_contract.xml',
        ## Wizard
            'wizard/contract_dashboard_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}