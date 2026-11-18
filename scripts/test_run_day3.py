import sys, os
sys.path.insert(0, os.path.abspath("."))
from process_closure import run_consolidation
import openpyxl

pos_map, der_comp = run_consolidation(
    pos1_s1_path="input_files/03/End Shift Report Shift 1 Pos 1 20260903.pdf",
    pos1_s2_path="input_files/03/End Shift Report Shift 2 Pos 1 20260903.pdf",
    opt_path="input_files/03/OPT Sales Report 20260903.pdf",
    der_path="input_files/03/Day End Report 20260903.pdf",
    output_wb="petron-till-closure-shifts.xlsx",
    pos_summary_wb="petron-till-closure-pos-summary.xlsx"
)

print("\n--- Day 03 Consolidation Complete ---")
print("Active keys in pos_map:", [k for k, v in pos_map.items() if v])

print("\n=== Checking petron-till-closure-shifts.xlsx ===")
wb1 = openpyxl.load_workbook("petron-till-closure-shifts.xlsx", data_only=False)
for s in wb1.sheetnames:
    ws = wb1[s]
    sales = ws['E25'].value or ws['E35'].value
    pay = ws['H55'].value
    var = ws['H57'].value
    print(f"Sheet: {s:<15} | Till: {ws['C2'].value} | Cashier: {ws['C4'].value} | Sales: {sales} | Pay: {pay}")

print("\n=== Checking petron-till-closure-pos-summary.xlsx ===")
wb2 = openpyxl.load_workbook("petron-till-closure-pos-summary.xlsx", data_only=False)
for s in wb2.sheetnames:
    ws = wb2[s]
    sales = ws['E25'].value or ws['E35'].value
    pay = ws['H55'].value
    var = ws['H57'].value
    print(f"Sheet: {s:<15} | Till: {ws['C2'].value} | Cashier: {ws['C4'].value} | Sales: {sales} | Pay: {pay}")
