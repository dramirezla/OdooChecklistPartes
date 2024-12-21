{
    'name': 'Mi Módulo',
    'version': '1.0',
    'summary': 'Descripción breve del módulo',
    'description': 'Descripción detallada del módulo',
    'author': 'David Alejandro Ramírez',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/mi_modelo_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
