{
    'name': 'Mi Módulo',
    'version': '2.0',
    'summary': 'Descripción breve del módulo',
    'description': 'Descripción detallada del módulo',
    'author': 'David Alejandro Ramírez',
    'depends': ['base','mail','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/mi_modelo_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
