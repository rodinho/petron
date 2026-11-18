import os
import sys
import re
import glob
import time
from datetime import datetime
from collections import Counter
import openpyxl
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\User\Documents\petron"
profile_dir = os.path.join(base_dir, "browser_profile")
base_input_dir = os.path.join(base_dir, "input_files")


def parse_date_arg(arg):
    arg = arg.strip().lower()
    if arg == "all":
        return "all", None
    if "/" in arg:
        parts = arg.split("/")
        day = parts[0].zfill(2)
        month = parts[1].zfill(2) if len(parts) > 1 else "09"
        year = parts[2] if len(parts) > 2 else "2026"
        if len(year) == 2:
            year = "20" + year
        return f"{year}-{month}-{day}", day
    clean = arg.replace("-", "")
    if len(clean) == 8 and clean.isdigit():
        return f"{clean[:4]}-{clean[4:6]}-{clean[6:]}", clean[6:]
    if clean.isdigit() and len(clean) <= 2:
        day = clean.zfill(2)
        return f"2026-09-{day}", day
    return None, None


def load_g4s_drops(folder_day):
    """Read verified cash deposits from Device Transactions - G4S *.xlsx for the day."""
    folder_path = os.path.join(base_input_dir, folder_day)
    if not os.path.exists(folder_path):
        return []

    g4s_files = sorted(glob.glob(os.path.join(folder_path, "*G4S*.xlsx")))
    if not g4s_files:
        return []

    drops = []
    for filepath in g4s_files:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws = wb.active

        # Locate header row containing 'Card Name' and 'Amount'
        header_row_idx = None
        col_map = {}
        for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if not row:
                continue
            row_strs = [str(c).strip() if c is not None else "" for c in row]
            if "Card Name" in row_strs and "Amount" in row_strs:
                header_row_idx = r_idx
                for c_idx, name in enumerate(row_strs):
                    if name:
                        col_map[name] = c_idx
                break

        if header_row_idx is None:
            # Fallback to standard G4S layout
            col_map = {
                "Transaction ID": 0,
                "Transaction Description": 6,
                "Card Name": 11,
                "Transaction Date": 13,
                "Amount": 16,
            }
            header_row_idx = 11

        idx_tx = col_map.get("Transaction ID", 0)
        idx_desc = col_map.get("Transaction Description", 6)
        idx_card = col_map.get("Card Name", 11)
        idx_dt = col_map.get("Transaction Date", 13)
        idx_amt = col_map.get("Amount", 16)

        for row in ws.iter_rows(min_row=header_row_idx + 1, values_only=True):
            if not row or len(row) <= idx_amt:
                continue
            amt_raw = row[idx_amt]
            if not isinstance(amt_raw, (int, float)) or amt_raw <= 0:
                continue

            desc = str(row[idx_desc] or "").strip()
            if desc and "deposit" not in desc.lower():
                continue

            card_name = str(row[idx_card] or "").strip()
            m_pos = re.search(r'(\d+)', card_name)
            if not m_pos:
                continue
            pos = m_pos.group(1)

            dt_val = row[idx_dt]
            if isinstance(dt_val, datetime):
                dt = dt_val
            elif isinstance(dt_val, str):
                try:
                    dt = datetime.fromisoformat(dt_val.strip())
                except ValueError:
                    continue
            else:
                continue

            drops.append({
                "tx_id": str(row[idx_tx] or "").strip(),
                "pos": pos,
                "dt": dt,
                "time_str": dt.strftime("%Y-%m-%dT%H:%M"),
                "amount": round(float(amt_raw), 2),
                "source_file": os.path.basename(filepath),
            })

    drops.sort(key=lambda d: (int(d["pos"]), d["dt"]))
    return drops


def load_cash_clearing_date(page, date_str):
    """Navigate reliably to Cash clearing for date_str, handling Blazor SignalR warmup & reconnects."""
    target_url = f"https://petron.myhiro.my/finances/clearing/cash?date={date_str}"
    if "/finances/clearing/cash" not in page.url or f"date={date_str}" in page.url:
        page.goto("https://petron.myhiro.my/finances/clearing/cash", wait_until="domcontentloaded")
        time.sleep(3)

    for attempt in range(2):
        page.goto(target_url, wait_until="domcontentloaded")
        for _ in range(35):
            time.sleep(1)
            txt = page.locator("body").inner_text()
            if "lost its connection" in txt.lower() or "reload now" in txt.lower():
                reload_btn = page.locator('button:has-text("Reload now")')
                if reload_btn.count() > 0 and reload_btn.first.is_visible():
                    print("  [Notice] Blazor disconnected, clicking Reload now...", flush=True)
                    reload_btn.first.click()
                    time.sleep(3)
                    continue
            if "Loading..." not in txt and (
                "handed over" in txt
                or "No till" in txt
                or "Please complete" in txt
            ):
                time.sleep(1.5)
                return True
        if attempt == 0:
            print(f"  [Notice] Retrying Cash clearing page load for {date_str}...", flush=True)
            page.goto("https://petron.myhiro.my/finances/clearing/cash", wait_until="domcontentloaded")
            time.sleep(3)
    return False


