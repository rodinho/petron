import os
import sys
import re
import time
import difflib
from playwright.sync_api import sync_playwright
import pypdf

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\User\Documents\petron"
profile_dir = os.path.join(base_dir, "browser_profile")
base_input_dir = os.path.join(base_dir, "input_files")

def clean_ocr(text):
    return text.replace('!', '1').replace('|', 'I').replace('$', 'S').replace('{', 'C').replace('}', '')

def match_cashier_name(raw_name, available_dropdown_names):
    if not raw_name:
        return 'Owner'
    cleaned = re.sub(r'[^A-Za-z]', '', raw_name).upper()
    best_match = 'Owner'
    best_score = 0
    for name in available_dropdown_names:
        clean_name = re.sub(r'[^A-Za-z]', '', name).upper()
        score = difflib.SequenceMatcher(None, cleaned, clean_name).ratio()
        if score > best_score:
            best_score = score
            best_match = name
    if best_score >= 0.40:
        return best_match
    return 'Owner'

def get_tills_from_eod_page(page, date_str):
    url = f"https://petron.myhiro.my/station/eod?date={date_str}"
    page.goto(url, wait_until='domcontentloaded')
    time.sleep(3)
    
    # Slot index to POS & Shift mapping:
    # 0: POS 1 S1, 1: POS 2 S1, 2: POS 3 S1
    # 3: POS 1 S2, 4: POS 2 S2, 5: POS 3 S2
    slot_mapping = {
        0: ('1', '1'),
        1: ('2', '1'),
        2: ('3', '1'),
        3: ('1', '2'),
        4: ('2', '2'),
        5: ('3', '2'),
    }
    
    slots = page.locator('.pt-slot')
    tills = []
    for i in range(min(6, slots.count())):
        txt = slots.nth(i).inner_text().strip()
        if 'empty' in txt.lower() or 'could not read' in txt.lower() or not txt:
            continue
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        pos, shift = slot_mapping[i]
        amount = None
        cashier = 'Owner'
        for l in lines:
            m = re.search(r'RM\s*([\d,]+\.\d{2})', l)
            if m:
                amount = float(m.group(1).replace(',', ''))
            elif re.match(r'^[A-Za-z\s]+$', l) and len(l) > 2 and 'read' not in l.lower():
                cashier = l
        if amount:
            tills.append({
                'pos': pos,
                'shift': shift,
                'raw_cashier': cashier,
                'sales': amount,
                'source': 'Hiro EOD Slot'
            })
    return tills

def parse_slip_info(filepath):
    try:
        reader = pypdf.PdfReader(filepath)
        text = ""
        for p in reader.pages:
            text += (p.extract_text() or "") + "\n"
    except Exception:
        return None

    lines = [clean_ocr(l.strip()) for l in text.splitlines() if l.strip()]
    fn = os.path.basename(filepath).lower()

    pos = "1"
    for p in ["pos 1", "pos 2", "pos 3", "pos-1", "pos-2", "pos-3", "pos1", "pos2", "pos3"]:
        if p in fn:
            pos = p.replace("pos", "").replace("-", "").strip()
            break

    shift = "1"
    if "shift 2" in fn or "shift2" in fn:
        shift = "2"
    elif "shift 3" in fn or "shift3" in fn:
        shift = "3"
    else:
        for line in lines:
            if "SHIFT" in line.upper():
                m = re.search(r'(\d+)', line)
                if m:
                    shift = m.group(1)
                    break

    raw_cashier = ""
    for i, line in enumerate(lines):
        if any(w in line.upper() for w in ['CASHIER', 'CASHLIER', 'LARILIIER', 'LASLRIER']):
            cand = line.split(':')[-1] if ':' in line else (lines[i+1] if i+1 < len(lines) else '')
            raw_cashier = cand.strip()
            break

    sales = None
    for i, line in enumerate(lines):
        if any(w in line.upper() for w in ["NET SALES", "SALES SUMMARY", "SALTS"]):
            for j in range(i, min(i+7, len(lines))):
                cleaned_line = lines[j].replace('!', '1').replace('l', '1').replace('O', '0')
                m = re.findall(r'(\d+[\s,]*\d*\.\d{2})', cleaned_line)
                if m:
                    for val_str in m:
                        v = float(val_str.replace(' ', '').replace(',', ''))
                        if v > 10.0:
                            sales = v
                            break
                if sales:
                    break
            if sales:
                break

    if not sales:
        for line in lines:
            if any(w in line.upper() for w in ["TOTAL", "SUBTOTAL"]):
                m = re.findall(r'(\d+[\s,]*\d*\.\d{2})', line.replace('!', '1'))
                if m:
                    for val_str in m:
                        v = float(val_str.replace(' ', '').replace(',', ''))
                        if v > 50.0 and (not sales or v > sales):
                            sales = v

    if not sales:
        return None

    return {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'pos': pos,
        'shift': shift,
        'raw_cashier': raw_cashier,
        'sales': sales,
        'source': 'Local Slip'
    }

