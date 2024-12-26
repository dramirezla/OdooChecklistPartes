from PyPDF2 import PdfReader
import io
from collections import Counter
import re
import streamlit as st
from pdf2image import convert_from_bytes  # Necesitarás instalar esta librería



# Función para procesar el archivo PDF (Extraer texto)
def procesar_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    contenido_paginas = []
    
    for page in reader.pages:
        texto = page.extract_text() or ""
        contenido_paginas.append(texto)
    
    return contenido_paginas

# Función para convertir el PDF en imágenes
# Función para convertir PDF a imágenes
def mostrar_pdf_como_imagen(pdf_file):
    pdf_bytes = pdf_file.read()
    pdf_images = convert_from_bytes(pdf_bytes)
    pdf_images_bytes = []
    
    for img in pdf_images:
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format="PNG")
        pdf_images_bytes.append(img_byte_array.getvalue())
    
    return pdf_images_bytes

# Crear la interfaz de usuario en Streamlit
st.title("Sube tu archivo PDF para procesar")

# Subir archivo PDF
pdf_file = st.file_uploader("Elige un archivo PDF", type="pdf")

# Si el usuario ha subido un archivo
if pdf_file is not None:
    st.write("Archivo subido correctamente")

    # Convertir el archivo PDF en imágenes usando pdf2image
    pdf_images = mostrar_pdf_como_imagen(pdf_file)

    # Procesar el contenido del PDF (extraer texto)
    contenido_paginas = procesar_pdf(pdf_file)

    # Inicializar frecuencias y partes por página
    partes_frecuencia = Counter()  # Diccionario para contar la frecuencia de cada letra
    partes_por_pagina = []  # Lista para almacenar las partes encontradas por cada página
    letras_seleccionadas = []  # Lista para almacenar las letras seleccionadas

    # Extraer datos y actualizar las frecuencias antes de mostrar
    for texto_pagina in contenido_paginas:
        partes_pagina_dividida = texto_pagina.split("Kerf: ", 1)  # Dividir en dos partes; antes y después de "Kerf"
        contenido_modificado = partes_pagina_dividida[1] if len(partes_pagina_dividida) > 1 else ""
        partes_mayusculas = re.findall(r'[A-Z]', contenido_modificado)
        partes_frecuencia.update(partes_mayusculas)
        partes_por_pagina.append(partes_mayusculas)

    # Mostrar tabla de frecuencias al principio
    st.write("### Frecuencia inicial de las partes encontradas:")
    partes_frecuencia_df = {letra: frecuencia for letra, frecuencia in partes_frecuencia.items()}
    st.dataframe(partes_frecuencia_df)

    for page_number, (img_byte_array, partes_mayusculas) in enumerate(zip(pdf_images, partes_por_pagina)):
        # Mostrar los checkboxes para cada letra mayúscula
        st.write(f"### Checklist del Layout #{page_number}:")
        for i, parte in enumerate(partes_mayusculas):
            if st.checkbox(f"{parte}", key=f"parte_{page_number}_{i}"):
                letras_seleccionadas.append(parte)

        # Mostrar la imagen de la página
        st.image(img_byte_array, caption=f"Layout {page_number}", use_container_width=True)

    # Estilo y colores en la tabla de frecuencias
    if st.button("Mostrar Frecuencia de Partes seleccionadas"):
        letras_seleccionadas_frecuencia = Counter(letras_seleccionadas)
        if letras_seleccionadas_frecuencia:
            st.write("### Tabla de Frecuencia de las partes seleccionadas")
            st.dataframe(letras_seleccionadas_frecuencia)
        else:
            st.write("No se ha seleccionado ninguna letra.")
