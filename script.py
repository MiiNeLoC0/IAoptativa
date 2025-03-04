import os
import requests
import xml.etree.ElementTree as ET
import re
import time
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd

# Reads the environment variable RUN_ENV to differentiate between "docker" and "local"
RUN_ENV = os.getenv("RUN_ENV", "local")

# If we are in Docker, Grobid is located at the hostname "grobid"
# Otherwise, we just assume Grobid runs on localhost
if RUN_ENV == "docker":
    GROBID_URL = "http://grobid:8070/api/processFulltextDocument"
    GROBID_HEALTH = "http://grobid:8070/api/isalive"
else:
    GROBID_URL = "http://localhost:8070/api/processFulltextDocument"
    GROBID_HEALTH = "http://localhost:8070/api/isalive"

# Directories for input PDFs and output files
INPUT_PDF_DIR = "papers/"
OUTPUT_GROBID_DIR = "grobid_output/"

# We check if output directory exists (create if needed)
os.makedirs(OUTPUT_GROBID_DIR, exist_ok=True)

# We'll store extracted data in these structures
extracted_abstracts = []  # List of abstract texts
paper_figure_counts = {}  # Dict to map filename -> number of figures
paper_links = {}  # Dict to map filename -> list of detected links


def wait_for_grobid():
    """
    Continuously checks if Grobid is alive by calling the /api/isalive endpoint.
    Retries every 5 seconds until it gets a successful response.
    """
    print("Waiting for Grobid")
    while True:
        try:
            response = requests.get(GROBID_HEALTH, timeout=2)
            if response.status_code == 200:
                print("Grobid is ready!")
                break
        except requests.ConnectionError:
            # If there's a connection error, do nothing and retry
            pass
        time.sleep(5)  # Wait 5 seconds before trying again


# We check if grobid is available
wait_for_grobid()

# Check if there are PDFs in the "papers/" directory.
# If none are found, raise an exception and stop.
pdf_files = [f for f in os.listdir(INPUT_PDF_DIR) if f.endswith(".pdf")]
if not pdf_files:
    raise FileNotFoundError("No PDF files found in the 'papers/' directory.")


def send_pdf_to_grobid(pdf_path):
    """
    Sends a PDF file to Grobid for processing.
    If Grobid returns a 200 status code, returns the TEI XML (as text).
    Otherwise, prints an error message and returns None.
    """
    with open(pdf_path, "rb") as pdf_file:
        files = {"input": pdf_file}
        # We pass teiCoordinates="figure" so Grobid includes figure coordinates
        response = requests.post(
            GROBID_URL, files=files, data={"teiCoordinates": "figure"}
        )
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error processing {pdf_path}: {response.status_code}")
        return None


def extract_paper_info(tei_xml, filename):
    """
    Parses the returned TEI XML to extract the abstract text and the number of figures.
    Appends the abstract text to extracted_abstracts,
    and updates the paper_figure_counts dictionary with the figure count.
    """
    root = ET.fromstring(tei_xml)  # Convert the TEI XML string into an ElementTree

    # Extract the abstract from all <abstract> tags
    abstract_content = ""
    for abstract in root.findall(".//{http://www.tei-c.org/ns/1.0}abstract"):
        # Combine the text content inside the <abstract> element
        abstract_content += " ".join(abstract.itertext()).strip()
    extracted_abstracts.append(abstract_content)

    # Count the number of <figure> tags
    figure_count = len(root.findall(".//{http://www.tei-c.org/ns/1.0}figure"))
    paper_figure_counts[filename] = figure_count

    # If there are zero figures, print a warning message
    if figure_count == 0:
        print(f"No figures found in {filename}.")


def extract_paper_links(tei_xml, filename):
    """
    Scans the TEI XML for any URLs in certain sections like abstract, body, references, etc.
    Stores the results in paper_links[filename].
    """
    root = ET.fromstring(tei_xml)
    extracted_links = []

    # We define the sections we want to search and their corresponding paths in the TEI XML
    sections_to_search = {
        "summary": ".//{http://www.tei-c.org/ns/1.0}abstract",
        "content": ".//{http://www.tei-c.org/ns/1.0}body",
        "references": ".//{http://www.tei-c.org/ns/1.0}listBibl",
        "annotations": ".//{http://www.tei-c.org/ns/1.0}note",
        "tables": ".//{http://www.tei-c.org/ns/1.0}table",
    }

    # For each section, gather all text and run a regex to detect links
    for section, path in sections_to_search.items():
        for element in root.findall(path):
            text = "".join(element.itertext()).strip()
            detected_links = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", text)
            for link in detected_links:
                extracted_links.append(
                    {"document": filename, "section": section, "url": link}
                )

    # Store all found links in the global dictionary
    paper_links[filename] = extracted_links

    # If no links were found in this PDF, print a message
    if not extracted_links:
        print(f"No links found in {filename}.")


# Loop through each PDF, send it to Grobid, and extract info/links if successful
for pdf_file in pdf_files:
    file_path = os.path.join(INPUT_PDF_DIR, pdf_file)
    print(f"Processing following pdf:  {file_path}...")
    tei_xml_data = send_pdf_to_grobid(file_path)
    if tei_xml_data:
        extract_paper_info(tei_xml_data, pdf_file)
        extract_paper_links(tei_xml_data, pdf_file)

# Write all extracted abstracts into a single text file
with open(
    os.path.join(OUTPUT_GROBID_DIR, "summaries.txt"), "w", encoding="utf-8"
) as file:
    file.write("\n".join(extracted_abstracts))

# Create a DataFrame of figure counts (filename vs. count) and save to CSV
figure_count_df = pd.DataFrame(
    list(paper_figure_counts.items()), columns=["Document", "Figure Count"]
)
figure_count_df.to_csv(os.path.join(OUTPUT_GROBID_DIR, "figure_data.csv"), index=False)

# Gather all links from every document, then save them to CSV
collected_links = []
for doc, links in paper_links.items():
    collected_links.extend(links)

link_data_df = pd.DataFrame(collected_links, columns=["document", "section", "url"])
link_data_df.to_csv(os.path.join(OUTPUT_GROBID_DIR, "extracted_links.csv"), index=False)

# Build one big string of all abstracts for the word cloud
full_abstract_text = " ".join(extracted_abstracts)

# Generate a word cloud from the combined abstracts
word_cloud = WordCloud(width=900, height=450, background_color="white").generate(
    full_abstract_text
)
plt.figure(figsize=(10, 5))
plt.imshow(word_cloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud of Extracted Summaries")
plt.savefig(os.path.join(OUTPUT_GROBID_DIR, "word_cloud_output.png"))
plt.show()

# Create a bar chart showing how many figures each paper had
plt.figure(figsize=(10, 5))
plt.bar(paper_figure_counts.keys(), paper_figure_counts.values(), color="lightcoral")
plt.xlabel("Document")
plt.ylabel("Number of Figures")
plt.title("Figures per Document")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_GROBID_DIR, "figure_chart.png"))
plt.show()

print("Finished. Results saved in 'processed_data/' (or 'grobid_output/').")