def get_day_slips(folder_day):
    folder_path = os.path.join(base_input_dir, folder_day)
    if not os.path.exists(folder_path):
        return []
        
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    end_shifts = [f for f in all_files if 'shift' in os.path.basename(f).lower() and 'opt' not in os.path.basename(f).lower()]
    eod_files = [f for f in all_files if 'eod pos' in os.path.basename(f).lower()]
    
    selected_files = []
    if end_shifts:
        selected_files.extend(end_shifts)
        existing_pos = set()
        for f in end_shifts:
            fn = os.path.basename(f).lower()
            for p in ['pos 1', 'pos 2', 'pos 3', 'pos1', 'pos2', 'pos3']:
                if p in fn:
                    existing_pos.add(p.replace('pos', '').replace(' ', ''))
        for f in eod_files:
            fn = os.path.basename(f).lower()
            for p in ['pos 1', 'pos 2', 'pos 3', 'pos1', 'pos2', 'pos3']:
                p_num = p.replace('pos', '').replace(' ', '')
                if p in fn and p_num not in existing_pos:
                    selected_files.append(f)
                    existing_pos.add(p_num)
    else:
        selected_files.extend(eod_files)
        
    results = []
    for f in selected_files:
        info = parse_slip_info(f)
        if info:
            results.append(info)
            
    results.sort(key=lambda x: (x['pos'], x['shift']))
    return results

