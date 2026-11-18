import os
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Styles
font_family = "Segoe UI"
header_font = Font(name=font_family, size=11, bold=True, color="FFFFFF")
section_font = Font(name=font_family, size=10, bold=True, color="1F497D")
title_font = Font(name=font_family, size=14, bold=True, color="002060")
bold_font = Font(name=font_family, size=10, bold=True)
regular_font = Font(name=font_family, size=10)
small_italic_font = Font(name=font_family, size=8, italic=True, color="595959")

# Fills
navy_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
gray_header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
light_blue_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
total_fill = PatternFill(start_color="EBF1F5", end_color="EBF1F5", fill_type="solid")

# Borders
thin_side = Side(style='thin', color='D9D9D9')
med_top_side = Side(style='thin', color='000000')
double_bottom_side = Side(style='double', color='000000')

cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
total_border = Border(top=med_top_side, bottom=double_bottom_side)


def build_till_sheet(ws, till_id, till_type, cashier, time_from, time_to, data):
    ws.views.sheetView[0].showGridLines = True

    ws["A1"] = "TILL CLOSURE"
    ws["A1"].font = title_font

    headers_info = [
        ("Till no / POS ID", till_id),
        ("Type (POS / OPT)", till_type),
        ("Cashier", cashier),
        ("Time from", time_from),
        ("Time to", time_to),
    ]
    for idx, (label, val) in enumerate(headers_info, start=2):
        ws[f"B{idx}"] = label
        ws[f"B{idx}"].font = bold_font
        ws[f"C{idx}"] = val
        ws[f"C{idx}"].font = regular_font
        ws[f"C{idx}"].fill = yellow_fill

    # Left Side Header: PRODUCTS SOLD (Row 8)
    ws["A8"] = "#"
    ws["B8"] = "Product"
    ws["C8"] = "Quantity (L / units)"
    ws["D8"] = "Unit price"
    ws["E8"] = "Total (RM)"
    for c in ["A8", "B8", "C8", "D8", "E8"]:
        ws[c].font = header_font
        ws[c].fill = navy_fill
        ws[c].alignment = Alignment(horizontal="center", vertical="center")

    # Right Side Header: PAYMENTS RECEIVED (Row 8)
    ws["G8"] = "Account"
    ws["H8"] = "Amount (RM)"
    for c in ["G8", "H8"]:
        ws[c].font = header_font
        ws[c].fill = navy_fill
        ws[c].alignment = Alignment(horizontal="center", vertical="center")

    products = [
        (1, "Blaze 95"),
        (2, "Blaze 97"),
        (3, "Blaze 100"),
        (4, "Diesel Max Euro 5"),
        (5, "Turbo Diesel Euro 5"),
        (6, "Fuel refund (enter litres as negative)"),
        (7, "Pump test (returned to tank)"),
        (8, "Shop - Tobacco"),
        (9, "Shop - Food"),
        (10, "Shop - Others"),
        (11, "Shop - Dealer item"),
        (12, "Merchandise refund (negative)"),
        (13, "Cash rounding"),
        (14, ""),
        (15, ""),
        (16, "")
    ]

    p_dict = (data or {}).get("products", {})
    for r_idx, (num, name) in enumerate(products, start=9):
        ws[f"A{r_idx}"] = num
        ws[f"A{r_idx}"].alignment = Alignment(horizontal="center")
        ws[f"B{r_idx}"] = name

        for col in ["A", "B", "C", "D", "E"]:
            ws[f"{col}{r_idx}"].border = cell_border

        ws[f"C{r_idx}"].number_format = '#,##0.000'
        ws[f"D{r_idx}"].number_format = '#,##0.00'
        ws[f"E{r_idx}"].number_format = '#,##0.00'

        ws[f"C{r_idx}"].fill = yellow_fill
        ws[f"D{r_idx}"].fill = yellow_fill
        ws[f"E{r_idx}"].fill = yellow_fill

        p_data = p_dict.get(name)
        if p_data:
            if "qty" in p_data and p_data["qty"] is not None:
                ws[f"C{r_idx}"] = p_data["qty"]
            if "price" in p_data and p_data["price"] is not None:
                ws[f"D{r_idx}"] = p_data["price"]
            if "total" in p_data and p_data["total"] is not None:
                ws[f"E{r_idx}"] = p_data["total"]

    # Row 25: TOTAL SALES
    ws["B25"] = "TOTAL SALES"
    ws["B25"].font = bold_font
    ws["E25"] = "=SUM(E9:E24)"
    ws["E25"].font = bold_font
    ws["E25"].fill = total_fill
    ws["E25"].border = total_border
    ws["E25"].number_format = '#,##0.00'

    # Row 26: Fuel Litres total
    ws["B26"] = "(Quantity total = fuel litres incl. refund and pump test)"
    ws["B26"].font = small_italic_font
    ws["C26"] = "=SUM(C9:C15)"
    ws["C26"].font = bold_font
    ws["C26"].number_format = '#,##0.000'

    # Row 28: PASS-THROUGH
    ws["A28"] = "PASS-THROUGH (non-sales)"
    ws["A28"].font = section_font

    ws["A29"] = "#"
    ws["B29"] = "Category"
    ws["C29"] = "Count"
    ws["E29"] = "Total (RM)"
    for c in ["A29", "B29", "C29", "E29"]:
        ws[c].font = header_font
        ws[c].fill = navy_fill
        ws[c].alignment = Alignment(horizontal="center")

    pass_through = [
        (1, "E-Pay - Store services (bill pay / reload)"),
        (2, "E-Pay - Prepaid cards"),
        (3, ""),
        (4, "")
    ]
    pt_dict = (data or {}).get("pass_through", {})
    for r_idx, (num, name) in enumerate(pass_through, start=30):
        ws[f"A{r_idx}"] = num
        ws[f"A{r_idx}"].alignment = Alignment(horizontal="center")
        ws[f"B{r_idx}"] = name
        for col in ["A", "B", "C", "D", "E"]:
            ws[f"{col}{r_idx}"].border = cell_border
        ws[f"C{r_idx}"].fill = yellow_fill
        ws[f"E{r_idx}"].fill = yellow_fill
        ws[f"E{r_idx}"].number_format = '#,##0.00'

        pt_data = pt_dict.get(name)
        if pt_data:
            if "count" in pt_data and pt_data["count"] is not None:
                ws[f"C{r_idx}"] = pt_data["count"]
            if "total" in pt_data and pt_data["total"] is not None:
                ws[f"E{r_idx}"] = pt_data["total"]

    # Row 34: TOTAL PASS-THROUGH
    ws["B34"] = "TOTAL PASS-THROUGH"
    ws["B34"].font = bold_font
    ws["E34"] = "=SUM(E30:E33)"
    ws["E34"].font = bold_font
    ws["E34"].fill = total_fill
    ws["E34"].border = total_border
    ws["E34"].number_format = '#,##0.00'

    # Row 35: TOTAL SALES + PASS-THROUGH
    ws["B35"] = "TOTAL SALES + PASS-THROUGH"
    ws["B35"].font = bold_font
    ws["E35"] = "=E25+E34"
    ws["E35"].font = bold_font
    ws["E35"].fill = light_blue_fill
    ws["E35"].border = total_border
    ws["E35"].number_format = '#,##0.00'

    # Right Side: Payments Received (Rows 9 to 52)
    payments_structure = [
        ("CASH", True),
        ("   Cash", False),
        ("CARDS", True),
        ("   Credit card", False),
        ("   MyDebit", False),
        ("   Fleet card", False),
        ("   Manual Visa", False),
        ("   Manual Mastercard", False),
        ("   Manual Amex", False),
        ("   Manual MyDebit", False),
        ("E-WALLET / QR", True),
        ("   TNG", False),
        ("   TNG QR", False),
        ("   Boost", False),
        ("   GrabPay", False),
        ("   ShopeePay", False),
        ("   MBB QRPay", False),
        ("   WeChat Pay", False),
        ("   Alipay", False),
        ("   VCash", False),
        ("   MCash", False),
        ("   UPI QR", False),
        ("   MBSB QRPay", False),
        ("CREDIT & REDEMPTION", True),
        ("   Station credit", False),
        ("   RM5 Fuel (450 pts)", False),
        ("   RM20 Fuel (1600 pts)", False),
        ("   RM45 Fuel (3000 pts)", False),
        ("   RM1 Mart (100 pts)", False),
        ("   Open redemptions", False),
        ("   Promotion discount voucher", False),
        ("   PMA voucher", False),
        ("   Good Kredit", False),
        ("   Manual charge", False),
        ("OTHER", True),
        ("   Pump test", False),
        ("   Drive off", False),
        ("   Unclaimed refund", False),
        ("SUBSIDY (paid by the government)", True),
        ("   BUDI95", False),
        ("   BUDI Diesel", False),
        ("   SKDS", False),
        ("   SKPS", False),
        ("   ADO", False),
    ]

    pay_dict = (data or {}).get("payments", {})
    val_rows = []
    for offset, (name, is_header) in enumerate(payments_structure):
        r = 9 + offset
        ws[f"G{r}"] = name
        ws[f"G{r}"].border = cell_border
        ws[f"H{r}"].border = cell_border
        ws[f"H{r}"].number_format = '#,##0.00'

        if is_header:
            ws[f"G{r}"].font = section_font
            ws[f"G{r}"].fill = gray_header_fill
            ws[f"H{r}"].fill = gray_header_fill
        else:
            ws[f"G{r}"].font = regular_font
            ws[f"H{r}"].fill = yellow_fill
            val_rows.append(r)
            clean_name = name.strip()
            if clean_name in pay_dict:
                val = pay_dict[clean_name]
                if val is not None and val != 0:
                    ws[f"H{r}"] = val

    for r in [53, 54]:
        ws[f"G{r}"].border = cell_border
        ws[f"H{r}"].border = cell_border
        ws[f"H{r}"].fill = yellow_fill
        val_rows.append(r)

    # Row 55: TOTAL PAYMENTS RECEIVED
    ws["G55"] = "TOTAL PAYMENTS RECEIVED"
    ws["G55"].font = bold_font
    val_sum_formula = f"=SUM({','.join([f'H{r}' for r in val_rows[:15]])})+SUM({','.join([f'H{r}' for r in val_rows[15:30]])})+SUM({','.join([f'H{r}' for r in val_rows[30:]])})"
    ws["H55"] = val_sum_formula
    ws["H55"].font = bold_font
    ws["H55"].fill = light_blue_fill
    ws["H55"].border = total_border
    ws["H55"].number_format = '#,##0.00'

    # Row 57: VARIANCE
    ws["G57"] = "VARIANCE (payments - sales)"
    ws["G57"].font = bold_font
    ws["H57"] = "=H55-E35"
    ws["H57"].font = bold_font
    ws["H57"].fill = total_fill
    ws["H57"].border = total_border
    ws["H57"].number_format = '#,##0.00'

    ws["G58"] = "Should be 0.00. If not, check the figures against the printed closure."
    ws["G58"].font = small_italic_font

    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 38
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 16
    ws.column_dimensions['F'].width = 4
    ws.column_dimensions['G'].width = 34
    ws.column_dimensions['H'].width = 16


