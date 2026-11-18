import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, time, re
from playwright.sync_api import sync_playwright

profile_dir = os.path.abspath("browser_profile")
base_input_dir = os.path.abspath("input_files")

def map_folder_files(folder_path):
    if not os.path.exists(folder_path):
        return {}
    
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))]
    mapping = {}
    
    for f in sorted(files, key=lambda x: (1 if "eod" in x.lower() and "shift" not in x.lower() else 0)):
        fl = f.lower()
        full_path = os.path.join(folder_path, f)
        
        # Whole Day Reports
        if "der" in fl or "day end" in fl or "dayend" in fl:
            mapping["Upload Day End"] = full_path
        elif "opt" in fl:
            mapping["Upload OPT"] = full_path
            
        # Shift 2
        elif "shift 2" in fl or "shift2" in fl:
            if "pos 1" in fl or "pos-1" in fl or "pos1" in fl:
                mapping["Upload POS-1 Shift 2"] = full_path
            elif "pos 2" in fl or "pos-2" in fl or "pos2" in fl:
                mapping["Upload POS-2 Shift 2"] = full_path
            elif "pos 3" in fl or "pos-3" in fl or "pos3" in fl:
                mapping["Upload POS-3 Shift 2"] = full_path
                
        # Specific Shift 1 (End Shift Report)
        elif "shift 1" in fl or "shift1" in fl:
            if "pos 1" in fl or "pos-1" in fl or "pos1" in fl:
                mapping["Upload POS-1 Shift 1"] = full_path
            elif "pos 2" in fl or "pos-2" in fl or "pos2" in fl:
                mapping["Upload POS-2 Shift 1"] = full_path
            elif "pos 3" in fl or "pos-3" in fl or "pos3" in fl:
                mapping["Upload POS-3 Shift 1"] = full_path

        # Fallback EOD POS (only if slot not already populated by Shift 1 report)
        elif "eod pos" in fl:
            if ("pos 1" in fl or "pos-1" in fl or "pos1" in fl) and "Upload POS-1 Shift 1" not in mapping:
                mapping["Upload POS-1 Shift 1"] = full_path
            elif ("pos 2" in fl or "pos-2" in fl or "pos2" in fl) and "Upload POS-2 Shift 1" not in mapping:
                mapping["Upload POS-2 Shift 1"] = full_path
            elif ("pos 3" in fl or "pos-3" in fl or "pos3" in fl) and "Upload POS-3 Shift 1" not in mapping:
                mapping["Upload POS-3 Shift 1"] = full_path
        # Fallback generic EOD file (e.g. EOD.pdf) -> POS-1 Shift 1
        elif "eod" in fl and "Upload POS-1 Shift 1" not in mapping:
            mapping["Upload POS-1 Shift 1"] = full_path
                
    return mapping

def upload_for_date(page, date_str, folder_day, pos_filter=None, trigger_read=True):
    folder_path = os.path.join(base_input_dir, folder_day)
    mapping = map_folder_files(folder_path)
    
    if pos_filter:
        norm_filter = pos_filter.lower().replace(" ", "").replace("-", "")
        filtered_mapping = {}
        for slot, path in mapping.items():
            slot_norm = slot.lower().replace(" ", "").replace("-", "")
            file_norm = os.path.basename(path).lower().replace(" ", "").replace("-", "")
            if norm_filter in slot_norm or norm_filter in file_norm:
                filtered_mapping[slot] = path
        mapping = filtered_mapping
    
    print(f"\n==========================================")
    print(f"Processing Date: {date_str} (Folder: {folder_day})")
    if pos_filter:
        print(f"Filter: [POS / Slot: {pos_filter}]")
    print(f"Mapped files: {len(mapping)}")
    for slot, path in mapping.items():
        print(f"  [{slot}] -> {os.path.basename(path)}")
    print(f"==========================================")
    
    if not mapping:
        print(f"No matching files found for {date_str}. Skipping.")
        return
        
    url = f"https://petron.myhiro.my/station/eod?date={date_str}"
    page.goto(url, wait_until='domcontentloaded')
    time.sleep(3)
    
    for slot_name, file_path in mapping.items():
        # Match both empty (Upload) and filled (Open) slot input selectors
        selector = f"input[aria-label='{slot_name}'], input[aria-label='{slot_name.replace('Upload ', 'Open ')}']"
        inp = page.locator(selector)
        
        if inp.count() > 0:
            print(f"--> Uploading/Overwriting: {slot_name} ({os.path.basename(file_path)})")
            inp.first.set_input_files(file_path)
            time.sleep(2)
            
            # Check if confirmation modal "Replace and read again" appears
            replace_btn = page.locator("button:has-text('Replace and read again')")
            try:
                replace_btn.wait_for(state="visible", timeout=3000)
                print("    Confirming replacement ('Replace and read again')...")
                replace_btn.click(force=True)
                replace_btn.wait_for(state="detached", timeout=5000)
                time.sleep(2)
            except Exception:
                pass
        else:
            print(f"--> Notice: Slot {slot_name} not available for upload on page.")
            
    # Check if any lingering modal is still open
    lingering_replace = page.locator("button:has-text('Replace and read again')")
    try:
        if lingering_replace.count() > 0 and lingering_replace.is_visible():
            print("    Confirming lingering replacement dialog...")
            lingering_replace.first.click(force=True)
            time.sleep(2)
    except Exception:
        pass

    # Wait for and click "Read files" button after uploading each day's files
    if trigger_read:
        read_btn = page.locator("button:has-text('Read files'), button:has-text('Read all'), button:has-text('Read again')").first
        clicked_read = False
        for _ in range(10):
            try:
                if read_btn.count() > 0 and read_btn.is_visible() and read_btn.is_enabled():
                    read_btn.scroll_into_view_if_needed()
                    print("--> Triggering 'Read files' button for uploaded slips...")
                    read_btn.click(force=True)
                    clicked_read = True
                    break
            except Exception as e:
                print("Notice on Read files button:", e)
            time.sleep(1)
        if not clicked_read:
            print("--> Notice: 'Read files' button was not visible/enabled (may have auto-read on upload).")
        
    print("Waiting 15 seconds for Blazor processing...")
    time.sleep(15)
    
    # Check slots
    slots = page.locator('.pt-slot')
    print(f"\nCurrent Status for {date_str}:")
    for i in range(slots.count()):
        text = slots.nth(i).inner_text().replace('\n', ' ')
        print(f"  Slot {i}: {text}")
        
    screenshot_path = f"scratch/eod_{date_str.replace('-', '')}_uploaded.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to: {screenshot_path}")

