#!/usr/bin/env python3
import shutil
from pathlib import Path
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
import matplotlib.pyplot as plt

def get_page_count(pdf_path):
    try:
        reader = PdfReader(pdf_path, strict=False)
        # decrypt empty PW if needed
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise PdfReadError("encrypted")
        return len(reader.pages)
    except (PdfReadError, ValueError) as e:
        print(f"⚠️  Could not read {pdf_path.name}: {e}")
        return None

def make_dir(base: Path, name: str) -> Path:
    """Ensure subfolder exists, return its Path."""
    d = base / name
    d.mkdir(exist_ok=True)
    return d

def classify_pdfs(folder: Path):
    folder = Path(folder)
    pdfs = list(folder.glob("*.pdf"))
    count = [0] * 11
    counts = 0
    print(f"count:{count}")
    # 1) Gather page counts, split into readable vs ineffective
    for pdf in pdfs:
        pc = get_page_count(pdf)
        if pc is not None and 1 <= pc <= 10:
            count[pc] += 1
    for i in range(1, 11):
        counts += count[i]
        print(f"{i} page files: {count[i]}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Classify PDFs into subfolders by page-count ranges and plot counts."
    )
    parser.add_argument(
        "folder",
        help="Path to the folder containing PDF files"
    )
    args = parser.parse_args()

    classify_pdfs(Path(args.folder))
