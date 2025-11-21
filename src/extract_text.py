# extract_text.py
# extract_text.py
"""
Extract text from PDF and save to output/extracted_text.txt
Default PDF path is the uploaded file:
    /mnt/data/ukpga_20250022_en.pdf
"""
import argparse
import pdfplumber
from src.utils import save_text, clean_text, ensure_dirs
import os

DEFAULT_PDF = "/mnt/data/ukpga_20250022_en.pdf"
OUTPUT_TEXT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "extracted_text.txt")

def extract_pdf_text(pdf_path):
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
    return "\n\n".join(texts)

def main(pdf_path=DEFAULT_PDF, out_path=OUTPUT_TEXT):
    ensure_dirs(os.path.dirname(out_path))
    print(f"[+] Extracting text from: {pdf_path}")
    text = extract_pdf_text(pdf_path)
    text = clean_text(text)
    save_text(out_path, text)
    print(f"[+] Saved extracted text to: {out_path}")
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=str, default=DEFAULT_PDF, help="Path to PDF file")
    parser.add_argument("--out", type=str, default=OUTPUT_TEXT, help="Path to save extracted text")
    args = parser.parse_args()
    main(args.pdf, args.out)

print('Extract text placeholder')