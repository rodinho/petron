import openpyxl

for fname in ['petron-till-closure.xlsx', 'petron-till-closure-shifts.xlsx', 'petron-till-closure-pos-summary.xlsx', 'petron-till-closure-pos-summary_updated.xlsx', 'petron-till-closure_updated.xlsx']:
    try:
        wb = openpyxl.load_workbook(fname, data_only=True)
        print('==================================================')
        print('FILE:', fname)
        for sname in wb.sheetnames:
            ws = wb[sname]
            if sname == 'Day summary':
                print(f'  [{sname}]')
                for r in range(7, 16):
                    c1 = ws.cell(r, 1).value
                    c3 = ws.cell(r, 3).value
                    c5 = ws.cell(r, 5).value
                    c6 = ws.cell(r, 6).value
                    if c1:
                        print(f'    {c1:<20} Sales={c3!r:<12} Payments={c5!r:<12} Variance={c6!r}')
            elif 'POS1' in sname:
                print(f'  [{sname}] Till={ws.cell(2, 3).value}, Cashier={ws.cell(4, 3).value}')
                print(f'    Cash={ws.cell(10, 8).value}, Visa={ws.cell(15, 8).value}, Master={ws.cell(16, 8).value}, MyDebit={ws.cell(13, 8).value}, Fleet={ws.cell(14, 8).value}')
                print(f'    TNG={ws.cell(20, 8).value}, TNG QR={ws.cell(21, 8).value}, MBB QRPay={ws.cell(25, 8).value}, GrabPay={ws.cell(23, 8).value}, Shopee={ws.cell(24, 8).value}')
                print(f'    Total Sales(E25)={ws.cell(25, 5).value}, Pass-thru(E34)={ws.cell(34, 5).value}, Total Payments(H55)={ws.cell(55, 8).value}, Variance(H57)={ws.cell(57, 8).value}')
    except Exception as e:
        print(f'Error on {fname}: {e}')