def aggregate_pos_shifts(pos_data_map):
    """
    Combines Shift 1 and Shift 2 for each POS into a single per-POS record:
    - POS1 = POS1 (S1) + POS1 (S2)
    - POS2 = POS2 (S1) + POS2 (S2)
    - POS3 = POS3 (S1) + POS3 (S2)
    - OPT  = OPT
    """
    aggregated = {}
    pos_keys = [
        ("POS1", ["POS1 (S1)", "POS1 (S2)"], "1 - POS1"),
        ("POS2", ["POS2 (S1)", "POS2 (S2)"], "2 - POS2"),
        ("POS3", ["POS3 (S1)", "POS3 (S2)"], "3 - POS3"),
    ]
    for pos_name, shift_keys, till_id in pos_keys:
        shifts = [pos_data_map.get(k) for k in shift_keys if pos_data_map.get(k)]
        if not shifts:
            aggregated[pos_name] = {
                "till_id": till_id,
                "type": "POS",
                "cashier": "-",
                "time_from": "",
                "time_to": "",
                "products": {},
                "pass_through": {},
                "payments": {}
            }
            continue
        
        # Cashier string
        cashiers = [s.get("cashier") for s in shifts if s.get("cashier") and s.get("cashier") != "-"]
        unique_cashiers = []
        for c in cashiers:
            if c not in unique_cashiers:
                unique_cashiers.append(c)
        cashier_str = " / ".join(unique_cashiers) if unique_cashiers else "-"

        time_from = shifts[0].get("time_from", "")
        time_to = shifts[-1].get("time_to", "")

        # Combine products
        comb_products = {}
        for s in shifts:
            for p_name, p_info in s.get("products", {}).items():
                if not isinstance(p_info, dict):
                    continue
                if p_name not in comb_products:
                    comb_products[p_name] = {
                        "qty": p_info.get("qty"),
                        "price": p_info.get("price"),
                        "total": p_info.get("total")
                    }
                else:
                    cur = comb_products[p_name]
                    if p_info.get("qty") is not None:
                        cur["qty"] = (cur["qty"] or 0.0) + p_info["qty"]
                    if p_info.get("price") is not None and cur.get("price") is None:
                        cur["price"] = p_info["price"]
                    if p_info.get("total") is not None:
                        cur["total"] = (cur["total"] or 0.0) + p_info["total"]

        # Combine pass-through
        comb_pass = {}
        for s in shifts:
            for pt_name, pt_info in s.get("pass_through", {}).items():
                if not isinstance(pt_info, dict):
                    continue
                if pt_name not in comb_pass:
                    comb_pass[pt_name] = {
                        "count": pt_info.get("count"),
                        "total": pt_info.get("total")
                    }
                else:
                    cur = comb_pass[pt_name]
                    if pt_info.get("count") is not None:
                        cur["count"] = (cur["count"] or 0) + pt_info["count"]
                    if pt_info.get("total") is not None:
                        cur["total"] = (cur["total"] or 0.0) + pt_info["total"]

        # Combine payments
        comb_payments = {}
        for s in shifts:
            for pay_name, pay_amt in s.get("payments", {}).items():
                if pay_amt is not None:
                    comb_payments[pay_name] = comb_payments.get(pay_name, 0.0) + pay_amt

        aggregated[pos_name] = {
            "till_id": till_id,
            "type": "POS",
            "cashier": cashier_str,
            "time_from": time_from,
            "time_to": time_to,
            "products": comb_products,
            "pass_through": comb_pass,
            "payments": comb_payments
        }

    # OPT terminal
    opt_data = pos_data_map.get("OPT")
    if opt_data:
        aggregated["OPT"] = opt_data
    else:
        aggregated["OPT"] = {
            "till_id": "1 - POS1 (OPT)",
            "type": "OPT",
            "cashier": "-",
            "time_from": "",
            "time_to": "",
            "products": {},
            "pass_through": {},
            "payments": {}
        }

    return aggregated



