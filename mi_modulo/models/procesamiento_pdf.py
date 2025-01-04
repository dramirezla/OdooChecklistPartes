from odoo import models, fields, api
from odoo.exceptions import UserError
from PyPDF2 import PdfReader
import base64
import io
import re
from collections import Counter

class ProcesamientoPDF(models.Model):
    _name = 'procesamiento.pdf'
    _description = 'Procesamiento de PDF'

    name = fields.Char(string='Nombre', required=True)
    archivo_pdf = fields.Binary(string='Archivo PDF', required=True, attachment=True)
    frecuencia_partes = fields.Text(string='Frecuencia de Partes', readonly=True)
    parte_ids = fields.One2many('procesamiento.pdf.parte', 'pdf_id', string='Partes Encontradas')
    procesado = fields.Boolean(string='Procesado', default=False)


    for rec in parte_ids:
	raise UserError(rec.letra)
        
    @api.model
    def create(self, vals):
        """
        Sobrescribe el método create para procesar automáticamente el PDF al crear un registro.
        """
        record = super(ProcesamientoPDF, self).create(vals)
        if vals.get('archivo_pdf'):
            record.procesar_pdf()
        return record

    def write(self, vals):
        """
        Sobrescribe el método write para procesar automáticamente el PDF si se actualiza el archivo.
        """
        res = super(ProcesamientoPDF, self).write(vals)
        if 'archivo_pdf' in vals:
            self.procesar_pdf()
        return res

    def procesar_pdf(self):
        """
        Procesa el archivo PDF, extrae texto y genera registros de partes encontradas.
        """
        self.ensure_one()
        if not self.archivo_pdf:
            raise UserError("Debe adjuntar un archivo PDF para procesar.")
        
        if self.procesado:
            raise UserError("El PDF ya ha sido procesado.")

        pdf_bytes = io.BytesIO(base64.b64decode(self.archivo_pdf))
        reader = PdfReader(pdf_bytes)
        frecuencia = Counter()
        partes = []
        contenido_paginas = []

        for page_num, page in enumerate(reader.pages):
            texto = page.extract_text() or ""
            partes_pagina_dividida = texto.split("Kerf: ", 1)  # Dividir en dos partes; antes y después de "Kerf"
            contenido_modificado = partes_pagina_dividida[1] if len(partes_pagina_dividida) > 1 else "" 
            partes_pagina = re.findall(r'[A-Z]', contenido_modificado)
            partes += [(letra[-1], page_num + 1) for letra in partes_pagina]
            frecuencia.update([letra[-1] for letra in partes_pagina])

  
        self.frecuencia_partes = "\n".join([f"{letra}: {freq}" for letra, freq in frecuencia.items()])
        
        
        self.parte_ids.unlink()
        for letra, layout in partes:
            self.env['procesamiento.pdf.parte'].create({
                'pdf_id': self.id,
                'letra': letra,
                'layout': layout - 1
            })

        self.procesado = True


class ProcesamientoPDFParte(models.Model):
    _name = 'procesamiento.pdf.parte'
    _description = 'Partes encontradas en el PDF'

    pdf_id = fields.Many2one('procesamiento.pdf', string='PDF Asociado')
    letra = fields.Char(string='Letra Encontrada')
    layout = fields.Integer(string='Número de Página')
    seleccionada = fields.Boolean(string='Seleccionada')
