from odoo import models, fields, api
from PyPDF2 import PdfReader
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
    procesado = fields.Boolean(string='Procesado')
    raise UserError("hola mundo")

    def procesar_pdf(self):
        """
        Procesa el archivo PDF, extrae texto y genera registros de partes encontradas.
        """
        self.ensure_one()
        if not self.archivo_pdf:
            raise ValueError("Debe adjuntar un archivo PDF para procesar.")

        pdf_bytes = io.BytesIO(self.archivo_pdf.decode('base64'))
        reader = PdfReader(pdf_bytes)
        frecuencia = Counter()
        partes = []

        for page_num, page in enumerate(reader.pages):
            texto = page.extract_text() or ""
            partes_pagina = re.findall(r'Kerf: [A-Z]', texto)
            partes += [(letra[-1], page_num + 1) for letra in partes_pagina]
            frecuencia.update([letra[-1] for letra in partes_pagina])

        # Guardar frecuencia en formato de texto
        self.frecuencia_partes = "\n".join([f"{letra}: {freq}" for letra, freq in frecuencia.items()])

        # Crear registros de partes encontradas
        self.parte_ids.unlink()
        for letra, layout in partes:
            self.env['procesamiento.pdf.parte'].create({
                'pdf_id': self.id,
                'letra': letra,
                'layout': layout
            })

        self.procesado = True

    def procesar_partes_seleccionadas(self):
        """
        Procesa las partes seleccionadas y muestra un mensaje con la frecuencia.
        """
        seleccionadas = self.parte_ids.filtered(lambda p: p.seleccionada)
        frecuencia = Counter(p.letra for p in seleccionadas)
        mensaje = "\n".join([f"{letra}: {freq}" for letra, freq in frecuencia.items()])

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Frecuencia de Partes Seleccionadas',
                'message': mensaje,
                'type': 'info',
                'sticky': False,
            }
        }


class ProcesamientoPDFParte(models.Model):
    _name = 'procesamiento.pdf.parte'
    _description = 'Partes encontradas en el PDF'

    pdf_id = fields.Many2one('procesamiento.pdf', string='PDF Asociado')
    letra = fields.Char(string='Letra Encontrada')
    layout = fields.Integer(string='Número de Página')
    seleccionada = fields.Boolean(string='Seleccionada')