def get_existing_tills(page, date_str):
    """Extract existing till codes (e.g. 20260901-P1S1) listed on Cash clearing page."""
    prefix = date_str.replace("-", "")
    body_text = page.locator("body").inner_text()
    tills = []
    seen = set()
    for match in re.finditer(rf'({prefix}-P(\d+)S(\d+))', body_text):
        code, pos, shift = match.group(1), match.group(2), match.group(3)
        if code not in seen:
            seen.add(code)
            tills.append({"code": code, "pos": pos, "shift": shift})
    return tills


def assign_drops_to_tills(drops, tills):
    """Map G4S drops to the available MyHiro tills by POS and timestamp/shift."""
    tills_by_pos = {}
    for t in tills:
        tills_by_pos.setdefault(t["pos"], []).append(t)

    for pos in tills_by_pos:
        tills_by_pos[pos].sort(key=lambda t: int(t["shift"]))

    assigned = {t["code"]: [] for t in tills}
    unmatched = []

    for d in drops:
        pos = d["pos"]
        candidates = tills_by_pos.get(pos, [])
        if not candidates:
            unmatched.append(d)
            continue
        if len(candidates) == 1:
            assigned[candidates[0]["code"]].append(d)
            continue

        # Multiple shifts exist for this POS
        shift_map = {t["shift"]: t["code"] for t in candidates}
        hour = d["dt"].hour
        if "3" in shift_map:
            if 7 <= hour < 15:
                target_shift = "1"
            elif 15 <= hour < 23:
                target_shift = "2"
            else:
                target_shift = "3"
            target_code = shift_map.get(target_shift, candidates[0]["code"])
        else:
            # 2 shifts (S1 / S2): before 15:00 -> S1, 15:00+ -> S2
            target_shift = "1" if hour < 15 else "2"
            target_code = shift_map.get(target_shift, candidates[-1]["code"])
        assigned[target_code].append(d)

    return assigned, unmatched


def get_existing_drop_amounts(page):
    """Read already-recorded Safe drop amounts in the currently opened till."""
    amounts = []
    rows = page.locator('tr:has-text("Safe drop")')
    for i in range(rows.count()):
        row_txt = rows.nth(i).inner_text()
        nums = re.findall(r'([\d,]+\.\d{2})', row_txt)
        if nums:
            # First numeric column is Initial amount
            amounts.append(round(float(nums[0].replace(",", "")), 2))
    return Counter(amounts)


def add_single_drop(page, drop, accepted_by):
    """Open the Cash drop modal and submit one G4S drop."""
    add_drop_btn = page.locator('button:has-text("Add drop")').first
    add_drop_btn.click()
    time.sleep(0.5)

    new_drop_item = page.locator('.dropdown-menu.show :text("Add new drop")')
    new_drop_item.wait_for(state="visible", timeout=5000)
    new_drop_item.click()

    dialog = page.locator('#cash-drop-dialog')
    dialog.wait_for(state="visible", timeout=8000)
    time.sleep(0.5)

    # Cashier: keep default unless empty
    cashier_inp = dialog.locator('#cdd-cashier')
    if not cashier_inp.input_value().strip():
        cashier_inp.fill("Owner hazieqaf98")
        cashier_inp.dispatch_event("change")

    # Accepted by *
    acc_inp = dialog.locator('#cdd-accepted')
    acc_inp.fill(accepted_by)
    acc_inp.dispatch_event("change")
    time.sleep(0.2)

    # Time (best-effort)
    time_inp = dialog.locator('#cdd-time')
    if time_inp.count() > 0:
        time_inp.fill(drop["time_str"])
        time_inp.dispatch_event("change")

    # Amount * & Actual amount *
    amt_str = f"{drop['amount']:.2f}"
    amt_inp = dialog.locator('#cdd-amount')
    amt_inp.fill(amt_str)
    amt_inp.dispatch_event("change")
    time.sleep(0.2)

    act_inp = dialog.locator('#cdd-actual')
    act_inp.fill(amt_str)
    act_inp.dispatch_event("change")
    act_inp.press("Tab")
    time.sleep(0.4)

    submit_btn = page.locator('.modal:visible button:has-text("Add drop")').last
    if submit_btn.get_attribute("disabled") is not None:
        print(f"    [Warning] Add drop button remained disabled for RM {amt_str}. Cancelling modal.", flush=True)
        cancel_btn = page.locator('.modal:visible button:has-text("Cancel")').last
        cancel_btn.click()
        time.sleep(0.5)
        return False

    submit_btn.click()
    try:
        dialog.wait_for(state="detached", timeout=10000)
    except Exception:
        time.sleep(1.5)
    time.sleep(1.0)
    return True


