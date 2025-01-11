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
        """
        Procesa el archivo PDF, extrae texto, genera registros de partes encontradas y calcula dimensiones asociadas.
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
    
        for page_num, page in enumerate(reader.pages):
            texto = page.extract_text() or ""
            partes_pagina_dividida = texto.split("Kerf: ", 1)  # Dividir en dos partes; antes y después de "Kerf"
            contenido_modificado = partes_pagina_dividida[1] if len(partes_pagina_dividida) > 1 else ""
    
            # Buscar las partes identificadas (letras mayúsculas seguidas de ":") y sus dimensiones
            matches = re.findall(r'([A-Z]):.*?(\d{1,3},\dcm)\s*x\s*(\d{1,3},\dcm)', contenido_modificado)
    
            # Procesar las partes encontradas
            for match in matches:
                letra, altura, base = match
                partes.append((letra, page_num + 1, altura, base))
                frecuencia[letra] += 1
    
        # Generar la tabla de frecuencias con las dimensiones
        partes_ordenadas = sorted(frecuencia.items(), key=lambda x: (len(x[0]), x[0]))
        self.frecuencia_partes = "\n".join([
            f"{letra}: {freq} veces, Tamaño: {', '.join([f'{p[2]} x {p[3]}' for p in partes if p[0] == letra])}"
            for letra, freq in partes_ordenadas
        ])
    
        # Eliminar partes anteriores y crear nuevas
        self.parte_ids.unlink()
        for letra, layout, altura, base in partes:
            self.env['procesamiento.pdf.parte'].create({
                'pdf_id': self.id,
                'letra': letra,
                'layout': layout - 1,
                'altura_parte': float(altura.replace(',', '.').replace('cm', '')),
                'base_parte': float(base.replace(',', '.').replace('cm', '')),
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
