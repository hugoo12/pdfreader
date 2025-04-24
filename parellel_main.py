import os
from multiprocessing import Pool, cpu_count
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from pathlib import Path
import time

def init_worker(path):
    global reader, num_pages
    reader = PdfReader(path, strict=False)
    num_pages = len(reader.pages)
def extract_page(page_idx):
    text = reader.pages[page_idx].extract_text() or ""
    return page_idx, text

def extract_pdf_in_parallel(pdf_path, workers=None):
    reader_main = PdfReader(pdf_path, strict=False)
    num_pages = len(reader_main.pages)

    workers = workers or cpu_count()
    with Pool(processes=workers, initializer=init_worker, initargs=(pdf_path,)) as pool:
        results = pool.map(extract_page, range(num_pages), chunksize=1)
    results.sort(key=lambda x: x[0])
    full_text = "\n".join(text for _, text in results)
    return full_text


if __name__ == "__main__":
    folder = Path(r'C:\Users\hugoo\Desktop\Pdf\1-10_pages\1_page')
    output_dir = folder / 'txt_outputs'
    output_dir.mkdir(parents=True, exist_ok=True)
    max_files = 100
    count = 0

    start_all = time.perf_counter()
    for pdf_path in folder.glob('*.pdf'):
        start = time.perf_counter()
        try:
            text = extract_pdf_in_parallel(pdf_path)
        except (PdfReadError, ValueError) as e:
            print(f"⛔ Skipping {pdf_path.name}: {e}")
            continue
        elapsed = time.perf_counter() - start

        out_path = output_dir / (pdf_path.stem + '.txt')
        with open(out_path, 'w', encoding='utf-8') as fout:
            fout.write(text)

        print(f"{pdf_path.name!r} → extracted in {elapsed:.2f}s")
        count += 1
        if count >= max_files:
            break
    total_elapsed = time.perf_counter() - start_all
    print(f"All done in {total_elapsed:.2f}s")
