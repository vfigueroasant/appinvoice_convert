import streamlit as st
import pandas as pd
import pdfplumber

# Función para extraer los datos del PDF
def extract_data_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Función para procesar los datos extraídos
def process_data(text, divisor):
    lines = text.split('\n')
    data = []
    for line in lines:
        columns = line.split()
        if len(columns) >= 7:
            try:
                # Extraemos los valores de las columnas según el nuevo orden
                referencia = columns[0]
                codigo = columns[1]
                cantidad = float(columns[2].replace(',', ''))
                descripcion = " ".join(columns[3:-3])  # Unimos las columnas para obtener la descripción
                precio = float(columns[-3].replace(',', ''))
                itbis = float(columns[-2].replace(',', ''))
                importe = float(columns[-1].replace(',', ''))

                # 1. Dividir el precio por el divisor
                nuevo_precio = precio / divisor

                # 2. Calcular el importe (nuevo precio * cantidad)
                nuevo_importe = nuevo_precio * cantidad

                # 3. Calcular el ITBIS (nuevo importe * 0.18)
                nuevo_itbis = nuevo_importe * 0.18

                # Añadimos los datos en el orden correcto
                data.append([codigo, descripcion, nuevo_precio, cantidad, nuevo_importe, nuevo_itbis])
            except ValueError:
                # Si hay un error al convertir a float, continuamos con la siguiente línea
                continue
    return data

# Función para crear un DataFrame y exportarlo a Excel
def create_excel(data, output_path):
    df = pd.DataFrame(data, columns=["CODIGO", "DESCRIPCION", "PRECIO", "CANTIDAD", "IMPORTE", "ITBIS"])
    df.to_excel(output_path, index=False)

# Interfaz gráfica con Streamlit
def main():
    # Título en azul
    st.markdown("<h1 style='color: blue;'>BEDU INVOICE</h1>", unsafe_allow_html=True)
    
# Agregar una imagen al sidebar



    st.sidebar.header("Configuración")

    
    divisor = st.sidebar.number_input("Ingrese el valor divisor:", value=0.7, min_value=0.1, max_value=10.0, step=0.1)
    
    uploaded_file = st.file_uploader("Cargar archivo PDF", type="pdf")
    
    if uploaded_file is not None:
        pdf_text = extract_data_from_pdf(uploaded_file)
        data = process_data(pdf_text, divisor)
        
        if data:
            st.subheader("Datos Procesados")
            df = pd.DataFrame(data, columns=["CODIGO", "DESCRIPCION", "PRECIO", "CANTIDAD", "IMPORTE", "ITBIS"])
            st.write(df)
            
            if st.button("Procesar y exportar a Excel"):
                output_path = "cotizacion_procesada.xlsx"
                create_excel(data, output_path)
                st.success(f"Datos procesados y exportados a {output_path}")
                # Proporcionar un enlace para descargar el archivo
                with open(output_path, "rb") as file:
                    btn = st.download_button(
                        label="Descargar Excel",
                        data=file,
                        file_name=output_path,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.warning("No se encontraron datos procesables en el PDF.")
                
if __name__ == "__main__":
    main()

