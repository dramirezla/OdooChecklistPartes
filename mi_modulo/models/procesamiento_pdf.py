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
        self.ensure_one()
        if not self.archivo_pdf:
            raise UserError("Debe adjuntar un archivo PDF para procesar.")
    
        if self.procesado:
            raise UserError("El PDF ya ha sido procesado.")
    
        pdf_bytes = io.BytesIO(base64.b64decode(self.archivo_pdf))
        reader = PdfReader(pdf_bytes)
        frecuencia = Counter()
        partes = []
    
        for page_num, page in enumerate(reader.pages):
            texto = page.extract_text() or ""
    
            if page_num == 0:  # Procesar solo la página 0 para este caso
                partes_pagina = re.findall(
                    r'([A-Z]{1,2})\s+(\d+)\s+([\d,]+)cm\s+([\d,]+)cm',
                    texto
                )
                for letra, copias, base, altura in partes_pagina:
                    base = float(base.replace(',', '.'))  # Convertir base a float
                    altura = float(altura.replace(',', '.'))  # Convertir altura a float
                    partes.append((letra, page_num + 1, base, altura))
                    frecuencia[letra] += int(copias)
    
        # Actualizar las partes en la base de datos
        self.frecuencia_partes = "\n".join([f"{letra}: {freq}" for letra, freq in sorted(frecuencia.items())])
        self.parte_ids.unlink()
        for letra, layout, base, altura in partes:
            self.env['procesamiento.pdf.parte'].create({
                'pdf_id': self.id,
                'letra': letra,
                'layout': layout,
                'base_parte': base,
                'altura_parte': altura,
            })
    
        self.procesado = True

    
        # Método para procesar partes seleccionadas
    def obtener_partes_seleccionadas(self):
        self.ensure_one()
        partes_seleccionadas = self.parte_ids.filtered(lambda p: p.seleccionada)
        if not partes_seleccionadas:
            raise UserError("No hay partes seleccionadas.")

        frecuencia = Counter([parte.letra for parte in partes_seleccionadas])
        resultado = [{"parte": letra, "frecuencia": freq} for letra, freq in frecuencia.items()]
        return resultado

    # Método para mostrar resultado en la interfaz de usuario
    def mostrar_partes_seleccionadas(self):
        self.ensure_one()
        resultado = self.obtener_partes_seleccionadas()
        mensaje = "\n".join([f"Parte: {item['parte']}, Frecuencia: {item['frecuencia']}" for item in resultado])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partes Seleccionadas',
            'view_mode': 'form',
            'res_model': 'procesamiento.pdf',
            'target': 'new',
            'context': {'default_name': f"Resultado - {self.name}", 'default_frecuencia_partes': mensaje},
        }


class ProcesamientoPDFParte(models.Model):
    _name = 'procesamiento.pdf.parte'
    _description = 'Partes encontradas en el PDF'

    pdf_id = fields.Many2one('procesamiento.pdf', string='PDF Asociado')
    letra = fields.Char(string='Parte')
    layout = fields.Integer(string='Layout')
    seleccionada = fields.Boolean(string='CheckBox')
    base_parte = fields.Float(string='Base (cm)')
    altura_parte = fields.Float(string='Altura (cm)')
