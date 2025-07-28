# PDF Outline Extractor

## Overview

This project is a PDF processing solution designed to automatically extract a structured outline—including a title and hierarchical headings (H1, H2, H3)—from PDF documents. It is containerized using Docker, ensuring a consistent and isolated runtime environment.

The script processes all PDF files from a designated `input` directory and generates a corresponding `.json` file for each, containing the extracted structure.

## How It Works

The core logic resides in the `process_pdfs.py` script, which leverages the **PyMuPDF** library to analyze the content of each PDF. The process is as follows:

1.  **Title Extraction**:
    *   The script first attempts to extract the title from the PDF's metadata.
    *   If no metadata title is found, it intelligently falls back to identifying the text with the largest font size on the first page, assuming it to be the main title.
    *   If neither method yields a title, the PDF's filename is used as a last resort.

2.  **Heading Identification**:
    *   To distinguish headings from body text, the script performs a frequency analysis of all font styles (a combination of size, flags, and font name) used throughout the document.
    *   The most frequently occurring style is assumed to be the **main body text**.
    *   Any text set in a font size **larger** than the main body text is classified as a potential heading.

3.  **Hierarchical Structuring**:
    *   The identified heading font sizes are sorted in descending order.
    *   The top three largest sizes are mapped to heading levels:
        *   **Largest size** -> **H1**
        *   **Second-largest size** -> **H2**
        *   **Third-largest size** -> **H3**
    *   The script then iterates through the document, tagging each piece of text that matches these heading styles with its corresponding level and page number.

4.  **JSON Output**:
    *   The final extracted structure, including the title and the list of headings, is written to a JSON file.

## Technology Stack

*   **Language**: Python 3.10
*   **PDF Processing**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) - A high-performance Python library for data extraction and manipulation of PDF documents.
*   **Containerization**: Docker - To create a portable and reproducible environment for the application.

## Project Structure

```
.
├── Dockerfile           # Defines the Docker container environment and dependencies.
├── process_pdfs.py      # The main Python script for PDF processing logic.
├── input/               # Directory where you place the PDFs to be processed.
├── output/              # Directory where the resulting JSON files will be saved.
└── sample_dataset/
    ├── pdfs/            # Sample PDF files for testing.
    └── outputs/         # Expected JSON output for the sample PDFs.
```

## How to Run

### Prerequisites

*   [Docker](https://www.docker.com/get-started) must be installed and running on your system.

### Step 1: Build the Docker Image

First, build the Docker image from the project's root directory. This command creates an image named `pdf-processor`.

```bash
docker build --platform linux/amd64 -t pdf-processor .
```

### Step 2: Run the Processor

Once the image is built, you can run the processor. The command mounts local directories into the container for input and output.

#### To process the included sample PDFs:

This command reads PDFs from `sample_dataset/pdfs` and saves the JSON output to `sample_dataset/outputs`.

```bash
docker run --rm \
  -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" \
  -v "$(pwd)/sample_dataset/outputs:/app/output" \
  --network none \
  pdf-processor
```

#### To process your own PDFs:

1.  Place your PDF files in the `input` directory.
2.  Create an `output` directory if it doesn't exist.
3.  Run the following command:

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input:ro" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  pdf-processor
```

**Note on Volume Paths**: The `$(pwd)` syntax works on Linux and macOS. For Windows PowerShell, you can use `${pwd}`. For Windows Command Prompt, use `%cd%`.

## Expected Output Format

The script generates a JSON file for each input PDF with the following structure:

```json
{
    "title": "Extracted Document Title",
    "outline": [
        {
            "level": "H1",
            "text": "This is a Main Heading",
            "page": 1
        },
        {
            "level": "H2",
            "text": "This is a Subheading",
            "page": 2
        }
    ]
}
