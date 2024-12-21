from odoo import models, fields

class MiModelo(models.Model):
    _name = 'mi_modelo'
    _description = 'Descripción de mi modelo'

    name = fields.Char(string='Nombre', required=True)
    descripcion = fields.Text(string='Descripción')
    fecha = fields.Date(string='Fecha')