def create_dynamic_till_closure(
    output_filename="petron-till-closure.xlsx",
    site_no="304194",
    site_name="PETRON GRAND SAGA NORTHBOUND",
    business_date="02/09/2026",
    pos_data_map=None
):
    """
    Creates the consolidated Petron Till Closure Excel workbook supporting
    2 shifts per POS terminal:
      - POS1 (S1) and POS1 (S2)
      - POS2 (S1) and POS2 (S2)
      - POS3 (S1) and POS3 (S2)
      - OPT
      - Day summary (reconciling all active shifts)
    """
    if pos_data_map is None:
        pos_data_map = {}

    wb = openpyxl.Workbook()
    default_sheet = wb.active

    # 1. DAY SUMMARY SHEET
    ws_sum = wb.create_sheet(title="Day summary")
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = f"{site_name} - DAY SUMMARY"
    ws_sum["A1"].font = title_font

    ws_sum["A3"] = "Site no:"
    ws_sum["B3"] = site_no
    ws_sum["A4"] = "Site name:"
    ws_sum["B4"] = site_name
    ws_sum["A5"] = "Business date:"
    ws_sum["B5"] = business_date
    for r in range(3, 6):
        ws_sum[f"A{r}"].font = bold_font
        ws_sum[f"B{r}"].font = regular_font

    sum_headers = ["Till / Shift", "Cashier", "Sales (RM)", "Pass-through (RM)", "Payments (RM)", "Variance (RM)", "Fuel litres"]
    for col_idx, h in enumerate(sum_headers, start=1):
        cell = ws_sum.cell(row=7, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    shifts_list = [
        ("POS1 (S1)", "POS 1 - Shift 1"),
        ("POS1 (S2)", "POS 1 - Shift 2"),
        ("POS2 (S1)", "POS 2 - Shift 1"),
        ("POS2 (S2)", "POS 2 - Shift 2"),
        ("POS3 (S1)", "POS 3 - Shift 1"),
        ("POS3 (S2)", "POS 3 - Shift 2"),
        ("OPT", "OPT Terminal"),
    ]

    for idx, (sheet_title, display_label) in enumerate(shifts_list, start=8):
        ws_sum.cell(row=idx, column=1, value=display_label).font = bold_font
        
        cashier_cell = ws_sum.cell(row=idx, column=2, value=f"='{sheet_title}'!C4")
        cashier_cell.font = regular_font

        ws_sum.cell(row=idx, column=3, value=f"='{sheet_title}'!E25").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=4, value=f"='{sheet_title}'!E34").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=5, value=f"='{sheet_title}'!H55").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=6, value=f"='{sheet_title}'!H57").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=7, value=f"='{sheet_title}'!C26").number_format = '#,##0.000'

        for c in range(1, 8):
            ws_sum.cell(row=idx, column=c).border = cell_border

    # TOTAL row on summary (Row 15: sums rows 8 to 14)
    ws_sum.cell(row=15, column=1, value="TOTAL").font = bold_font
    for c in range(3, 8):
        col_let = get_column_letter(c)
        tot_cell = ws_sum.cell(row=15, column=c, value=f"=SUM({col_let}8:{col_let}14)")
        tot_cell.font = bold_font
        tot_cell.fill = total_fill
        tot_cell.border = total_border
        tot_cell.number_format = '#,##0.00' if c != 7 else '#,##0.000'

    for col_letter, width in zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], [20, 18, 16, 18, 16, 16, 16]):
        ws_sum.column_dimensions[col_letter].width = width

    # Create sheets for each shift
    for sheet_title, display_label in shifts_list:
        ws = wb.create_sheet(title=sheet_title)
        cdata = pos_data_map.get(sheet_title)
        if cdata:
            build_till_sheet(
                ws, 
                cdata.get("till_id", sheet_title), 
                cdata.get("type", "POS"), 
                cdata.get("cashier", "-"), 
                cdata.get("time_from", f"{business_date} 00:00"), 
                cdata.get("time_to", f"{business_date} 23:59"), 
                cdata
            )
        else:
            build_till_sheet(
                ws, 
                sheet_title, 
                "OPT" if "OPT" in sheet_title else "POS", 
                "-", 
                "", 
                "", 
                {"products": {}, "pass_through": {}, "payments": {}}
            )

    if default_sheet.title in wb.sheetnames and len(wb.sheetnames) > 1:
        wb.remove(default_sheet)

    try:
        wb.save(output_filename)
    except PermissionError:
        alt_filename = output_filename.replace('.xlsx', '_updated.xlsx')
        try:
            wb.save(alt_filename)
        except Exception:
            pass
        raise PermissionError(
            f"'{output_filename}' is currently open in Microsoft Excel. "
            f"Please close the file in Excel and click 'Consolidate & Generate' again.\n"
            f"(A temporary backup copy has been saved to '{alt_filename}')."
        )
    return output_filename



