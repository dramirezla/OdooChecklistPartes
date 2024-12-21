from odoo import models, fields, api

class MiModelo(models.Model):
    _name = 'mi.modelo'
    _description = 'Descripción de mi modelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre')