def save_opened_till(page, till_code, on_short="cancel"):
    """Click 'Confirm all drops and save' (if enabled) or 'Save till'."""
    save_btn = page.locator('button:has-text("Save till")').first
    if save_btn.count() == 0:
        print(f"    [Warning] Save till button not found for {till_code}.", flush=True)
        return False

    # Try split-button arrow -> "Confirm all drops and save" only if enabled
    split_arrow = save_btn.locator('..').locator('button').nth(1)
    if split_arrow.count() > 0 and split_arrow.is_visible() and split_arrow.get_attribute("disabled") is None:
        split_arrow.click()
        time.sleep(0.5)
        confirm_save = page.locator('.dropdown-menu.show :text("Confirm all drops and save")')
        if (
            confirm_save.count() > 0
            and confirm_save.first.is_visible()
            and confirm_save.first.get_attribute("disabled") is None
        ):
            confirm_save.first.click()
            time.sleep(2.5)
        else:
            split_arrow.click()
            time.sleep(0.3)
            if save_btn.get_attribute("disabled") is None:
                save_btn.click()
                time.sleep(2.5)
            else:
                print(f"    [Notice] Save till button disabled for {till_code} (already saved).", flush=True)
                return True
    elif save_btn.get_attribute("disabled") is None:
        save_btn.click()
        time.sleep(2.5)
    else:
        print(f"    [Notice] Save till button disabled for {till_code} (already saved).", flush=True)
        return True

    # Check if shortage penalty modal (#cashier-shortage-dialog) appeared
    short_dlg = page.locator('dialog[open]:has(#cashier-shortage-dialog)')
    if short_dlg.count() > 0:
        short_txt = short_dlg.first.inner_text().splitlines()[1] if len(short_dlg.first.inner_text().splitlines()) > 1 else "Shortage detected"
        if on_short == "ignore":
            btn = short_dlg.first.locator('button:has-text("Ignore")')
            if btn.count() > 0:
                btn.first.click()
                time.sleep(2.5)
                print(f"    Saved till {till_code} (posted shortage to expenses: {short_txt}).", flush=True)
                return True
        elif on_short == "charge":
            btn = short_dlg.first.locator('button:has-text("Charge")')
            if btn.count() > 0:
                btn.first.click()
                time.sleep(2.5)
                print(f"    Saved till {till_code} (charged shortage to cashier: {short_txt}).", flush=True)
                return True
        # Default safe mode: cancel penalty dialog so drops stay Confirmed without false expense/salary deduction
        cancel_el = short_dlg.first.locator('a:has-text("Cancel"), button:has-text("Cancel")')
        if cancel_el.count() > 0:
            cancel_el.first.click()
            time.sleep(1.5)
        print(
            f"    [HOLD SAVE] Till {till_code} has a shortfall dialog ({short_txt}). "
            f"All drops are Saved & Confirmed; cancelled penalty modal (use --on-short ignore/charge to settle).",
            flush=True
        )
        return False

    print(f"    Saved till {till_code} successfully!", flush=True)
    return True


