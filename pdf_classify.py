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

def classify_pdfs(folder: Path, bin_size: int = 5):
    folder = Path(folder)
    pdfs = list(folder.glob("*.pdf"))

    readable = {}
    ineffective = []

    # 1) Gather page counts, split into readable vs ineffective
    for pdf in pdfs:
        pc = get_page_count(pdf)
        if pc is None:
            ineffective.append(pdf)
        else:
            readable[pdf] = pc

    if not readable and not ineffective:
        print("No PDFs found.")
        return

    # 2) Compute min/max over readable only
    if readable:
        pages = list(readable.values())
        mn, mx = min(pages), max(pages)
        print(f"Min pages = {mn}, Max pages = {mx}")

    # 3) Prepare ineffective_data folder
    ine_dir = make_dir(folder, "ineffective_data")
    for pdf in ineffective:
        shutil.move(str(pdf), str(ine_dir / pdf.name))

    # 4) Classify each readable PDF into bins
    for pdf, pc in readable.items():
        idx = (pc - 1) // bin_size
        start = idx * bin_size + 1
        end   = (idx + 1) * bin_size
        bin_name = f"{start}-{end}_pages"
        dest_dir = make_dir(folder, bin_name)
        shutil.move(str(pdf), str(dest_dir / pdf.name))
        print(f"Moved {pdf.name} ({pc} pages) → {bin_name}/")

    # 5) Build histogram data
    bins = [p for p in folder.iterdir() if p.is_dir()]
    names = []
    counts = []
    for b in sorted(bins):
        cnt = len(list(b.glob("*.pdf")))
        names.append(b.name)
        counts.append(cnt)

    # 6) Plot
    plt.figure(figsize=(10,6))
    bars = plt.bar(names, counts)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,  # x-coordinate: center of the bar
            height + 0.5,                      # y-coordinate: a little above the bar
            str(int(height)),                  # the label to show
            ha='center',                       # horizontal alignment
            va='bottom'                        # vertical alignment
        )
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Category")
    plt.ylabel("Number of PDF files")
    plt.title("PDF counts per page-count bin")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Classify PDFs into subfolders by page-count ranges and plot counts."
    )
    parser.add_argument(
        "folder",
        help="Path to the folder containing PDF files"
    )
    parser.add_argument(
        "--bin-size", "-b",
        type=int,
        default=5,
        help="Number of pages per bin (default: 5)"
    )
    args = parser.parse_args()

    classify_pdfs(Path(args.folder), bin_size=args.bin_size)