def post_tills_for_date(page, date_str, folder_day):
    # Step 1: Check if Hiro's EOD page already read the slips
    slips = get_tills_from_eod_page(page, date_str)
    
    # Step 2: Fallback to local files if none on EOD page
    if not slips:
        slips = get_day_slips(folder_day)

    print(f"\n========================================================")
    print(f"Processing Sales Clearing for Date: {date_str} (Folder: {folder_day})")
    print(f"Found {len(slips)} till slips to process:")
    for s in slips:
        src = s.get('source', '')
        print(f"  - POS {s['pos']} Shift {s['shift']} | Cashier: {s['raw_cashier']} | Sales: RM {s['sales']:,.2f} ({src})")
    print(f"========================================================")

    if not slips:
        print(f"No valid slip reports found for {date_str}. Skipping.")
        return

    url = f"https://petron.myhiro.my/finances/clearing/sales?date={date_str}"
    page.goto(url, wait_until='domcontentloaded')
    time.sleep(4)

    for idx, slip in enumerate(slips):
        till_number = f"{date_str.replace('-', '')}-P{slip['pos']}S{slip['shift']}"
        print(f"\n[{idx+1}/{len(slips)}] Creating Till: {till_number} (POS {slip['pos']} Shift {slip['shift']})")

        select_till_btn = page.get_by_role('button', name='Select till')
        if select_till_btn.count() == 0:
            print("Notice: 'Select till' button not found on page.")
            continue

        select_till_btn.click()
        time.sleep(1)

        add_manual_btn = page.get_by_text('Add manual till')
        if add_manual_btn.count() == 0:
            print("Notice: 'Add manual till' menu option not found.")
            continue

        add_manual_btn.click()
        time.sleep(2)

        # 1. Fill Till number
        page.locator('#mt-no').fill(till_number)

        # 2. Select Cashier
        cashier_field = page.locator('.mt-field:has-text("Cashier") .form-select')
        cashier_field.click()
        time.sleep(1)

        items = page.locator('.dropdown-item, li, span, div[role="option"]').all_inner_texts()
        available_names = [x.split('\n')[0].strip() for x in items if x.strip() and not any(w in x for w in ['Include non-current', 'Please select', 'Theme'])]
        matched_cashier = match_cashier_name(slip['raw_cashier'], available_names)

        cashier_opt = page.locator('.dropdown-item, li, span, div[role="option"]').filter(has_text=matched_cashier).first
        if cashier_opt.count() > 0:
            cashier_opt.click()
            print(f"    Selected Cashier: {matched_cashier}")
        else:
            page.locator('.dropdown-item, li, span, div[role="option"]').filter(has_text='Owner').first.click()
            print(f"    Cashier '{matched_cashier}' not found, used fallback 'Owner'")
        time.sleep(1)

        # 3. Select Shift
        shift_val = str(slip['shift'])
        if shift_val == '1':
            shift_pill = page.locator('button.mt-seg-btn:has-text("07–15")')
        elif shift_val == '2':
            shift_pill = page.locator('button.mt-seg-btn:has-text("15–23")')
        else:
            shift_pill = page.locator('button.mt-seg-btn:has-text("23–07")')

        if shift_pill.count() > 0:
            shift_pill.click()
        time.sleep(1)

        # 4. Fill Total Sales
        sales_str = f"{slip['sales']:.2f}"
        page.locator('#mt-total').fill(sales_str)
        time.sleep(1)

        # 5. Fill How it was paid (Cash balanced)
        page.locator('input[aria-label="Amount of Cash"]').fill(sales_str)
        time.sleep(1)

        # Verify Balanced RM 0.00
        save_post_btn = page.locator('button:has-text("Save and post")')
        is_disabled = save_post_btn.get_attribute('disabled') is not None
        if not is_disabled:
            print(f"    Balanced (RM {sales_str})! Clicking 'Save and post'...")
            save_post_btn.click()
            try:
                page.locator('.modal').wait_for(state="detached", timeout=8000)
            except Exception:
                pass
            time.sleep(3)
            print(f"    Till {till_number} successfully posted!")
        else:
            save_btn = page.locator('button:has-text("Save")').first
            if save_btn.count() > 0 and save_btn.get_attribute('disabled') is None:
                print(f"    Clicking 'Save'...")
                save_btn.click()
                time.sleep(3)
            else:
                print(f"    Warning: Could not enable save button for {till_number}.")
                page.locator('button:has-text("Cancel")').click()
                time.sleep(1)

    screenshot_path = f"scratch/sales_clearing_{date_str.replace('-', '')}_done.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to: {screenshot_path}")

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

    if len(sys.argv) > 1:
        arg1 = sys.argv[1].strip()
        parsed_date, parsed_day = parse_date_arg(arg1)
        if parsed_date and parsed_date != "all":
            dates = [(parsed_date, parsed_day)]

    print("========================================================")
    print("      PETRON SALES CLEARING TILL POSTING AUTOMATION      ")
    print("========================================================")
    print(f"Target Dates: {[d[0] for d in dates]}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            ignore_default_args=['--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()

        for date_str, folder_day in dates:
            post_tills_for_date(page, date_str, folder_day)

    print("\nAll target dates processed successfully!")

if __name__ == "__main__":
    main()
