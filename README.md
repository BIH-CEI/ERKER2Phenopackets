# ERKER to Phenopackets
In this repository we are developing a pipeline mapping the ERKER Dataset to the [Phenopackets](https://github.com/phenopackets/phenopacket-schema) format. The ERKER dataset is a collection of clinical data from the Charité Berlin. The Phenopackets format is a standard for the exchange of phenotypic and genomic data for patients with rare diseases. The goal of this project is to develop a general pipeline that can be used to map any clinical dataset to the Phenopackets format.

More information on Phenopackets:
- [Phenopackets Documentation](https://phenopackets-schema.readthedocs.io/en/latest/)
- [Article on Phenopackets in the journal Nature Biotechnology](https://www.nature.com/articles/s41587-022-01357-4)

[![Unit Tests and Code Style](https://github.com/https://github.com/BIH-CEI/ERKER2Phenopackets/actions/workflows/python-app.yaml/badge.svg)](https://github.com/BIH-CEI/ERKER2Phenopackets/blob/main/.github/workflows/python-app.yaml))


## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Installation](#installation)
- [Resources](#resources)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Project Description

Reliable exchange of medical data between medical facilities is essential for patient's medical care. Especially patients with rare diseases can profit of digital interoperability. 

To capture and produce RD-specific and FAIR (Findability, Accessability, Interoperability, Reusability) data, the *ERKER* (ERDRI-CDS kompatible Erfassung in REDCap / ERDRI-CDS compatible data capture in REDCap) was developed within our research projects CORD-MI, Screen4Care, Fair4Rare and Lab4Rare. With the subproject ERKER2Phenopackets we develop the transfer of ERKER data to Phenopackets - a computable representation of clinical data enabling deep phenotyping. The MC4R-deficiency, a rare genetic disease resulting in severe obesity, is used to develop the first example pipeline.

Please find a set of 50 phenopackets that were created artificially in the [`ERKER2Phenopackets/data/out/phenopackets`](https://github.com/BIH-CEI/ERKER2Phenopackets/tree/main/ERKER2Phenopackets/data/out/phenopackets/example-phenopackets-from-synthetic-data) directory.

## Features

REDCap is a clinical electronic data capture system, for which many university hospitals have licenses. The *ERKER* version 1.5 form (ERDRI-CDS kompatible Erfassung in REDCap / ERDRI-CDS compatible data capture in REDCap) can be downloaded for free here: https://github.com/BIH-CEI/ERKER. For disease specific RD data capture in .csv or Excel format, you can use the Python import template to capture the data semi automatically. 

For further use of Phenopackets please read: https://www.nature.com/articles/s41587-022-01357-4. The overall pipeline from the ERKER format to Phenopackets will be developed here. 

## Installation

### 1. Installing Python

We recommend the installation using Anaconda

#### A. Installing Python with pip (Standard Python)

To install Python using the standard method with pip, follow these steps:

1. **Check if Python is already installed:** Open your terminal or command prompt and type `python --version` or `python3 --version`. <br>
  a. If Python is installed, you'll see the version number. Please check that your version is at least `3.10` or higher. if not, run `pip install --upgrade python` <br>
  b. If not, proceed with the installation.

3. **Download Python:** Visit the official Python website at [python.org](https://www.python.org/downloads/) and download the latest version of Python for your operating system.

4. **Run the Installer:** Double-click the downloaded installer and follow the on-screen instructions. Make sure to check the box that says "Add Python to PATH" during installation to easily run Python from the command line.

5. **Verify Installation:** After installation, open your terminal or command prompt and type `python --version` or `python3 --version` to confirm that Python is installed and check the version.

#### B. Installing Python with Anaconda

Anaconda is a popular distribution of Python that comes with many pre-installed data science libraries and tools. To install Python using Anaconda, follow these steps:

1. **Download Anaconda:** Visit the Anaconda website at [anaconda.com](https://www.anaconda.com/download#downloads) and download the Anaconda distribution for your operating system.

2. **Run the Installer:** Double-click the downloaded Anaconda installer and follow the on-screen instructions. Anaconda provides an installer with a graphical user interface that makes it easy to customize your installation.

3. **Create an Environment (Optional, but highly recommended):** Anaconda allows you to create isolated Python environments for different projects. You can use the Anaconda Navigator or the command line to create and manage environments. [Anaconda Creating Environment Tutorial](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/)

4. **Verify Installation:** After installation, open your terminal or Anaconda Navigator and type `python --version` or `python3 --version` to confirm that Anaconda Python is installed and check the version.

Now, you have Python installed on your system, and you can start using it by running `python` in your terminal.

### 2. Clone this repository to your machine.

1. Open a git CMD
2. Navigate to the folder where you would like to install this git repository.
3. Run `git clone https://github.com/BIH-CEI/ERKER2Phenopackets`

### 3. Installing Required Python Packages

1. Open your Python CMD
2. Navigate into the repository folder
3. Run `pip install .`
4. (Optional): If you would like to install the required Python packages for testing run `pip install .[test]`

### 4. Installing MongoDB
  Please follow the official [MongoDB Installation Tutorial](https://www.mongodb.com/docs/manual/administration/install-community/).

## Resources

### Ontologies
- Human Phenotype Ontology (HP, version: 2023-06-06) [🔗](http://www.human-phenotype-ontology.org)
- Online Mendelian Inheritance in Man (OMIM, version: 2023-09-08) [🔗](https://www.omim.org/)
- Orphanet Rare Disease Ontology (OPRHA, version: 2023-09-10) [🔗](https://www.orpha.net/)
- National Center for Biotechnology Information Taxonomy (NCBITaxon, version: 2023-02-21) [🔗](https://www.ncbi.nlm.nih.gov/taxonomy)
- Logical Observation Identifiers Names and Codes (LOINC, version: 2023-08-15) [🔗](https://loinc.org/)
- HUGO Gene Nomenclature Committee (HGNC, version: 2023-09-10) [🔗](https://www.genenames.org/)
- Gene Ontology (GENO, version: 2023-07-27) [🔗](https://geneontology.org/)

## License

This project is licensed under the terms of the [MIT License](https://github.com/BIH-CEI/ERKER2Phenopackets/blob/main/LICENSE)

## Acknowledgements

We would like to extend our thanks to Daniel Danis for his support in the development of this project.

---

- Authors: 
  - [Adam Gräfe](https://github.com/graefea)
  - [Filip Rehburg](https://github.com/frehburg)
