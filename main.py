from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from pathlib import Path
import time

start = time.perf_counter()

folder = Path(r"C:\Users\hugoo\Desktop\Pdf\1-10_pages\1_page")
output_dir = folder / 'txt_outputs'
output_dir.mkdir(parents=True, exist_ok=True)

max_files = 100
count = 0

for pdf_path in folder.glob('*.pdf'):
    try:
        reader = PdfReader(pdf_path, strict=False)
    except (PdfReadError, ValueError) as e:
        print(f"⛔ Skipping {pdf_path.name}: {e}")
        continue

    text = "".join(p.extract_text() or "" for p in reader.pages)

    # build an output filename, e.g. "document.pdf" → "document.txt"
    out_path = output_dir / (pdf_path.stem + '.txt')
    with open(out_path, 'w', encoding='utf-8') as fout:
        fout.write(text)

    print(f"Wrote {pdf_path.name} → {out_path.name}")
    count += 1
    if count >= max_files:
        break

end = time.perf_counter()
print(f"\nTotal execution time: {end - start:.2f} seconds")
