from flask import Flask, render_template, request, redirect, url_for
import os
import glob
import xml.etree.ElementTree as ET
import psycopg2

app = Flask(__name__)

def parse_xml_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    variables = {}

    for element in root.iter():
        tag = element.tag

        if '}' in tag:
            tag = tag.split('}')[1]

        for attr, value in element.attrib.items():
            attr_name = f'{tag}/{attr}'
            variables[attr_name] = value

        if element.text and element.text.strip():
            variables[tag] = element.text.strip()

    return variables

# Configurar la conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    host="mahmud.db.elephantsql.com",
    database="yojgvdcw",
    user="yojgvdcw",
    password="6BKJVATqCv2B5ifJ4XAWOxb-xQXq0yIg"
)
cur = conn.cursor()

# Crear una tabla para almacenar la información de los archivos XML
cur.execute("""
    CREATE TABLE IF NOT EXISTS xml_data (
        filename TEXT PRIMARY KEY
    )
""")

# Conjunto para almacenar las columnas únicas
unique_columns = set()

@app.route("/")
def index():
    cur.execute("SELECT filename, * FROM xml_data")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return render_template("index.html", rows=rows, columns=columns)

@app.route("/upload", methods=["POST"])
def upload_xml():
    uploaded_files = request.files.getlist("xml_files")
    uploaded_data = []

    for uploaded_file in uploaded_files:
        if uploaded_file.filename != '':
            file_path = os.path.join('static/uploads', uploaded_file.filename)
            uploaded_file.save(file_path)

            all_variables = parse_xml_file(file_path)

            # Extraer solo las claves deseadas
            extracted_data = {
                "filename": uploaded_file.filename,
                "NOMBRE": all_variables.get("NOMBRE", ""),
                "Comprobante_Folio": all_variables.get("Comprobante_Folio", ""),
                "FE_FECHA": all_variables.get("FE_FECHA", "")
            }

            unique_columns.update(extracted_data.keys())

            try:
                cur.execute("INSERT INTO xml_data (filename) VALUES (%s)", (file_path,))
                conn.commit()
            except:
                print(f"{file_path} is already in the database.\nSkipping this data...")

            set_columns = ', '.join([f'"{col.replace("/", "_").replace("{", "_").replace("}", "_")}" = %s' for col in extracted_data.keys()])
            query = f"UPDATE xml_data SET {set_columns} WHERE filename = %s"
            column_values = [extracted_data.get(col, "") for col in extracted_data.keys()]
            try:
                cur.execute(query, column_values + [file_path])
                conn.commit()
            except:
                print(f"{file_path} is already in the database.\nSkipping this data...")

            # Agregar la información del archivo actual a la lista uploaded_data
            uploaded_data.append(extracted_data)

            # Eliminar el archivo después de procesarlo
            os.remove(file_path)

    # Obtener las columnas únicas de los archivos cargados
    columns = list(unique_columns)
    return render_template("index.html", uploaded_data=uploaded_data, columns=columns)

if __name__ == "__main__":
    app.run(debug=True)
