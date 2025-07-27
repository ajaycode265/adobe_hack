import os
import json
import fitz  # PyMuPDF
from pathlib import Path
from collections import Counter

def get_font_styles(doc):
    """Extracts all font styles (size, flags, font_name) and their frequencies."""
    styles = Counter()
    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        styles[(span["size"], span["flags"], span["font"])] += 1
    return styles

def get_main_body_style(styles):
    """Determines the most common font style, assumed to be the body text."""
    if not styles:
        return None
    # Find the style with the highest frequency
    most_common_style = styles.most_common(1)[0][0]
    return most_common_style

def extract_outline_from_pdf(pdf_path):
    """Extracts the title and a structured outline from a PDF."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return None

    # 1. Extract Title
    title = doc.metadata.get("title", "")
    if not title:
        # Fallback: use the largest text on the first page as the title
        max_size = 0
        blocks = doc[0].get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["size"] > max_size:
                            max_size = span["size"]
                            title = span["text"]
    title = title.strip() if title else pdf_path.stem

    # 2. Analyze font styles to identify headings
    styles = get_font_styles(doc)
    main_body_style = get_main_body_style(styles)

    if not main_body_style:
        return {"title": title, "outline": []}

    main_body_size = main_body_style[0]

    # Identify potential heading sizes (larger than body text)
    heading_sizes = sorted([s[0] for s in styles if s[0] > main_body_size], reverse=True)
    
    # Create a mapping from size to H-level (H1, H2, H3)
    size_to_level = {}
    if len(heading_sizes) > 0:
        size_to_level[heading_sizes[0]] = "H1"
    if len(heading_sizes) > 1:
        size_to_level[heading_sizes[1]] = "H2"
    if len(heading_sizes) > 2:
        size_to_level[heading_sizes[2]] = "H3"

    # 3. Extract Outline
    outline = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["size"] in size_to_level:
                            text = span["text"].strip()
                            if text:  # Avoid empty headings
                                outline.append({
                                    "level": size_to_level[span["size"]],
                                    "text": text,
                                    "page": page_num + 1
                                })
    
    doc.close()
    return {"title": title, "outline": outline}

def process_pdfs():
    """Processes all PDFs in the input directory and saves the outlines."""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found at " + str(input_dir))
        return

    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        result = extract_outline_from_pdf(pdf_file)
        
        if result:
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            print(f"  -> Saved output to {output_file.name}")

if __name__ == "__main__":
    print("Starting PDF outline extraction...")
    process_pdfs()
    print("Completed processing all PDFs.")