def process_cash_clearing_date(page, date_str, folder_day, accepted_by, on_short="cancel"):
    drops = load_g4s_drops(folder_day)
    print("\n========================================================", flush=True)
    print(f"Processing Cash Clearing for Date: {date_str} (Folder: {folder_day})", flush=True)
    print(f"Accepted by: {accepted_by}", flush=True)
    print(f"Found {len(drops)} G4S verified cash drops (Total RM {sum(d['amount'] for d in drops):,.2f})", flush=True)
    print("========================================================", flush=True)

    if not drops:
        print(f"No G4S cash drop Excel found in input_files/{folder_day}. Skipping.", flush=True)
        return

    ok = load_cash_clearing_date(page, date_str)
    if not ok:
        print(f"[Error] Could not load Cash Clearing page for {date_str}.", flush=True)
        return

    tills = get_existing_tills(page, date_str)
    if not tills:
        print(f"[Warning] No tills posted on Cash Clearing for {date_str}. Run Sales Clearing first.", flush=True)
        return

    print(f"Found {len(tills)} till(s) on MyHiro: {[t['code'] for t in tills]}", flush=True)
    assigned, unmatched = assign_drops_to_tills(drops, tills)

    if unmatched:
        by_pos = {}
        for d in unmatched:
            by_pos.setdefault(d["pos"], []).append(d)
        for pos, pos_drops in sorted(by_pos.items()):
            pos_sum = sum(x["amount"] for x in pos_drops)
            print(
                f"  [SKIP] POS {pos} has {len(pos_drops)} G4S drops (RM {pos_sum:,.2f}), "
                f"but no POS {pos} till exists in Sales Clearing for {date_str}.",
                flush=True
            )

    for till in tills:
        code = till["code"]
        till_drops = assigned.get(code, [])
        if not till_drops:
            print(f"\n--- Till {code}: 0 G4S drops mapped. Skipping.", flush=True)
            continue

        till_sum = sum(d["amount"] for d in till_drops)
        print(f"\n--- Opening Till {code} ({len(till_drops)} drops, Total RM {till_sum:,.2f}) ---", flush=True)

        # Open till via row click (or Switch till dropdown if another till is already open)
        visible_row = page.locator(f'text={code}').locator('visible=true')
        if visible_row.count() > 0:
            visible_row.first.click()
            time.sleep(2.5)
        else:
            switch_btn = page.locator('button[data-test="select-till-button"], button:has-text("Switch till")')
            if switch_btn.count() > 0 and switch_btn.first.is_visible():
                switch_btn.first.click()
                time.sleep(0.8)
                opt = page.locator(f'button[data-test="{code}"], .sc-till-menu.show :text("{code}")').first
                opt.click()
                time.sleep(2.5)
            else:
                print(f"  [Error] Could not open till {code}.", flush=True)
                continue

        existing_counts = get_existing_drop_amounts(page)
        if existing_counts:
            print(f"  Existing drops on {code}: {dict(existing_counts)}", flush=True)

        added_count = 0
        for idx, d in enumerate(till_drops, start=1):
            amt = d["amount"]
            if existing_counts[amt] > 0:
                existing_counts[amt] -= 1
                print(f"  [{idx}/{len(till_drops)}] [SKIP] Drop RM {amt:,.2f} ({d['time_str']}) already exists.", flush=True)
                continue

            print(f"  [{idx}/{len(till_drops)}] Adding drop RM {amt:,.2f} (G4S {d['dt'].strftime('%H:%M:%S')})...", flush=True)
            if add_single_drop(page, d, accepted_by):
                added_count += 1

        if added_count > 0:
            save_opened_till(page, code, on_short=on_short)
        else:
            print(f"  No new drops added for {code}. Checking save status...", flush=True)
            save_btn = page.locator('button:has-text("Save till")').first
            if save_btn.count() > 0 and save_btn.get_attribute("disabled") is None:
                save_opened_till(page, code, on_short=on_short)

    # Reload date summary for clean screenshot
    load_cash_clearing_date(page, date_str)
    os.makedirs(os.path.join(base_dir, "scratch"), exist_ok=True)
    ss_path = os.path.join(base_dir, "scratch", f"cash_clearing_{date_str.replace('-', '')}_done.png")
    page.screenshot(path=ss_path, full_page=True)
    print(f"\nScreenshot saved to: {ss_path}", flush=True)


def main():
    dates = [
        ("2026-09-01", "01"),
        ("2026-09-02", "02"),
        ("2026-09-03", "03"),
        ("2026-09-04", "04"),
        ("2026-09-05", "05"),
        ("2026-09-06", "06"),
        ("2026-09-07", "07"),
    ]
    accepted_by = "Owner hazieqaf98"
    on_short = "cancel"

    raw_args = sys.argv[1:]
    positional = []
    i = 0
    while i < len(raw_args):
        a = raw_args[i].strip()
        if a == "--on-short" and i + 1 < len(raw_args):
            val = raw_args[i + 1].strip().lower()
            if val in ("cancel", "ignore", "charge"):
                on_short = val
            i += 2
            continue
        if a == "--accepted-by" and i + 1 < len(raw_args):
            accepted_by = raw_args[i + 1].strip()
            i += 2
            continue
        positional.append(a)
        i += 1

    if positional:
        parsed_date, parsed_day = parse_date_arg(positional[0])
        if parsed_date and parsed_date != "all":
            dates = [(parsed_date, parsed_day)]
        if len(positional) > 1 and positional[1].strip():
            accepted_by = " ".join(positional[1:]).strip()

    print("========================================================", flush=True)
    print("         PETRON CASH CLEARING DROP AUTOMATION           ", flush=True)
    print("========================================================", flush=True)
    print(f"Target Dates : {[d[0] for d in dates]}", flush=True)
    print(f"Accepted By  : {accepted_by}", flush=True)
    print(f"On Shortfall : {on_short}", flush=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            ignore_default_args=["--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        for date_str, folder_day in dates:
            process_cash_clearing_date(page, date_str, folder_day, accepted_by, on_short=on_short)

        context.close()

    print("\nAll target dates processed successfully!", flush=True)


if __name__ == "__main__":
    main()
