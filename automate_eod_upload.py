"""
Automated Document Upload Script for Petron Station EOD
Target: https://petron.myhiro.my/station/eod?date=YYYY-MM-DD
Dates: 2026-09-01 to 2026-09-07
"""

import os
import sys
import time
import argparse
from playwright.sync_api import sync_playwright

def map_date_files(folder_path):
    """Maps files in date folder to their corresponding EOD slots."""
    if not os.path.exists(folder_path):
        return None
        
    files = os.listdir(folder_path)
    mapping = {
        'shift1_pos1': None,
        'shift1_pos2': None,
        'shift1_pos3': None,
        'shift2_pos1': None,
        'shift2_pos2': None,
        'shift2_pos3': None,
        'day_end': None,
        'opt': None,
        'atg': None
    }
    
    for f in sorted(files):
        p = os.path.abspath(os.path.join(folder_path, f))
        fu = f.upper()
        
        # Day End Report
        if "DAY END" in fu or "DER" in fu:
            mapping['day_end'] = p
        # OPT
        elif "OPT" in fu:
            mapping['opt'] = p
        # ATG / Tank Gauge / Fuel delivery
        elif "ATG" in fu or "TANK" in fu:
            mapping['atg'] = p
        # POS 1
        elif "POS 1" in fu or "POS1" in fu or "POS-1" in fu:
            if "SHIFT 1" in fu or "S1" in fu:
                mapping['shift1_pos1'] = p
            elif "SHIFT 2" in fu or "S2" in fu:
                mapping['shift2_pos1'] = p
            else:
                if not mapping['shift1_pos1']:
                    mapping['shift1_pos1'] = p
                else:
                    mapping['shift2_pos1'] = p
        # POS 2
        elif "POS 2" in fu or "POS2" in fu or "POS-2" in fu:
            if "SHIFT 1" in fu or "S1" in fu:
                mapping['shift1_pos2'] = p
            elif "SHIFT 2" in fu or "S2" in fu:
                mapping['shift2_pos2'] = p
            else:
                if not mapping['shift1_pos2']:
                    mapping['shift1_pos2'] = p
                else:
                    mapping['shift2_pos2'] = p
        # POS 3
        elif "POS 3" in fu or "POS3" in fu or "POS-3" in fu:
            if "SHIFT 1" in fu or "S1" in fu:
                mapping['shift1_pos3'] = p
            elif "SHIFT 2" in fu or "S2" in fu:
                mapping['shift2_pos3'] = p
            else:
                if not mapping['shift1_pos3']:
                    mapping['shift1_pos3'] = p
                else:
                    mapping['shift2_pos3'] = p
                    
    return mapping

def wait_for_login(page):
    """Checks if the page is currently on the login screen and waits for user to log in."""
    current_url = page.url.lower()
    if "login" in current_url or "account" in current_url:
        print("\n" + "=" * 70)
        print(" [!] ACTION REQUIRED: Please sign in to your dealer account")
        print("     in the opened Chrome browser window.")
        print("     The script will automatically continue once signed in...")
        print("=" * 70 + "\n")
        
        while True:
            time.sleep(2)
            current_url = page.url.lower()
            if "login" not in current_url and "account" not in current_url:
                print(" [✓] Login detected! Continuing with automation...\n")
                time.sleep(3)
                break

