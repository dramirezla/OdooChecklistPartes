{
    'name': 'Custom Module',
    'version': '1.0',
    'summary': 'A simple custom Odoo module',
    'description': 'This is a basic custom module example for Odoo.sh integration.',
    'author': 'Your Name',
    'category': 'Custom',
    'depends': ['base'],
    'data': [
        'views/custom_model_views.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}