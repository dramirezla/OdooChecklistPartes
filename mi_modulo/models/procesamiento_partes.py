

class ProcesamientoPDFParte(models.Model):
    _name = 'procesamiento.pdf.parte'
    _description = 'Partes encontradas en el PDF'

    pdf_id = fields.Many2one('procesamiento.pdf', string='PDF Asociado')
    letra = fields.Char(string='Letra Encontrada')
    layout = fields.Integer(string='Número de Página')
    seleccionada = fields.Boolean(string='Seleccionada')