def upload_to_card(page, section_title, target_label, file_path):
    """
    Finds the upload card within the relevant section and attaches the file.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"  [-] {section_title} -> {target_label}: No file to upload (skipped)")
        return False
        
    file_name = os.path.basename(file_path)
    print(f"  [+] Uploading {section_title} [{target_label}]: '{file_name}'...")
    
    # Try multiple locator strategies to trigger file upload
    try:
        # Strategy A: Locate card by text within section
        # Look for section container first if possible
        card = None
        # Find element containing target_label (e.g. 'POS-1', 'Day End', 'OPT')
        locators = page.locator(f"text={target_label}").all()
        for loc in locators:
            if loc.is_visible():
                # Check if it has an upload '+' button or dropzone near it
                parent = loc.locator("xpath=./ancestor-or-self::div[contains(@class, 'card') or contains(@class, 'box') or contains(@class, 'tile') or contains(@class, 'drop') or contains(@class, 'slot')]").first
                card = parent if parent.count() > 0 else loc
                break

        if card and card.is_visible():
            with page.expect_file_chooser(timeout=6000) as fc_info:
                # Click the '+' sign or the card
                plus_btn = card.locator("text=+").first
                if plus_btn.count() > 0 and plus_btn.is_visible():
                    plus_btn.click()
                else:
                    card.click()
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
            print(f"      [✓] Attached '{file_name}' successfully!")
            time.sleep(3)  # wait for Dropzone / Blazor upload
            return True
    except Exception as e:
        pass

    # Strategy B: Direct input[type='file'] fallback
    try:
        file_inputs = page.locator("input[type='file']").all()
        for fi in file_inputs:
            with page.expect_file_chooser(timeout=4000) as fc_info:
                fi.click()
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
            print(f"      [✓] Attached '{file_name}' via input!")
            time.sleep(3)
            return True
    except Exception as e:
        print(f"      [!] Could not attach {file_name}: {e}")
        return False

def run_upload(cdp_port=None, base_dir="input_files"):
    print("=" * 70)
    print("      PETRON EOD DOCUMENT UPLOAD AUTOMATION (01 to 07)")
    print("=" * 70)
    
    profile_dir = os.path.abspath("browser_profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser_context = None
        
        # Mode 1: Connect via CDP if specified
        if cdp_port:
            try:
                print(f"Attempting to connect to existing Chrome on port {cdp_port}...")
                browser = p.chromium.connect_over_cdp(f"http://localhost:{cdp_port}")
                browser_context = browser.contexts[0]
                print("Connected to Chrome via port 9222!")
            except Exception as e:
                print(f"[!] Could not connect to Chrome port {cdp_port}: {e}")
                print("    Falling back to opening dedicated Chrome browser window...")
                
        # Mode 2: Launch visible dedicated Chrome window (no port conflicts!)
        if not browser_context:
            print(f"Launching Google Chrome (visible window)...")
            browser_context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                headless=False,
                args=["--start-maximized"]
            )
            print("Chrome window opened successfully!")
            
        page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
        
        # First navigate to base page and verify login
        page.goto("https://petron.myhiro.my/", wait_until='networkidle')
        wait_for_login(page)
        
        dates = ["01", "02", "03", "04", "05", "06", "07"]
        
        for d in dates:
            date_str = f"2026-09-{d}"
            folder_path = os.path.join(base_dir, d)
            
            print(f"\n=======================================================")
            print(f"        PROCESSING DATE: {date_str}")
            print(f"=======================================================")
            
            if not os.path.exists(folder_path):
                print(f"  [!] Folder '{folder_path}' does not exist locally yet. Skipping date {d}.")
                continue
                
            mapping = map_date_files(folder_path)
            eod_url = f"https://petron.myhiro.my/station/eod?date={date_str}"
            print(f"  Opening {eod_url}...")
            page.goto(eod_url, wait_until='networkidle', timeout=30000)
            time.sleep(4)
            
            # Check if session expired
            wait_for_login(page)
            
            # 1. Shift 1 Uploads
            print("\n  --- Processing Shift 1 ---")
            if mapping['shift1_pos1']:
                upload_to_card(page, "Shift 1", "POS-1", mapping['shift1_pos1'])
            if mapping['shift1_pos2']:
                upload_to_card(page, "Shift 1", "POS-2", mapping['shift1_pos2'])
            if mapping['shift1_pos3']:
                upload_to_card(page, "Shift 1", "POS-3", mapping['shift1_pos3'])
                
            # 2. Shift 2 Uploads
            print("\n  --- Processing Shift 2 ---")
            if mapping['shift2_pos1']:
                upload_to_card(page, "Shift 2", "POS-1", mapping['shift2_pos1'])
            if mapping['shift2_pos2']:
                upload_to_card(page, "Shift 2", "POS-2", mapping['shift2_pos2'])
            if mapping['shift2_pos3']:
                upload_to_card(page, "Shift 2", "POS-3", mapping['shift2_pos3'])
                
            # 3. Station Reports (Whole Day)
            print("\n  --- Processing Station Reports ---")
            if mapping['day_end']:
                upload_to_card(page, "Station Reports", "Day End", mapping['day_end'])
            if mapping['opt']:
                upload_to_card(page, "Station Reports", "OPT", mapping['opt'])
            if mapping['atg']:
                upload_to_card(page, "Station Reports", "ATG", mapping['atg'])
                
            print(f"\n  [✓] All available files for {date_str} completed!")
            time.sleep(3)
            
        print("\n" + "=" * 70)
        print("  ALL SCHEDULED DATES HAVE BEEN PROCESSED!")
        print("=" * 70)
        print("You can review the uploads in your Chrome window.")
        input("\nPress Enter to close browser and finish...")
        browser_context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdp", type=int, default=None, help="Connect via CDP port (e.g. 9222)")
    parser.add_argument("--dir", type=str, default="input_files", help="Path to input_files folder")
    args = parser.parse_args()
    run_upload(cdp_port=args.cdp, base_dir=args.dir)
