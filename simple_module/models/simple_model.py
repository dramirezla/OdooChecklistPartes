
from odoo import models, fields

class SimpleModel(models.Model):
    _name = "simple.model"
    _description = "Simple Model"

    name = fields.Char(string="Name", required=True)
