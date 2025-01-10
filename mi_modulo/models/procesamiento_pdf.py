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
            partes_pagina_dividida = texto.split("Kerf: ", 1)  # Dividir en dos partes; antes y después de "Kerf"
            contenido_modificado = partes_pagina_dividida[1] if len(partes_pagina_dividida) > 1 else ""
    
            # Validar si se encontró una dimensión del layout
            if page_num == 1:
                match_dim = re.search(r'\[A1\]\s*(\d{1,4})[xX](\d{1,4})', texto)
                if match_dim:
                    altura_layout = int(match_dim.group(1))  # Primera captura (altura)
                    base_layout = int(match_dim.group(2))   # Segunda captura (base)
                else:
                    altura_layout, base_layout = 0, 0  # Valores predeterminados si no se encuentran dimensiones
    
            # Buscar dimensiones de las partes, ejemplo: "H: 12,0cm x 72,9cm"
            partes_dimensiones = re.findall(r'([A-Z]):\s*(\d{1,3},\d)cm\s*x\s*(\d{1,3},\d)cm', contenido_modificado)
    
            # Ejemplo: Calculando posiciones relativas (puedes adaptar esta lógica según el contenido del PDF)
            for letra, altura, base in partes_dimensiones:
                altura_num = float(altura.replace(',', '.'))  # Convertir a número
                base_num = float(base.replace(',', '.'))      # Convertir a número
                
                # Relativizar dimensiones con respecto al layout
                altura_relativa = round((altura_num / altura_layout) * 100, 2) if altura_layout else 0
                base_relativa = round((base_num / base_layout) * 100, 2) if base_layout else 0
            
                # Posiciones relativas arbitrarias (puedes extraerlas del contenido si es posible)
                pos_x_relativa = round((base_num / base_layout) * 50, 2)  # Ejemplo
                pos_y_relativa = round((altura_num / altura_layout) * 50, 2)  # Ejemplo
            
                partes.append({
                    'letra': letra,
                    'layout': page_num + 1,
                    'altura': altura_relativa,
                    'base': base_relativa,
                    'pos_x': pos_x_relativa,
                    'pos_y': pos_y_relativa,
                })
    
            frecuencia.update([parte['letra'] for parte in partes])
    
        # Ordenar alfabéticamente las claves de frecuencia antes de construir la tabla
        partes_ordenadas = sorted(frecuencia.items(), key=lambda x: (len(x[0]), x[0]))
        self.frecuencia_partes = "\n".join([f"{letra}: {freq}" for letra, freq in partes_ordenadas])
    
        # Eliminar partes anteriores y crear nuevas
        self.parte_ids.unlink()
        for parte in partes:
            self.env['procesamiento.pdf.parte'].create({
                'pdf_id': self.id,
                'letra': parte['letra'],
                'layout': parte['layout'],
                'altura': parte['altura'],
                'base': parte['base']
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
    altura = fields.Float(string='Altura (%)', digits=(6, 2))
    base = fields.Float(string='Base (%)', digits=(6, 2))
    pos_x = fields.Float(string='Posición X (%)', digits=(6, 2))  # Coordenada X relativa
    pos_y = fields.Float(string='Posición Y (%)', digits=(6, 2))  # Coordenada Y relativa
    seleccionada = fields.Boolean(string='CheckBox')

