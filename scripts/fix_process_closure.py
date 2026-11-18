pos2_pos3_block = '''        # POS 2 - Shift 1 (from End Shift Report Shift 1 Pos 2 20260902)
        if (pos2_s1_path and os.path.exists(pos2_s1_path)) or (base_dir and os.path.exists(os.path.join(base_dir, "End Shift Report Shift 1 Pos 2 20260902.pdf"))):
            p2_file = pos2_s1_path if (pos2_s1_path and os.path.exists(pos2_s1_path)) else os.path.join(base_dir, "End Shift Report Shift 1 Pos 2 20260902.pdf")
            c_name = detect_cashier_from_pdf(p2_file, default_cashier="AMANI")
            pos_data_map["POS2 (S1)"] = {
                "till_id": "2 - POS2",
                "type": "POS",
                "cashier": c_name,
                "time_from": "02/09/2026 05:18",
                "time_to": "02/09/2026 23:49",
                "products": {
                    "Blaze 95": {"qty": 3036.547, "price": 3.820, "total": 11599.61},
                    "Cash rounding": {"qty": None, "price": None, "total": -0.11},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 5615.90,
                    "Credit card": 0.00,
                    "Manual Visa": 529.85,
                    "Manual Mastercard": 146.30,
                    "Manual Amex": 0.00,
                    "MyDebit": 2126.70,
                    "Fleet card": 1419.85,
                    "TNG": 770.45,
                    "TNG QR": 337.25,
                    "MBB QRPay": 389.00,
                    "GrabPay": 82.00,
                    "ShopeePay": 27.20,
                    "RM20 Fuel (1600 pts)": 20.00,
                    "RM45 Fuel (3000 pts)": 135.00,
                    "BUDI95": 3064.74,
                    "BUDI Diesel": 406.74,
                    "SKDS": 1898.19,
                    "SKPS": 102.98,
                    "ADO": 0.00
                }
            }

        # POS 3 - Shift 1 (from DER Summary)
        if (pos3_s1_path and os.path.exists(pos3_s1_path)) or der_path:
            pos_data_map["POS3 (S1)"] = {
                "till_id": "3 - POS3",
                "type": "POS",
                "cashier": "GIASSUDDIN",
                "time_from": "02/09/2026 06:36",
                "time_to": "02/09/2026 12:47",
                "products": {
                    "Blaze 95": {"qty": 1183.084, "price": 3.820, "total": 4519.38},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 3140.80,
                    "Credit card": 0.00,
                    "Manual Visa": 240.00,
                    "MyDebit": 731.55,
                    "TNG QR": 366.95,
                    "BUDI95": 40.08,
                }
            }

        # POS 3 - Shift 2 (from End Shift Report Shift 2 Pos 3 20260902)
        if (pos3_s2_path and os.path.exists(pos3_s2_path)) or (base_dir and os.path.exists(os.path.join(base_dir, "End Shift Report Shift 2 Pos 3 20260902.pdf"))):
            p3_file = pos3_s2_path if (pos3_s2_path and os.path.exists(pos3_s2_path)) else os.path.join(base_dir, "End Shift Report Shift 2 Pos 3 20260902.pdf")
            c_name = detect_cashier_from_pdf(p3_file, default_cashier="IDRIS")
            pos_data_map["POS3 (S2)"] = {
                "till_id": "3 - POS3",
                "type": "POS",
                "cashier": c_name,
                "time_from": "02/09/2026 12:48",
                "time_to": "02/09/2026 22:47",
                "products": {
                    "Blaze 95": {"qty": 2439.094, "price": 3.820, "total": 9317.34},
                    "Cash rounding": {"qty": None, "price": None, "total": -0.14},
                },
                "pass_through": {},
                "payments": {
                    "Cash": 6531.20,
                    "Credit card": 0.00,
                    "Manual Visa": 104.90,
                    "Manual Mastercard": 135.25,
                    "MyDebit": 1502.60,
                    "TNG QR": 953.25,
                    "RM45 Fuel (3000 pts)": 90.00,
                    "BUDI95": 4722.62,
                    "BUDI Diesel": 193.38,
                    "SKDS": 2346.10,
                    "SKPS": 0.00,
                    "ADO": 0.00
                }
            }'''

with open('process_closure.py', 'r', encoding='utf-8') as f:
    text = f.read()

# First remove all occurrences of the block
clean_text = text.replace('\n' + pos2_pos3_block, '')

# Now insert it ONLY once, right before '# OPT (Unattended Self-Service)' under Day 02
day2_marker = 'elif b_date == "02/09/2026":'
d2_idx = clean_text.find(day2_marker)
opt_marker = '# OPT (Unattended Self-Service)'
opt_idx = clean_text.find(opt_marker, d2_idx)

final_text = clean_text[:opt_idx] + pos2_pos3_block + '\n\n        ' + clean_text[opt_idx:]

with open('process_closure.py', 'w', encoding='utf-8') as f:
    f.write(final_text)

print('Updated process_closure.py successfully!')
