import os

day3_block = '''    if b_date == "03/09/2026":
        # POS 1 - Shift 1 (from End Shift Report Shift 1 Pos 1 20260903)
        if (pos1_s1_path and os.path.exists(pos1_s1_path)) or (base_dir and os.path.exists(os.path.join(base_dir, "End Shift Report Shift 1 Pos 1 20260903.pdf"))):
            p1_file = pos1_s1_path if (pos1_s1_path and os.path.exists(pos1_s1_path)) else os.path.join(base_dir, "End Shift Report Shift 1 Pos 1 20260903.pdf")
            c_name = detect_cashier_from_pdf(p1_file, default_cashier="GIASSUDDIN")
            pos_data_map["POS1 (S1)"] = {
                "till_id": "1 - POS1",
                "type": "POS",
                "cashier": c_name,
                "time_from": "03/09/2026 00:01",
                "time_to": "03/09/2026 06:41",
                "products": {
                    "Blaze 95": {"qty": 675.363, "price": 3.770, "total": 2546.12},
                    "Cash rounding": {"qty": None, "price": None, "total": 0.08},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 2029.15,
                    "Credit card": 0.00,
                    "Manual Mastercard": 50.00,
                    "MyDebit": 221.00,
                    "TNG QR": 246.05,
                }
            }

        # POS 1 - Shift 2 (from End Shift Report Shift 2 Pos 1 20260903)
        if (pos1_s2_path and os.path.exists(pos1_s2_path)) or (base_dir and os.path.exists(os.path.join(base_dir, "End Shift Report Shift 2 Pos 1 20260903.pdf"))):
            p1_s2_file = pos1_s2_path if (pos1_s2_path and os.path.exists(pos1_s2_path)) else os.path.join(base_dir, "End Shift Report Shift 2 Pos 1 20260903.pdf")
            c_name = detect_cashier_from_pdf(p1_s2_file, default_cashier="KAWSAR / IQHMAL")
            pos_data_map["POS1 (S2)"] = {
                "till_id": "1 - POS1",
                "type": "POS",
                "cashier": c_name,
                "time_from": "03/09/2026 07:06",
                "time_to": "03/09/2026 23:58",
                "products": {
                    "Blaze 95": {"qty": 3877.745, "price": 3.770, "total": 14619.10},
                    "Merchandise refund (negative)": {"qty": None, "price": None, "total": -400.00},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 7264.50,
                    "Credit card": 0.00,
                    "Manual Visa": 461.45,
                    "Manual Mastercard": 136.00,
                    "MyDebit": 3195.95,
                    "Fleet card": 150.00,
                    "TNG": 1407.00,
                    "MBB QRPay": 394.55,
                    "ShopeePay": 153.60,
                    "TNG QR": 246.05,
                    "Station credit": 700.00,
                    "RM20 Fuel (1600 pts)": 20.00,
                    "RM45 Fuel (3000 pts)": 90.00,
                }
            }

        # POS 2 - Shift 1 (from DER Summary)
        if (pos2_s1_path and os.path.exists(pos2_s1_path)) or der_path:
            pos_data_map["POS2 (S1)"] = {
                "till_id": "2 - POS2",
                "type": "POS",
                "cashier": "WINA / KAWSAR / IQHMAL / IEQA",
                "time_from": "03/09/2026 06:12",
                "time_to": "03/09/2026 17:03",
                "products": {
                    "Blaze 95": {"qty": 2174.629, "price": 3.770, "total": 8198.35},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 4442.05,
                    "Credit card": 0.00,
                    "Manual Visa": 87.60,
                    "MyDebit": 1384.75,
                    "TNG": 927.00,
                    "MBB QRPay": 1197.80,
                    "ShopeePay": 69.15,
                    "RM45 Fuel (3000 pts)": 90.00,
                }
            }

        # POS 2 - Shift 2 (from DER Summary)
        if (pos2_s2_path and os.path.exists(pos2_s2_path)) or der_path:
            pos_data_map["POS2 (S2)"] = {
                "till_id": "2 - POS2",
                "type": "POS",
                "cashier": "KAOSAR / IQHMAL",
                "time_from": "03/09/2026 17:08",
                "time_to": "03/09/2026 23:48",
                "products": {
                    "Blaze 95": {"qty": 1057.334, "price": 3.770, "total": 3986.15},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 2880.20,
                    "Credit card": 0.00,
                    "Manual Visa": 96.50,
                    "MyDebit": 700.00,
                    "TNG QR": 309.45,
                }
            }

        # POS 3 - Shift 1 (from DER Summary)
        if (pos3_s1_path and os.path.exists(pos3_s1_path)) or der_path:
            pos_data_map["POS3 (S1)"] = {
                "till_id": "3 - POS3",
                "type": "POS",
                "cashier": "GIASSUDDIN / KAOSAR / WINA",
                "time_from": "03/09/2026 06:48",
                "time_to": "03/09/2026 22:46",
                "products": {
                    "Blaze 95": {"qty": 3405.809, "price": 3.770, "total": 12839.90},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 8564.30,
                    "Credit card": 0.00,
                    "Manual Visa": 796.35,
                    "Manual Mastercard": 118.73,
                    "MyDebit": 2161.07,
                    "TNG": 363.20,
                    "MBB QRPay": 322.50,
                    "ShopeePay": 458.75,
                    "RM5 Fuel (450 pts)": 10.00,
                    "RM45 Fuel (3000 pts)": 45.00,
                }
            }

        # OPT (Unattended Self-Service)
        if (opt_path and os.path.exists(opt_path)) or (base_dir and os.path.exists(os.path.join(base_dir, "OPT Sales Report 20260903.pdf"))):
            p_opt = opt_path if (opt_path and os.path.exists(opt_path)) else os.path.join(base_dir, "OPT Sales Report 20260903.pdf")
            c_name = detect_cashier_from_pdf(p_opt, default_cashier="FAREEZ")
            pos_data_map["OPT"] = {
                "till_id": "1 - POS1 (OPT)",
                "type": "OPT",
                "cashier": c_name,
                "time_from": "03/09/2026 00:00",
                "time_to": "03/09/2026 23:59",
                "products": {
                    "Blaze 95": {"qty": 4630.103, "price": 3.770, "total": 17455.49},
                    "Blaze 97": {"qty": 5.661, "price": 4.250, "total": 24.06},
                    "Diesel Max Euro 5": {"qty": 1548.640, "price": 4.670, "total": 7232.15},
                    "Turbo Diesel Euro 5": {"qty": 241.715, "price": 4.870, "total": 1177.15},
                },
                "pass_through": {},
                "payments": {
                    "Credit card": 7414.73,
                    "MyDebit": 11225.27,
                    "Fleet card": 7248.85,
                }
            }'''

with open('process_closure.py', 'r', encoding='utf-8') as f:
    text = f.read()

m1 = 'DAY 03 DATA DEFINITIONS'
m2 = 'DAY 02 DATA DEFINITIONS'
i1 = text.find(m1)
i2 = text.find(m2)

start_idx = text.find('\n', i1) + 1
start_idx = text.find('\n', start_idx) + 1

new_text = text[:start_idx] + day3_block + '\n\n    # ==========================================\n    ' + text[i2:]
with open('process_closure.py', 'w', encoding='utf-8') as f:
    f.write(new_text)
print("Updated Day 03 in process_closure.py successfully!")
