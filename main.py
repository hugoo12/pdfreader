from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pathlib import Path
import time

start = time.perf_counter()


def safe_extract_all_text(reader):
    text = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            chunk = page.extract_text() or ""
        except (PdfReadError, AttributeError) as e:
            print(f" ⚠️  Skipping page {i} due to parse error: {e!r}")
            continue
        text.append(chunk)
    return "\n".join(text)

folder = Path(r"C:\Users\hugoo\Desktop\Pdf\41-inf_pages")
output_dir = folder / 'txt_outputs1'
output_dir.mkdir(parents=True, exist_ok=True)

max_files = 350
count = 0

for pdf_path in folder.glob('*.pdf'):
    try:
        reader = PdfReader(pdf_path, strict=False)
    except (PdfReadError, ValueError) as e:
        print(f"⛔ Skipping {pdf_path.name}: {e}")
        continue

    text = safe_extract_all_text(reader)

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