def create_consolidated_pos_till_closure(
    output_filename="petron-till-closure-pos-summary.xlsx",
    site_no="304194",
    site_name="PETRON GRAND SAGA NORTHBOUND",
    business_date="02/09/2026",
    pos_data_map=None
):
    """
    Creates the consolidated Petron Till Closure Excel workbook without shift breakdown
    (just one POS total up):
      - POS1 (aggregated total for POS1)
      - POS2 (aggregated total for POS2)
      - POS3 (aggregated total for POS3)
      - OPT  (OPT terminal)
      - Day summary (reconciling POS1, POS2, POS3, OPT)
    """
    if pos_data_map is None:
        pos_data_map = {}

    if any("(S" in k for k in pos_data_map.keys()):
        agg_map = aggregate_pos_shifts(pos_data_map)
    else:
        agg_map = pos_data_map

    wb = openpyxl.Workbook()
    default_sheet = wb.active

    # 1. DAY SUMMARY SHEET
    ws_sum = wb.create_sheet(title="Day summary")
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = f"{site_name} - DAY SUMMARY"
    ws_sum["A1"].font = title_font

    ws_sum["A3"] = "Site no:"
    ws_sum["B3"] = site_no
    ws_sum["A4"] = "Site name:"
    ws_sum["B4"] = site_name
    ws_sum["A5"] = "Business date:"
    ws_sum["B5"] = business_date
    for r in range(3, 6):
        ws_sum[f"A{r}"].font = bold_font
        ws_sum[f"B{r}"].font = regular_font

    sum_headers = ["Till", "Cashier", "Sales (RM)", "Pass-through (RM)", "Payments (RM)", "Variance (RM)", "Fuel litres"]
    for col_idx, h in enumerate(sum_headers, start=1):
        cell = ws_sum.cell(row=7, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    tills_list = [
        ("POS1", "POS 1"),
        ("POS2", "POS 2"),
        ("POS3", "POS 3"),
        ("OPT", "OPT Terminal"),
    ]

    for idx, (sheet_title, display_label) in enumerate(tills_list, start=8):
        ws_sum.cell(row=idx, column=1, value=display_label).font = bold_font
        
        cashier_cell = ws_sum.cell(row=idx, column=2, value=f"='{sheet_title}'!C4")
        cashier_cell.font = regular_font

        ws_sum.cell(row=idx, column=3, value=f"='{sheet_title}'!E25").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=4, value=f"='{sheet_title}'!E34").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=5, value=f"='{sheet_title}'!H55").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=6, value=f"='{sheet_title}'!H57").number_format = '#,##0.00'
        ws_sum.cell(row=idx, column=7, value=f"='{sheet_title}'!C26").number_format = '#,##0.000'

        for c in range(1, 8):
            ws_sum.cell(row=idx, column=c).border = cell_border

    # TOTAL row on summary (Row 12: sums rows 8 to 11)
    ws_sum.cell(row=12, column=1, value="TOTAL").font = bold_font
    for c in range(3, 8):
        col_let = get_column_letter(c)
        tot_cell = ws_sum.cell(row=12, column=c, value=f"=SUM({col_let}8:{col_let}11)")
        tot_cell.font = bold_font
        tot_cell.fill = total_fill
        tot_cell.border = total_border
        tot_cell.number_format = '#,##0.00' if c != 7 else '#,##0.000'

    for col_letter, width in zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], [20, 18, 16, 18, 16, 16, 16]):
        ws_sum.column_dimensions[col_letter].width = width

    # Create sheets for each POS terminal
    for sheet_title, display_label in tills_list:
        ws = wb.create_sheet(title=sheet_title)
        cdata = agg_map.get(sheet_title)
        if cdata:
            build_till_sheet(
                ws, 
                cdata.get("till_id", sheet_title), 
                cdata.get("type", "POS"), 
                cdata.get("cashier", "-"), 
                cdata.get("time_from", f"{business_date} 00:00"), 
                cdata.get("time_to", f"{business_date} 23:59"), 
                cdata
            )
        else:
            build_till_sheet(
                ws, 
                sheet_title, 
                "OPT" if "OPT" in sheet_title else "POS", 
                "-", 
                "", 
                "", 
                {"products": {}, "pass_through": {}, "payments": {}}
            )

    if default_sheet.title in wb.sheetnames and len(wb.sheetnames) > 1:
        wb.remove(default_sheet)

    try:
        wb.save(output_filename)
    except PermissionError:
        alt_filename = output_filename.replace('.xlsx', '_updated.xlsx')
        try:
            wb.save(alt_filename)
        except Exception:
            pass
        raise PermissionError(
            f"'{output_filename}' is currently open in Microsoft Excel. "
            f"Please close the file in Excel and click 'Consolidate & Generate' again.\n"
            f"(A temporary backup copy has been saved to '{alt_filename}')."
        )
    return output_filename

