import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

def extract_page_text(page):
    """Thread worker: extract text from one PdfReader page."""
    return page.extract_text() or ""

def extract_pdf_with_threads(pdf_path, max_workers=8):
    # 1) Load PDF once
    reader = PdfReader(pdf_path, strict=False)
    pages = reader.pages
    num_pages = len(pages)

    texts = [None] * num_pages

    # 2) Spin up threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # schedule each page extraction
        future_to_idx = {
            executor.submit(extract_page_text, pages[i]): i
            for i in range(num_pages)
        }
        # as each thread completes, store its result
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                texts[idx] = future.result()
            except Exception as e:
                texts[idx] = f"[Error on page {idx}: {e}]"

    # 3) Reassemble full text
    return "\n".join(texts)

if __name__ == "__main__":
    folder = Path('/Users/victoryan/Downloads/Pdf')
    output_dir = folder / 'txt_outputs'
    output_dir.mkdir(exist_ok=True)

    max_files = 100
    count = 0

    overall_start = time.perf_counter()
    for pdf_path in folder.glob('*.pdf'):
        start = time.perf_counter()
        try:
            full_text = extract_pdf_with_threads(pdf_path, max_workers=4)
        except (PdfReadError, ValueError) as e:
            print(f"⛔ Skipping {pdf_path.name}: {e}")
            continue
        elapsed = time.perf_counter() - start

        out_file = output_dir / (pdf_path.stem + '.txt')
        out_file.write_text(full_text, encoding='utf-8')

        print(f"{pdf_path.name!r} → {elapsed:.2f}s with threads")
        count += 1
        if count >= max_files:
            break

    total = time.perf_counter() - overall_start
    print(f"\nProcessed {count} PDFs in {total:.2f}s")
