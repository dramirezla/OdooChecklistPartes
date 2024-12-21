from odoo import models, fields, api
import fitz  # PyMuPDF
import re
from collections import Counter

class PdfProcessor(models.Model):
    _name = 'mimodelo2'
    _description = 'PDF Processor'

    name = fields.Char(string='Nombre del Documento')
    pdf_file = fields.Binary(string='Archivo PDF', attachment=True)
    extracted_text = fields.Text(string='Texto Extraído')
    letter_frequency = fields.Text(string='Frecuencia de Letras')
    image_previews = fields.Html(string='Vista Previa de Imágenes')

    def process_pdf(self):
        if self.pdf_file:
            pdf_data = self.pdf_file.decode('base64')  # Decodificar archivo binario
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

            extracted_text = ""
            letter_freq = Counter()
            image_tags = []

            for page in pdf_document:
                text = page.get_text()
                extracted_text += text

                # Buscar letras mayúsculas después de "Kerf:"
                parts = text.split("Kerf: ", 1)
                content = parts[1] if len(parts) > 1 else ""
                letters = re.findall(r'[A-Z]', content)
                letter_freq.update(letters)

                # Extraer imágenes
                for img_index, img in enumerate(page.get_images(full=True)):
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    img_tag = f'<img src="data:image/png;base64,{img_bytes}" width="200"/>'
                    image_tags.append(img_tag)

            self.extracted_text = extracted_text
            self.letter_frequency = str(letter_freq)
            self.image_previews = ''.join(image_tags)

