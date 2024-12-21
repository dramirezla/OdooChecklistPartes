# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AttachmentProcessor(models.Model):
    _name = 'attachment.processor'
    _description = 'Attachment Processor'

    name = fields.Char(string="Name", required=True)
    attachment = fields.Binary(string="Attachment", attachment=True)
    attachment_filename = fields.Char(string="Attachment Filename")

    @api.model
    def process_attachment(self):
        """Process the attached .zip file and extract the PDF content."""
        import zipfile
        import io
        from PyPDF2 import PdfReader

        if not self.attachment or not self.attachment_filename.endswith('.zip'):
            raise ValueError("Please upload a valid .zip file.")

        # Read the zip file
        zip_file = zipfile.ZipFile(io.BytesIO(base64.b64decode(self.attachment)))

        for file_info in zip_file.infolist():
            if file_info.filename.endswith('.pdf'):
                # Extract the PDF file
                pdf_content = zip_file.read(file_info.filename)

                # Process the PDF
                pdf_reader = PdfReader(io.BytesIO(pdf_content))
                extracted_text = "".join(page.extract_text() for page in pdf_reader.pages)

                # Example: Extract NIT and price using patterns
                import re
                nit = re.search(r'NIT[:\s]*(\d+)', extracted_text)
                price = re.search(r'Precio[:\s]*\$?([0-9,\.]+)', extracted_text)

                return {
                    'nit': nit.group(1) if nit else None,
                    'price': price.group(1) if price else None,
                }

        raise ValueError("No valid PDF file found in the .zip archive.")
