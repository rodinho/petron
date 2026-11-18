import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import openpyxl

from process_closure import run_consolidation

class PetronTillClosureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Petron Grand Saga - Till Closure Manager (2 Shifts per POS)")
        self.root.geometry("980x760")
        self.root.minsize(920, 680)
        
        # Color palette
        self.bg_color = "#F4F6F9"
        self.primary_blue = "#002B49"  # Petron Navy
        self.petron_red = "#E31837"    # Petron Red
        self.card_bg = "#FFFFFF"
        self.border_color = "#D1D5DB"
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.folder_path = tk.StringVar(value=os.path.abspath("input_files/02") if os.path.exists("input_files/02") else os.path.abspath("input_files"))
        
        # Shift variables
        self.pos1_s1_path = tk.StringVar(value="")
        self.pos1_s2_path = tk.StringVar(value="")
        self.pos2_s1_path = tk.StringVar(value="")
        self.pos2_s2_path = tk.StringVar(value="")
        self.pos3_s1_path = tk.StringVar(value="")
        self.pos3_s2_path = tk.StringVar(value="")
        self.opt_path = tk.StringVar(value="")
        self.teraju_path = tk.StringVar(value="")
        self.der_path = tk.StringVar(value="")
        
        self.status_var = tk.StringVar(value="Ready. Choose files or click 'Consolidate & Generate'.")
        
        self.setup_ui()
        
        # Auto-detect from initial folder
        self.auto_detect_from_folder(self.folder_path.get())
        self.refresh_summary_table()

    def clear_all_inputs(self):
        self.pos1_s1_path.set("")
        self.pos1_s2_path.set("")
        self.pos2_s1_path.set("")
        self.pos2_s2_path.set("")
        self.pos3_s1_path.set("")
        self.pos3_s2_path.set("")
        self.opt_path.set("")
        self.teraju_path.set("")
        self.der_path.set("")
        self.status_var.set("Inputs cleared.")

    def auto_detect_from_folder(self, folder):
        if not folder or not os.path.exists(folder):
            return
        
        self.clear_all_inputs()
        files = os.listdir(folder)
        
        for f in files:
            full_path = os.path.abspath(os.path.join(folder, f))
            if os.path.isdir(full_path):
                continue
            
            f_upper = f.upper()

            # Master DER / Day End Report
            if ("DER" in f_upper or "DAY END" in f_upper) and f_upper.endswith(".PDF"):
                if not self.der_path.get():
                    self.der_path.set(full_path)
            
            # Teraju / Invoice
            elif "TERAJU" in f_upper or "RECEIVABLE" in f_upper or "INVOICE" in f_upper:
                if not self.teraju_path.get() and (f_upper.endswith(".CSV") or f_upper.endswith(".XLSX")):
                    self.teraju_path.set(full_path)

            # OPT
            elif "OPT" in f_upper:
                if not self.opt_path.get() and f_upper.endswith(".PDF"):
                    self.opt_path.set(full_path)

            # POS 1
            elif "POS 1" in f_upper or "POS1" in f_upper or "POS_1" in f_upper:
                if "SHIFT 1" in f_upper or "S1" in f_upper:
                    self.pos1_s1_path.set(full_path)
                elif "SHIFT 2" in f_upper or "S2" in f_upper:
                    self.pos1_s2_path.set(full_path)
                elif "EOD" in f_upper:
                    if not self.pos1_s1_path.get():
                        self.pos1_s1_path.set(full_path)

            # POS 2
            elif "POS 2" in f_upper or "POS2" in f_upper or "POS_2" in f_upper:
                if "SHIFT 1" in f_upper or "S1" in f_upper:
                    self.pos2_s1_path.set(full_path)
                elif "SHIFT 2" in f_upper or "S2" in f_upper:
                    self.pos2_s2_path.set(full_path)
                elif "EOD" in f_upper:
                    if not self.pos2_s1_path.get():
                        self.pos2_s1_path.set(full_path)
                    elif not self.pos2_s2_path.get():
                        self.pos2_s2_path.set(full_path)

            # POS 3
            elif "POS 3" in f_upper or "POS3" in f_upper or "POS_3" in f_upper:
                if "SHIFT 1" in f_upper or "S1" in f_upper:
                    self.pos3_s1_path.set(full_path)
                elif "SHIFT 2" in f_upper or "S2" in f_upper:
                    self.pos3_s2_path.set(full_path)
                elif "EOD" in f_upper:
                    if not self.pos3_s1_path.get():
                        self.pos3_s1_path.set(full_path)
                    elif not self.pos3_s2_path.get():
                        self.pos3_s2_path.set(full_path)

        self.status_var.set(f"Loaded files from: {os.path.basename(folder)}")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_path.get() or "input_files")
        if folder:
            self.folder_path.set(folder)
            self.auto_detect_from_folder(folder)

    def setup_ui(self):
        header = tk.Frame(self.root, bg=self.primary_blue, height=75)
        header.pack(fill="x", side="top")
        
        title_label = tk.Label(
            header, 
            text="PETRON GRAND SAGA NORTHBOUND", 
            fg="#FFFFFF", 
            bg=self.primary_blue, 
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(anchor="w", padx=25, pady=(10, 2))
        
        subtitle_label = tk.Label(
            header, 
            text="Daily Till Closure Consolidation System (2 Shifts per POS + OPT Reconciliation)", 
            fg="#93C5FD", 
            bg=self.primary_blue, 
            font=("Segoe UI", 9)
        )
        subtitle_label.pack(anchor="w", padx=25, pady=(0, 10))
        
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=18, pady=10)
        main_frame.pack(fill="both", expand=True)

        # File Selection Card
        file_card = tk.LabelFrame(
            main_frame, 
            text=" 1. Source Files Input (2 Shifts per POS Terminal) ", 
            font=("Segoe UI", 10, "bold"),
            bg=self.card_bg, 
            fg=self.primary_blue, 
            padx=12, 
            pady=8,
            relief="solid",
            bd=1
        )
        file_card.pack(fill="x", pady=(0, 10))

        # Folder Quick-Bar
        fbar = tk.Frame(file_card, bg=self.card_bg)
        fbar.pack(fill="x", pady=(0, 8))
        
        lbl_f = tk.Label(fbar, text="Folder / Day:", bg=self.card_bg, fg="#374151", font=("Segoe UI", 9, "bold"))
        lbl_f.pack(side="left", padx=(0, 6))
        
        entry_f = tk.Entry(fbar, textvariable=self.folder_path, width=45, font=("Segoe UI", 9), relief="solid", bd=1)
        entry_f.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        btn_bf = tk.Button(
            fbar, 
            text="📁 Browse Folder...", 
            font=("Segoe UI", 8, "bold"), 
            bg="#E5E7EB", 
            relief="flat", 
            padx=8, 
            pady=2,
            command=self.browse_folder
        )
        btn_bf.pack(side="left", padx=2)

        btn_detect = tk.Button(
            fbar, 
            text="🔄 Auto-Detect", 
            font=("Segoe UI", 8), 
            bg="#E5E7EB", 
            relief="flat", 
            padx=8, 
            pady=2,
            command=lambda: self.auto_detect_from_folder(self.folder_path.get())
        )
        btn_detect.pack(side="left", padx=2)

        btn_clear = tk.Button(
            fbar, 
            text="🗑️ Clear", 
            font=("Segoe UI", 8), 
            bg="#FEE2E2", 
            fg="#991B1B",
            relief="flat", 
            padx=6, 
            pady=2,
            command=self.clear_all_inputs
        )
        btn_clear.pack(side="left", padx=2)

        # 2-Column Grid for Shifts
        grid_frame = tk.Frame(file_card, bg=self.card_bg)
        grid_frame.pack(fill="x")
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(4, weight=1)

        # Left Column: Shift 1
        self.create_grid_input(grid_frame, 0, 0, "POS 1 - Shift 1:", self.pos1_s1_path, [("PDF/TXT", "*.pdf;*.txt")])
        self.create_grid_input(grid_frame, 1, 0, "POS 2 - Shift 1:", self.pos2_s1_path, [("PDF/TXT", "*.pdf;*.txt")])
        self.create_grid_input(grid_frame, 2, 0, "POS 3 - Shift 1:", self.pos3_s1_path, [("PDF/TXT", "*.pdf;*.txt")])
        self.create_grid_input(grid_frame, 3, 0, "OPT Terminal:", self.opt_path, [("PDF/TXT", "*.pdf;*.txt")])

        # Right Column: Shift 2 & Invoices
        self.create_grid_input(grid_frame, 0, 3, "POS 1 - Shift 2:", self.pos1_s2_path, [("PDF/TXT", "*.pdf;*.txt")])
        self.create_grid_input(grid_frame, 1, 3, "POS 2 - Shift 2:", self.pos2_s2_path, [("PDF/TXT", "*.pdf;*.txt")])
        self.create_grid_input(grid_frame, 2, 3, "POS 3 - Shift 2:", self.pos3_s2_path, [("PDF/TXT", "*.pdf;*.txt")])
        self.create_grid_input(grid_frame, 3, 3, "Teraju / E-Pay (CSV):", self.teraju_path, [("CSV/Excel", "*.csv;*.xlsx")])

        # Row 4: Master DER
        self.create_grid_input(grid_frame, 4, 0, "Day End Report (DER):", self.der_path, [("PDF", "*.pdf")])
        der_info = tk.Label(
            grid_frame,
            text="* Master BOS audit file (auto-cross checks all tills, fuels, tenders & subsidies)",
            bg=self.card_bg,
            fg="#6B7280",
            font=("Segoe UI", 8, "italic")
        )
        der_info.grid(row=4, column=3, columnspan=3, sticky="w", padx=6, pady=3)

        # Action Buttons Frame
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=(0, 10))

        self.btn_run = tk.Button(
            btn_frame, 
            text="⚡ Consolidate & Generate Both Closures", 
            bg=self.petron_red, 
            fg="#FFFFFF", 
            font=("Segoe UI", 11, "bold"),
            padx=14, 
            pady=7, 
            relief="flat",
            cursor="hand2",
            activebackground="#C1122C",
            activeforeground="#FFFFFF",
            command=self.process_consolidation
        )
        self.btn_run.pack(side="left")

        self.btn_verify_der = tk.Button(
            btn_frame, 
            text="🔍 Verify vs DER", 
            bg="#D97706", 
            fg="#FFFFFF", 
            font=("Segoe UI", 10, "bold"),
            padx=12, 
            pady=7, 
            relief="flat",
            cursor="hand2",
            activebackground="#B45309",
            activeforeground="#FFFFFF",
            command=self.show_der_verification_dialog
        )
        self.btn_verify_der.pack(side="left", padx=(8, 0))

        self.btn_open_shifts = tk.Button(
            btn_frame, 
            text="📊 Shift Breakdown (.xlsx)", 
            bg="#0284C7", 
            fg="#FFFFFF", 
            font=("Segoe UI", 10, "bold"),
            padx=12, 
            pady=7, 
            relief="flat",
            cursor="hand2",
            activebackground="#0369A1",
            activeforeground="#FFFFFF",
            command=self.open_shifts_excel_file
        )
        self.btn_open_shifts.pack(side="left", padx=(8, 0))

        self.btn_open_pos = tk.Button(
            btn_frame, 
            text="📋 POS Summary (.xlsx)", 
            bg="#4F46E5", 
            fg="#FFFFFF", 
            font=("Segoe UI", 10, "bold"),
            padx=12, 
            pady=7, 
            relief="flat",
            cursor="hand2",
            activebackground="#4338CA",
            activeforeground="#FFFFFF",
            command=self.open_pos_summary_excel_file
        )
        self.btn_open_pos.pack(side="left", padx=(8, 0))

        self.btn_open_dash = tk.Button(
            btn_frame, 
            text="🌐 Dashboard", 
            bg="#0F766E", 
            fg="#FFFFFF", 
            font=("Segoe UI", 10, "bold"),
            padx=12, 
            pady=7, 
            relief="flat",
            cursor="hand2",
            activebackground="#115E59",
            activeforeground="#FFFFFF",
            command=self.open_html_dashboard
        )
        self.btn_open_dash.pack(side="left", padx=(8, 0))

        # Status & Summary Card
        summary_card = tk.LabelFrame(
            main_frame, 
            text=" 2. Consolidated Reconciliation Status (Dynamic Cashiers & Shifts) ", 
            font=("Segoe UI", 10, "bold"),
            bg=self.card_bg, 
            fg=self.primary_blue, 
            padx=12, 
            pady=10,
            relief="solid",
            bd=1
        )
        summary_card.pack(fill="both", expand=True)

        columns = ("till", "cashier", "sales", "passthru", "payments", "variance", "status")
        self.tree = ttk.Treeview(summary_card, columns=columns, show="headings", height=8)
        
        self.tree.heading("till", text="Till / Shift")
        self.tree.heading("cashier", text="Cashier")
        self.tree.heading("sales", text="Products Sold (RM)")
        self.tree.heading("passthru", text="Pass-thru E-Pay (RM)")
        self.tree.heading("payments", text="Payments (RM)")
        self.tree.heading("variance", text="Variance (RM)")
        self.tree.heading("status", text="Reconciliation Status")
        
        self.tree.column("till", width=120, anchor="center")
        self.tree.column("cashier", width=120, anchor="w")
        self.tree.column("sales", width=130, anchor="e")
        self.tree.column("passthru", width=140, anchor="e")
        self.tree.column("payments", width=130, anchor="e")
        self.tree.column("variance", width=110, anchor="center")
        self.tree.column("status", width=150, anchor="center")
        
        self.tree.pack(fill="both", expand=True, pady=(0, 5))

        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bg="#E5E7EB", 
            fg="#1F2937", 
            font=("Segoe UI", 9), 
            anchor="w", 
            padx=15, 
            pady=5
        )
        status_bar.pack(fill="x", side="bottom")

    def create_grid_input(self, parent, row, col_start, label_text, str_var, filetypes):
        lbl = tk.Label(parent, text=label_text, bg=self.card_bg, fg="#374151", font=("Segoe UI", 9), anchor="w")
        lbl.grid(row=row, column=col_start, sticky="w", padx=(6, 4), pady=2)
        
        entry = tk.Entry(parent, textvariable=str_var, font=("Segoe UI", 9), relief="solid", bd=1)
        entry.grid(row=row, column=col_start+1, sticky="ew", padx=2, pady=2)
        
        btn = tk.Button(
            parent, 
            text="...", 
            font=("Segoe UI", 8, "bold"),
            bg="#E5E7EB",
            relief="flat",
            padx=6,
            pady=1,
            command=lambda: self.browse_file(str_var, filetypes)
        )
        btn.grid(row=row, column=col_start+2, padx=(2, 10), pady=2)

    def browse_file(self, str_var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            str_var.set(path)

    def process_consolidation(self):
        try:
            self.status_var.set("Processing selected till and shift files...")
            self.root.update_idletasks()
            
            p1_s1 = self.pos1_s1_path.get().strip()
            p1_s2 = self.pos1_s2_path.get().strip()
            p2_s1 = self.pos2_s1_path.get().strip()
            p2_s2 = self.pos2_s2_path.get().strip()
            p3_s1 = self.pos3_s1_path.get().strip()
            p3_s2 = self.pos3_s2_path.get().strip()
            opt = self.opt_path.get().strip()
            teraju = self.teraju_path.get().strip()
            der = self.der_path.get().strip()
            
            pos_map, der_comp = run_consolidation(
                pos1_s1_path=p1_s1,
                pos1_s2_path=p1_s2,
                pos2_s1_path=p2_s1,
                pos2_s2_path=p2_s2,
                pos3_s1_path=p3_s1,
                pos3_s2_path=p3_s2,
                opt_path=opt,
                teraju_path=teraju,
                der_path=der,
                output_wb="petron-till-closure.xlsx"
            )
            
            self.refresh_summary_table()
            active_list = []
            if p1_s1: active_list.append("POS 1 (S1)")
            if p1_s2: active_list.append("POS 1 (S2)")
            if p2_s1: active_list.append("POS 2 (S1)")
            if p2_s2: active_list.append("POS 2 (S2)")
            if p3_s1: active_list.append("POS 3 (S1)")
            if p3_s2: active_list.append("POS 3 (S2)")
            if opt: active_list.append("OPT")
            
            der_msg = ""
            if der_comp:
                match_count = sum(1 for d in der_comp.values() if d["match"])
                der_msg = f"\n\nDER Audit: {match_count}/{len(der_comp)} metrics reconciled with Day End Report."

            msg = (
                f"Consolidation complete!\n\n"
                f"Both closure files generated:\n"
                f" 1. Shift Breakdown: petron-till-closure.xlsx\n"
                f" 2. POS Summary: petron-till-closure-pos-summary.xlsx\n\n"
                f"Active shifts: {', '.join(active_list) if active_list else 'None'}.{der_msg}"
            )
            self.status_var.set("Done! Both closure files generated successfully.")
            messagebox.showinfo("Success", msg)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate closure:\n{str(e)}")

    def show_der_verification_dialog(self):
        der = self.der_path.get().strip()
        if not der or not os.path.exists(der):
            # Try to auto-find in folder
            folder = self.folder_path.get()
            if folder and os.path.exists(folder):
                for f in os.listdir(folder):
                    f_up = f.upper()
                    if ("DER" in f_up or "DAY END" in f_up) and f_up.endswith(".PDF"):
                        der = os.path.join(folder, f)
                        self.der_path.set(der)
                        break
                        
        if not der or not os.path.exists(der):
            messagebox.showwarning("DER Missing", "Please select or place a Day End Report (DER) PDF to perform reconciliation.")
            return

        try:
            from parse_inputs import parse_full_der_summary
            from process_closure import get_parsed_data_for_shifts, compare_pos_with_der

            pos_map, b_date = get_parsed_data_for_shifts(
                pos1_s1_path=self.pos1_s1_path.get(),
                pos1_s2_path=self.pos1_s2_path.get(),
                pos2_s1_path=self.pos2_s1_path.get(),
                pos2_s2_path=self.pos2_s2_path.get(),
                pos3_s1_path=self.pos3_s1_path.get(),
                pos3_s2_path=self.pos3_s2_path.get(),
                opt_path=self.opt_path.get(),
                teraju_path=self.teraju_path.get(),
                der_path=der
            )
            der_sum = parse_full_der_summary(der)
            comp = compare_pos_with_der(pos_map, der_sum)

            # Verification Modal Window
            win = tk.Toplevel(self.root)
            win.title(f"DER Cross-Check Audit - {der_sum.get('business_date', b_date)}")
            win.geometry("780x440")
            win.minsize(700, 380)
            win.configure(bg="#F9FAFB")

            header = tk.Frame(win, bg=self.primary_blue, pady=12, padx=16)
            header.pack(fill="x")
            
            tk.Label(
                header,
                text="DAY END REPORT (DER) vs ALL POS AUDIT",
                fg="#FFFFFF",
                bg=self.primary_blue,
                font=("Segoe UI", 12, "bold")
            ).pack(anchor="w")

            tk.Label(
                header,
                text=f"Station Site: 304194  |  Business Date: {der_sum.get('business_date', b_date)}  |  Source: {os.path.basename(der)}",
                fg="#93C5FD",
                bg=self.primary_blue,
                font=("Segoe UI", 9)
            ).pack(anchor="w", pady=(2, 0))

            card = tk.Frame(win, bg="#FFFFFF", padx=16, pady=12, bd=1, relief="solid")
            card.pack(fill="both", expand=True, padx=16, pady=12)

            cols = ("metric", "pos", "der", "diff", "status")
            tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
            tree.heading("metric", text="Reconciliation Metric")
            tree.heading("pos", text="All POS Sum")
            tree.heading("der", text="DER Master Report")
            tree.heading("diff", text="Variance (Delta)")
            tree.heading("status", text="Audit Status")

            tree.column("metric", width=180, anchor="w")
            tree.column("pos", width=130, anchor="e")
            tree.column("der", width=130, anchor="e")
            tree.column("diff", width=110, anchor="e")
            tree.column("status", width=130, anchor="center")

            for metric, data in comp.items():
                p_val = f"RM {data['pos']:,.2f}" if "Litres" not in metric else f"{data['pos']:,.3f} L"
                d_val = f"RM {data['der']:,.2f}" if "Litres" not in metric else f"{data['der']:,.3f} L"
                diff_val = f"RM {data['diff']:+,.2f}" if "Litres" not in metric else f"{data['diff']:+,.3f} L"
                st = "BALANCED" if data["match"] else "VARIANCE"
                tree.insert("", "end", values=(metric, p_val, d_val, diff_val, st))

            tree.pack(fill="both", expand=True)

            btn_box = tk.Frame(win, bg="#F9FAFB", pady=8)
            btn_box.pack(fill="x", padx=16)

            tk.Button(
                btn_box,
                text="Close",
                font=("Segoe UI", 9, "bold"),
                bg="#E5E7EB",
                padx=16,
                pady=4,
                relief="flat",
                command=win.destroy
            ).pack(side="right")

        except Exception as e:
            messagebox.showerror("Audit Error", f"Failed to parse DER summary:\n{str(e)}")

    def refresh_summary_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        target_file = "petron-till-closure.xlsx"
        if not os.path.exists(target_file):
            return
            
        try:
            wb = openpyxl.load_workbook(target_file, data_only=True)
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
                        status_text = "BALANCED" if abs(var) < 0.01 else f"ERR ({var:+.2f})"
                        self.tree.insert("", "end", values=(
                            display_label, 
                            cashier, 
                            f"{sales:,.2f}", 
                            f"{pass_thru:,.2f}", 
                            f"{payments:,.2f}", 
                            f"{var:,.2f}", 
                            status_text
                        ))
                    else:
                        self.tree.insert("", "end", values=(
                            display_label, 
                            "-", 
                            "0.00", 
                            "0.00", 
                            "0.00", 
                            "0.00", 
                            "[NO FILE / INACTIVE]"
                        ))
            
            tot_var = tot_pay - (tot_sales + tot_pass)
            self.tree.insert("", "end", values=(
                "TOTAL", 
                "Active Tills", 
                f"{tot_sales:,.2f}", 
                f"{tot_pass:,.2f}", 
                f"{tot_pay:,.2f}", 
                f"{tot_var:,.2f}", 
                "BALANCED" if abs(tot_var) < 0.01 else f"ERR ({tot_var:+.2f})"
            ))
        except Exception as e:
            print("Table refresh error:", e)

    def open_shifts_excel_file(self):
        target = os.path.abspath("petron-till-closure.xlsx")
        if not os.path.exists(target):
            target = os.path.abspath("petron-till-closure-shifts.xlsx")
        if os.path.exists(target):
            os.startfile(target)
        else:
            messagebox.showwarning("File Missing", "Shift breakdown closure has not been generated yet.")

    def open_pos_summary_excel_file(self):
        target = os.path.abspath("petron-till-closure-pos-summary.xlsx")
        if os.path.exists(target):
            os.startfile(target)
        else:
            messagebox.showwarning("File Missing", "petron-till-closure-pos-summary.xlsx has not been generated yet.")

    def open_excel_file(self):
        self.open_pos_summary_excel_file()

    def open_html_dashboard(self):
        target = os.path.abspath("petron_dashboard.html")
        if os.path.exists(target):
            os.startfile(target)
        else:
            messagebox.showwarning("File Missing", "petron_dashboard.html has not been generated yet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PetronTillClosureApp(root)
    root.mainloop()