def parse_date_range_arg(arg):
    """Parse a day range like '09-30' or '09 to 30' into [(YYYY-MM-DD, DD), ...]."""
    m = re.fullmatch(r"(\d{1,2})\s*(?:-|to)\s*(\d{1,2})", arg.strip().lower())
    if not m:
        return None
    start_d, end_d = int(m.group(1)), int(m.group(2))
    if 1 <= start_d <= end_d <= 31:
        return [(f"2026-09-{str(d).zfill(2)}", str(d).zfill(2)) for d in range(start_d, end_d + 1)]
    return None

def parse_date_arg(arg):
    arg = arg.strip().lower()
    if arg == "all":
        return "all", None
    # Handle formats like "03/09", "03/09/2026", "3/9", "3/9/2026"
    if "/" in arg:
        parts = arg.split("/")
        day = parts[0].zfill(2)
        month = parts[1].zfill(2) if len(parts) > 1 else "09"
        year = parts[2] if len(parts) > 2 else "2026"
        if len(year) == 2:
            year = "20" + year
        return f"{year}-{month}-{day}", day
    # Handle "2026-09-03" or "20260903"
    clean = arg.replace("-", "")
    if len(clean) == 8 and clean.isdigit():
        return f"{clean[:4]}-{clean[4:6]}-{clean[6:]}", clean[6:]
    # Handle single or double digit day "03" or "3"
    if clean.isdigit() and len(clean) <= 2:
        day = clean.zfill(2)
        return f"2026-09-{day}", day
    return None, None

def main():
    # Detect all folders 01 to 31 available in base_input_dir
    all_days = []
    if os.path.exists(base_input_dir):
        for entry in sorted(os.listdir(base_input_dir)):
            if entry.isdigit() and len(entry) <= 2:
                day_str = entry.zfill(2)
                all_days.append((f"2026-09-{day_str}", day_str))
    if not all_days:
        all_days = [(f"2026-09-{str(d).zfill(2)}", str(d).zfill(2)) for d in range(1, 31)]
    dates = all_days
    
    args = [a for a in sys.argv[1:] if a.strip().lower() != "--no-read"]
    trigger_read = "--no-read" not in [a.strip().lower() for a in sys.argv[1:]]

    pos_filter = None
    if len(args) > 0:
        arg1 = args[0].strip()
        range_dates = parse_date_range_arg(arg1)
        if range_dates:
            dates = range_dates
            if len(args) > 1:
                pos_filter = " ".join(args[1:]).strip()
        else:
            parsed_date, parsed_day = parse_date_arg(arg1)
            if parsed_date == "all":
                if len(args) > 1:
                    pos_filter = " ".join(args[1:]).strip()
            elif parsed_date:
                dates = [(parsed_date, parsed_day)]
                if len(args) > 1:
                    pos_filter = " ".join(args[1:]).strip()
            else:
                # First argument is a POS filter
                pos_filter = " ".join(args).strip()
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            ignore_default_args=['--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        for date_str, folder_day in dates:
            folder_path = os.path.join(base_input_dir, folder_day)
            if os.path.exists(folder_path):
                upload_for_date(page, date_str, folder_day, pos_filter=pos_filter, trigger_read=trigger_read)
            else:
                print(f"\nFolder {folder_day} not present in input_files yet. Skipping {date_str}.")
                
        context.close()
    print("\nBatch upload execution finished.")

if __name__ == "__main__":
    main()
