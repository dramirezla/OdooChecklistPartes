from odoo import models, fields, api
import PyPDF2
from pdf2image import convert_from_bytes
import re
from collections import Counter
import base64

class PdfProcessor(models.Model):
    _name = 'mimodelo2'
    _description = 'PDF Processor'

    name = fields.Char(string='Nombre del Documento')
    pdf_file = fields.Binary(string='Archivo PDF', attachment=True)
    extracted_text = fields.Text(string='Texto Extraído')
    letter_frequency = fields.Text(string='Frecuencia de Letras')
    image_previews = fields.Html(string='Vista Previa de Imágenes')
    activity_ids = fields.Many2many(string='Activities')

    def process_pdf(self):
        if self.pdf_file:
            # Decodificar archivo binario
            pdf_data = base64.b64decode(self.pdf_file)

            # Extraer texto usando PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_data)
            extracted_text = ""
            letter_freq = Counter()

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                extracted_text += text if text else ""

                # Buscar letras mayúsculas después de "Kerf:"
                parts = text.split("Kerf: ", 1)
                content = parts[1] if len(parts) > 1 else ""
                letters = re.findall(r'[A-Z]', content)
                letter_freq.update(letters)

            # Extraer imágenes usando pdf2image
            image_tags = []
            images = convert_from_bytes(pdf_data)
            for img in images:
                img_bytes = img.tobytes("png")  # Convierte la imagen a formato PNG
                img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                img_tag = f'<img src="data:image/png;base64,{img_base64}" width="200"/>'
                image_tags.append(img_tag)

            # Guardar los resultados en los campos correspondientes
            self.extracted_text = extracted_text
            self.letter_frequency = str(letter_freq)
            self.image_previews = ''.join(image_tags)

