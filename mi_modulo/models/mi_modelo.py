from odoo import models, fields, api

class MiModelo(models.Model):
    _name = 'mimodelo'
    _description = 'Descripción de mi modelo'

    name = fields.Char(string='Nombre', required=True)
    descripcion = fields.Text(string='Descripción')
    fecha = fields.Date(string='Fecha')
