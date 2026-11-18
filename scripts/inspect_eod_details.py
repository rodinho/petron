import os
from pypdf import PdfReader

files = [
    "EOD POS 1 20260902.pdf",
    "EOD POS 2 20260902.pdf",
    "EOD POS 3 20260902.pdf",
    "End Shift Report Shift 1 Pos 2 20260902.pdf",
    "End Shift Report Shift 2 Pos 3 20260902.pdf",
    "OPT Sales Report 20260902.pdf",
]

for fname in files:
    path = os.path.join("input_files", "02", fname)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    reader = PdfReader(path)
    print("======================================================================")
    print(f"FILE: {fname} ({len(reader.pages)} pages)")
    print("======================================================================")
    for p_idx, page in enumerate(reader.pages):
        print(f"--- PAGE {p_idx+1} ---")
        lines = (page.extract_text() or "").splitlines()
        for line in lines:
            if line.strip():
                print(line.strip())
