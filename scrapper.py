import glob
import xml.etree.ElementTree as ET
import psycopg2

def parse_xml_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    variables = {}

    # Traverse the XML tree and collect all the variables
    for element in root.iter():
        # Get the tag name
        tag = element.tag

        # Remove the namespace if present
        if '}' in tag:
            tag = tag.split('}')[1]

        # Process the attributes of the element
        for attr, value in element.attrib.items():
            attr_name = f'{tag}/{attr}'  # Combine the tag and attribute names
            variables[attr_name] = value

        # Process the text content of the element
        if element.text and element.text.strip():
            variables[tag] = element.text.strip()

    return variables

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="mahmud.db.elephantsql.com",
    database="yojgvdcw",
    user="yojgvdcw",
    password="6BKJVATqCv2B5ifJ4XAWOxb-xQXq0yIg"
)
cur = conn.cursor()
print("Connection Connected")

# Main execution
file_pattern = '*.xml'  # File pattern to match XML files in the directory
xml_files = glob.glob(file_pattern)  # Get a list of XML files matching the pattern

# Create a table to store the variables
cur.execute("""
    CREATE TABLE IF NOT EXISTS xml_data (
        filename TEXT PRIMARY KEY
    )
""")

# Get the unique set of column names from all XML files
unique_columns = set()

for filename in xml_files:
    all_variables = parse_xml_file(filename)
    print(f"Variables received from XML: {filename}")

    # Collect the unique column names
    unique_columns.update(all_variables.keys())

    # Insert the filename into the table
    try:
        cur.execute("INSERT INTO xml_data (filename) VALUES (%s)", (filename,))
    except:
        print(f"{filename} is already in the database.\nSkipping this data...")

# Create the column headers dynamically in the table
for column in unique_columns:
    # Replace slashes and curly braces with underscores in column names
    column_cleaned = column.replace('/', '_').replace('{', '_').replace('}', '_')
    try:
        cur.execute(f'ALTER TABLE xml_data ADD COLUMN IF NOT EXISTS "{column_cleaned}" TEXT')
    except:
        print(f"{filename} is already in the database.\nSkipping this data...")

# Insert the XML data into the table
for filename in xml_files:
    all_variables = parse_xml_file(filename)

    # Generate the SET clause dynamically
    set_columns = ', '.join([f'"{col.replace("/", "_").replace("{", "_").replace("}", "_")}" = %s' for col in all_variables.keys()])
    query = f"UPDATE xml_data SET {set_columns} WHERE filename = %s"

    # Execute the UPDATE query with variable values
    column_values = [all_variables.get(col) for col in all_variables.keys()]
    try:
        cur.execute(query, column_values + [filename])
    except:
        print(f"{filename} is already in the database.\nSkipping this data...")
# Commit the changes and close the database connection
conn.commit()
print("Committing changes...")

cur.close()
print("Closing connection...")

conn.close()
