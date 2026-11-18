import os
import openpyxl
from process_closure import run_consolidation

def main():
    print("=" * 75)
    print("      PETRON DYNAMIC TILL CLOSURE CONSOLIDATION (2 SHIFTS)")
    print("=" * 75)
    
    # Priority folders: input_files/02, input_files/03, or input_files
    input_dirs = ["input_files/02", "input_files/03", "input_files/01", "input_files"]
    selected_dir = next((d for d in input_dirs if os.path.exists(d)), "input_files")
    
    print(f"Scanning directory: {selected_dir}")
    
    pos1_s1, pos1_s2 = "", ""
    pos2_s1, pos2_s2 = "", ""
    pos3_s1, pos3_s2 = "", ""
    opt_file = ""
    teraju_file = ""
    
    if os.path.exists(selected_dir):
        files = os.listdir(selected_dir)
        for f in sorted(files):
            path = os.path.join(selected_dir, f)
            fu = f.upper()
            if "TERAJU" in fu or "RECEIVABLE" in fu:
                if not teraju_file: teraju_file = path
            elif "OPT" in fu:
                if not opt_file: opt_file = path
            elif "POS 1" in fu or "POS1" in fu:
                if "SHIFT 1" in fu or "S1" in fu: pos1_s1 = path
                elif "SHIFT 2" in fu or "S2" in fu: pos1_s2 = path
                elif not pos1_s1: pos1_s1 = path
            elif "POS 2" in fu or "POS2" in fu:
                if "SHIFT 1" in fu or "S1" in fu: pos2_s1 = path
                elif "SHIFT 2" in fu or "S2" in fu: pos2_s2 = path
                elif not pos2_s1: pos2_s1 = path
                elif not pos2_s2: pos2_s2 = path
            elif "POS 3" in fu or "POS3" in fu:
                if "SHIFT 1" in fu or "S1" in fu: pos3_s1 = path
                elif "SHIFT 2" in fu or "S2" in fu: pos3_s2 = path
                elif not pos3_s1: pos3_s1 = path
                elif not pos3_s2: pos3_s2 = path

    print("\nSource Files Detected:")
    print(f"  POS 1 (Shift 1): {pos1_s1 if pos1_s1 else '[NONE / INACTIVE]'}")
    print(f"  POS 1 (Shift 2): {pos1_s2 if pos1_s2 else '[NONE / INACTIVE]'}")
    print(f"  POS 2 (Shift 1): {pos2_s1 if pos2_s1 else '[NONE / INACTIVE]'}")
    print(f"  POS 2 (Shift 2): {pos2_s2 if pos2_s2 else '[NONE / INACTIVE]'}")
    print(f"  POS 3 (Shift 1): {pos3_s1 if pos3_s1 else '[NONE / INACTIVE]'}")
    print(f"  POS 3 (Shift 2): {pos3_s2 if pos3_s2 else '[NONE / INACTIVE]'}")
    print(f"  OPT Terminal   : {opt_file if opt_file else '[NONE / INACTIVE]'}")
    print(f"  Teraju Raasa   : {teraju_file if teraju_file else '[NONE]'}")
    
    target_wb = "petron-till-closure.xlsx"
    try:
        run_consolidation(
            pos1_s1_path=pos1_s1,
            pos1_s2_path=pos1_s2,
            pos2_s1_path=pos2_s1,
            pos2_s2_path=pos2_s2,
            pos3_s1_path=pos3_s1,
            pos3_s2_path=pos3_s2,
            opt_path=opt_file,
            teraju_path=teraju_file,
            output_wb=target_wb
        )
        print(f"\n[OK] Generated and populated '{target_wb}' successfully.")
    except PermissionError as pe:
        print(f"\n[NOTICE] {pe}")
        target_wb = "petron-till-closure_updated.xlsx"

    print("\nSummary Reconciliation:")
    print("-" * 75)
    print(f"{'Till / Shift':<16} {'Cashier':<14} {'Sales (RM)':<12} {'Pass-thru':<12} {'Payments':<12} {'Variance'}")
    print("-" * 75)
    
    wb = openpyxl.load_workbook(target_wb, data_only=True)
    shifts = [
        ("POS1 (S1)", "POS 1 - Shift 1"),
        ("POS1 (S2)", "POS 1 - Shift 2"),
        ("POS2 (S1)", "POS 2 - Shift 1"),
        ("POS2 (S2)", "POS 2 - Shift 2"),
        ("POS3 (S1)", "POS 3 - Shift 1"),
        ("POS3 (S2)", "POS 3 - Shift 2"),
        ("OPT", "OPT Terminal"),
    ]
    
    tot_sales = 0.0
    tot_pass = 0.0
    tot_pay = 0.0
    
    for sheet_name, display_label in shifts:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            cashier = str(ws.cell(4, 3).value or "-").strip()
            sales = sum([ws.cell(r, 5).value or 0 for r in range(9, 25) if isinstance(ws.cell(r, 5).value, (int, float))])
            pass_thru = sum([ws.cell(r, 5).value or 0 for r in range(30, 34) if isinstance(ws.cell(r, 5).value, (int, float))])
            payments = sum([ws.cell(r, 8).value or 0 for r in range(9, 55) if isinstance(ws.cell(r, 8).value, (int, float))])
            var = payments - (sales + pass_thru)
            
            is_active = (sales > 0 or payments > 0 or (cashier != "-" and cashier != ""))
            if is_active:
                tot_sales += sales
                tot_pass += pass_thru
                tot_pay += payments
                status = "[BALANCED 0.00]" if abs(var) < 0.01 else f"[VARIANCE {var:+.2f}]"
                print(f"{display_label:<16} {cashier:<14} {sales:>10.2f}  {pass_thru:>10.2f}  {payments:>10.2f}  {status}")
            else:
                print(f"{display_label:<16} {'-':<14} {'0.00':>10}  {'0.00':>10}  {'0.00':>10}  [INACTIVE]")
            
    print("-" * 75)
    tot_var = tot_pay - (tot_sales + tot_pass)
    print(f"{'TOTAL':<16} {'Active Shifts':<14} {tot_sales:>10.2f}  {tot_pass:>10.2f}  {tot_pay:>10.2f}  {'[BALANCED 0.00]' if abs(tot_var) < 0.01 else f'[ERR {tot_var:+.2f}]'}")
    print("-" * 75)

if __name__ == "__main__":
    main()
