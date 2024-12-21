{
    'name': 'Mi Módulo',
    'version': '1.0',
    'summary': 'Descripción breve del módulo',
    'description': 'Modulo para la descripcion y seleccion de partes de un documento pdf',
    'author': 'David Alejandro Ramírez',
    'category': 'Custom',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/mi_modelo_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
