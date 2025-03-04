# Rationale

This documents explains how did we valitaded each of our answers. The **why** and **how** we integrated Grobid, Docker, and Python libraries in our project, as well as the validation and testing measures taken to ensure reliable outcomes.

---

## Why Grobid?

- **High-Precision PDF Extraction**

  We choose Grobid because its a robust and structured extraction of academic paper components (including abstracts, figures, and references).

---

## Why Docker?

- **Reproducibility**  
  Docker ensures consistent runtime environments across multiple machines, eliminating the need of manual dependencies.

- **Isolation**  
  Containerization prevents version conflicts and library collisions on local hosts.

- **Seamless Distribution**  
  Colleagues can deploy and run the entire workflow via a single `docker-compose up` command, simplifying setup and collaboration.

---

## Pipeline Overview

1. **PDF Input**

   - All PDF should be placed in a `papers/` directory before running the program.

2. **Grobid Processing**

   - Our script transmits each PDF to Grobid’s `processFulltextDocument` endpoint for parsing.

3. **Data Extraction**

   - **Abstracts**: Extracted from `<abstract>` nodes in the TEI XML response.
   - **Figures**: Calculated based on `<figure>` element occurrences.
   - **Links**: Located via regular expressions across abstracts, main content, and references.

4. **Generated Outputs**
   - `summaries.txt` containing abstracts
   - `figure_data.csv` summarizing figure counts
   - `extracted_links.csv` listing all identified links
   - Word Cloud graphic (`word_cloud_output.png`)
   - Bar Chart visualization (`figure_chart.png`)

---

## Validation and Testing

1. **Local vs. Docker Execution**

   - An environment variable `RUN_ENV` is used to differentiate between local execution (`localhost:8070`) and Docker-based execution (`grobid:8070`).

2. **Empty PDF Directory**

   - If no PDFs exist in `papers/`, the script raises an error, alerting users to supply valid input files.

3. **Missing Figures or Links**

   - The script logs a warning if a document has no figures or links but continues processing without failing.

4. **Grobid connection check**
   - A `wait_for_grobid()` function repeatedly queries the `api/isalive` endpoint, ensuring Grobid is operational before PDF processing begins.

---
