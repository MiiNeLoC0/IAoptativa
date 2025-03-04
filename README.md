# README - Grobid PDF Processing Project

## Description

In this repository you will find two installation options to extract information from scientific papers in PDF format using **Grobid**. One being manually downloading the dependencies and running grobid with docker. The other one is using Docker to do all automatically. The objective of the project is to processes documents to extract **abstracts**, **figures count**, and **links** in order to visualize the results through a **word cloud** and **bar chart**.

## Requirements

We wil be using docker on both installations options. You only need to download Conda if you want to do the manual option.

- Docker: You can download it from (https://www.docker.com/).
- Conda: You can download it from (https://docs.conda.io/en/latest/miniconda.html).

## Installation Instructions

### Clone the repository

```bash
git clone https://github.com/MiiNeLoC0/IAoptativa.git
cd IAoptativa
```

### Open docker aplication

## 🚀 Execution Instructions

### **Option 1: Run with Docker (Recommended)**

This method automates everything using Docker. Just use the follow command.

```bash
docker-compose up --build
```

This will:

- Start the Grobid server.
- Process all PDFs inside the `papers/` folder.
- Save extracted data into `grobid_output/`.

### **Option 2: Run Locally with Conda**

If you prefer to run the project manually without using mainly Docker, follow these steps:
**Add your PDFs to `papers/`**

**Create a Conda environment and install dependencies:**

```bash
conda env create -f environment.yml
conda activate grobid_env
```

**Opem another terminal and start the Grobid server manually:**

```bash
docker run -t --rm -p 8070:8070 lfoppiano/grobid:latest-full
```

Wait untill grobid is connected.
**Run the script locally:**

```bash
python script.py
```

## Running Example

In `papers/` there are 1 example paper that you can use to try the program.

- Extracted abstracts are saved in `grobid_output/summaries.txt`
- Figures count per paper is saved in `grobid_output/figure_data.csv`
- Extracted links are stored in `grobid_output/extracted_links.csv`
- A **word cloud** is generated in `grobid_output/word_cloud_output.png`
- A **bar chart** of figures count is saved in `grobid_output/figure_chart.png`

## Preferred Citation

If using this project in research, cite **Xiaolei** as the main contributor. For example:

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
authors:
  - family-names: "Xiaolei"
    given-names: "Zhu"
title: "IAoptativa"
version: 1.0.0
doi: 10.5281/zenodo.14882318
date-released: 2025-02-17
url: "https://github.com/MiiNeLoC0/IAoptativa"
```

## Where to Get Help

You can contact the author through the following method:

- **Email:** `xiaolei.zhu@alumnos.upm.es`

## Acknowledgements

- **Grobid** for text extraction.
- **Docker** for containerized execution.
- **Conda** for environment management.
