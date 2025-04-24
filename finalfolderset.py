#!/usr/bin/env python3
import shutil
from pathlib import Path
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

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

    single_page = []
    double_page = []
    other_page = []

    single_dir = make_dir(folder, "1_page")
    double_dir = make_dir(folder, "2_page")
    triple_dir = make_dir(folder, "3-10_page")

    for pdf in pdfs:
        pc = get_page_count(pdf)
        if pc == 1:
            single_page.append(pdf)
            shutil.move(str(pdf), str(single_dir / pdf.name))
        elif pc == 2:
            double_page.append(pdf)
            shutil.move(str(pdf), str(double_dir / pdf.name))
        elif 3<= pc <= 10:
            other_page.append(pdf)
            shutil.move(str(pdf), str(triple_dir / pdf.name))


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
