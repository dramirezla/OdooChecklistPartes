from odoo import models, fields

class MiModelo(models.Model):
    _name = 'mimodelo3'
    _description = 'Procesamiento de partes de un pdf'

    name = fields.Char(string='Nombre', required=True)
    descripcion = fields.Text(string='Descripción')
    fecha = fields.Date(string='Fecha')
