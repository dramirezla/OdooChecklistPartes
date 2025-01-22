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
    
        for page_num, page in enumerate(reader.pages):
            texto = page.extract_text() or ""
            if page_num == 0:
                raise UserError(texto)
            partes_pagina_dividida = texto.split("Kerf: ", 1)  # Dividir en dos partes; antes y después de "Kerf"
            contenido_modificado = partes_pagina_dividida[1] if len(partes_pagina_dividida) > 1 else ""
    
            # 1. Buscar combinaciones de letras mayúsculas seguidas de ":"
            letras_con_dos_puntos = re.findall(r'[A-Z]{1,2}:', contenido_modificado)
            
            if letras_con_dos_puntos:
                # Si hay combinaciones seguidas de ":", tomar esas (sin el ":")
                partes_pagina = [letra.rstrip(':') for letra in letras_con_dos_puntos]
            else:
                # Si no hay combinaciones seguidas de ":", tomar todas las letras mayúsculas individuales
                partes_pagina = re.findall(r'[A-Z]', contenido_modificado)
    
            # Asociar las partes a la página correspondiente
            partes += [(letra, page_num + 1) for letra in partes_pagina]
            frecuencia.update(partes_pagina)
    
        # Ordenar alfabéticamente las claves de frecuencia antes de construir la tabla
        partes_ordenadas = sorted(frecuencia.items(), key=lambda x: (len(x[0]), x[0]))
        self.frecuencia_partes = "\n".join([f"{letra}: {freq}" for letra, freq in partes_ordenadas])
    
        # Eliminar partes anteriores y crear nuevas
        self.parte_ids.unlink()
        for letra, layout in partes:
            self.env['procesamiento.pdf.parte'].create({
                'pdf_id': self.id,
                'letra': letra,
                'layout': layout - 1
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
