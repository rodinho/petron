import sys, os
sys.path.insert(0, os.path.abspath("."))
from process_closure import run_consolidation

pos_map, der_comp = run_consolidation(
    pos1_s1_path="input_files/02/EOD POS 1 20260902.pdf",
    opt_path="input_files/02/OPT Sales Report 20260902.pdf",
    der_path="input_files/02/DER 20260902.pdf"
)
print("Consolidation completed successfully!")
print("Active keys in pos_map:", [k for k, v in pos_map.items() if v])
if der_comp:
    for k, v in der_comp.items():
        print(f"{k}: POS={v['pos']}, DER={v['der']}, diff={v['diff']}, match={v['match']}")
