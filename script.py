import os
import requests
import xml.etree.ElementTree as ET
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd

# Configuración del servidor GROBID
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"

# Directorios de entrada y salida
INPUT_PDF_DIR = "papers/"
OUTPUT_GROBID_DIR = "grobid_output/"

# Asegurar la existencia del directorio de salida
os.makedirs(OUTPUT_GROBID_DIR, exist_ok=True)

# Almacenamiento de datos extraídos
extracted_abstracts = []
paper_figure_counts = {}
paper_links = {}


# Función para procesar PDFs usando GROBID
def send_pdf_to_grobid(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        files = {"input": pdf_file}
        response = requests.post(
            GROBID_URL, files=files, data={"teiCoordinates": "figure"}
        )
    if response.status_code == 200:
        return response.text  # Devuelve el XML TEI
    else:
        print(f"Error al procesar {pdf_path}: {response.status_code}")
        return None


# Extraer información clave de los documentos procesados
def extract_paper_info(tei_xml, filename):
    root = ET.fromstring(tei_xml)

    # Extraer el resumen
    abstract_content = ""
    for abstract in root.findall(".//{http://www.tei-c.org/ns/1.0}abstract"):
        abstract_content += " ".join(abstract.itertext()).strip()

    extracted_abstracts.append(abstract_content)

    # Contar el número de figuras
    figure_count = len(root.findall(".//{http://www.tei-c.org/ns/1.0}figure"))
    paper_figure_counts[filename] = figure_count


# Extraer enlaces desde distintas secciones del documento
def extract_paper_links(tei_xml, filename):
    root = ET.fromstring(tei_xml)
    extracted_links = []

    sections_to_search = {
        "summary": ".//{http://www.tei-c.org/ns/1.0}abstract",
        "content": ".//{http://www.tei-c.org/ns/1.0}body",
        "references": ".//{http://www.tei-c.org/ns/1.0}listBibl",
        "annotations": ".//{http://www.tei-c.org/ns/1.0}note",
        "tables": ".//{http://www.tei-c.org/ns/1.0}table",
    }

    for section, path in sections_to_search.items():
        for element in root.findall(path):
            text = "".join(element.itertext()).strip()
            detected_links = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", text)
            for link in detected_links:
                extracted_links.append(
                    {"document": filename, "section": section, "url": link}
                )

    paper_links[filename] = extracted_links


# Procesar todos los archivos PDF
for pdf_file in os.listdir(INPUT_PDF_DIR):
    if pdf_file.endswith(".pdf"):
        file_path = os.path.join(INPUT_PDF_DIR, pdf_file)
        print(f"Procesando {file_path}...")
        tei_xml_data = send_pdf_to_grobid(file_path)
        if tei_xml_data:
            extract_paper_info(tei_xml_data, pdf_file)
            extract_paper_links(tei_xml_data, pdf_file)

# Guardar resúmenes extraídos
with open(
    os.path.join(OUTPUT_GROBID_DIR, "summaries.txt"), "w", encoding="utf-8"
) as file:
    file.write("\n".join(extracted_abstracts))

# Guardar recuento de figuras en CSV
figure_count_df = pd.DataFrame(
    list(paper_figure_counts.items()), columns=["Document", "Figure Count"]
)
figure_count_df.to_csv(os.path.join(OUTPUT_GROBID_DIR, "figure_data.csv"), index=False)

# Guardar enlaces extraídos en CSV
collected_links = []
for doc, links in paper_links.items():
    collected_links.extend(links)

link_data_df = pd.DataFrame(collected_links, columns=["document", "section", "url"])
link_data_df.to_csv(os.path.join(OUTPUT_GROBID_DIR, "extracted_links.csv"), index=False)

# Crear nube de palabras desde los resúmenes
full_abstract_text = " ".join(extracted_abstracts)
word_cloud = WordCloud(width=900, height=450, background_color="white").generate(
    full_abstract_text
)

plt.figure(figsize=(10, 5))
plt.imshow(word_cloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud of Extracted Summaries")
plt.savefig(os.path.join(OUTPUT_GROBID_DIR, "word_cloud_output.png"))
plt.show()

# Generar gráfico de barras con el recuento de figuras
plt.figure(figsize=(10, 5))
plt.bar(paper_figure_counts.keys(), paper_figure_counts.values(), color="lightcoral")
plt.xlabel("Document")
plt.ylabel("Number of Figures")
plt.title("Figures per Document")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_GROBID_DIR, "figure_chart.png"))
plt.show()

print("Finalizado. Resultados guardados en 'processed_data/'")
