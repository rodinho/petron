"""
Full End-to-End Petron EOD Document Downloader & Uploader
"""

import os
import sys
import time
import subprocess
import argparse
from playwright.sync_api import sync_playwright

def download_gdrive_folder(folder_url="https://drive.google.com/drive/folders/1kZdUCJL8vM-gyxd8_wuT_IQIeFAXjPt0", target_dir="input_files"):
    """Attempts to download all folders (01 to 07) from Google Drive using gdown."""
    print("\n[Step 1/2] Checking input files...")
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        python_exe = sys.executable
        cmd = [python_exe, "-m", "gdown", "--folder", folder_url, "-O", target_dir]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("  [✓] Successfully downloaded updated files from Google Drive!")
        else:
            print("  [i] Using available local files in input_files/")
    except Exception as e:
        print(f"  [i] GDrive note: {e}")

def map_date_files(folder_path):
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
        
        if "DAY END" in fu or "DER" in fu:
            mapping['day_end'] = p
        elif "OPT" in fu:
            mapping['opt'] = p
        elif "ATG" in fu or "TANK" in fu:
            mapping['atg'] = p
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

def perform_upload_on_page(page, label, file_path):
    if not file_path or not os.path.exists(file_path):
        return False
        
    file_name = os.path.basename(file_path)
    print(f"    -> Uploading to [{label}]: {file_name}")
    
    try:
        card = page.locator(f"xpath=//*[contains(text(), '{label}')]/ancestor-or-self::*[contains(@class, 'card') or contains(@class, 'box') or contains(@class, 'slot') or contains(@class, 'tile')][1]")
        if card.count() == 0:
            card = page.locator(f"text={label}").first
            
        with page.expect_file_chooser(timeout=6000) as fc_info:
            plus_icon = card.locator("text=+").first
            if plus_icon.count() > 0 and plus_icon.is_visible():
                plus_icon.click()
            else:
                card.click()
                
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        print(f"       [✓] Attached {file_name} successfully!")
        time.sleep(3)
        return True
    except Exception as e:
        try:
            inputs = page.locator("input[type='file']")
            if inputs.count() > 0:
                with page.expect_file_chooser(timeout=4000) as fc_info:
                    inputs.first.click()
                fc_info.value.set_files(file_path)
                print(f"       [✓] Attached {file_name} via input fallback!")
                time.sleep(3)
                return True
        except Exception:
            pass
            
    print(f"       [!] Could not attach {file_name}")
    return False

def run_automation():
    print("=" * 70)
    print("      PETRON EOD FULL AUTOMATION (DOWNLOAD + UPLOAD 01-07)")
    print("=" * 70)
    
    # 1. Download
    download_gdrive_folder()
    
    # 2. Browser
    print("\n[Step 2/2] Opening Google Chrome...")
    profile_dir = os.path.abspath("browser_profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            ignore_default_args=["--no-sandbox", "--disable-extensions"],
            args=["--test-type", "--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        # Check login status
        print("  Checking dealer login status...")
        page.goto("https://petron.myhiro.my/Account/Login", wait_until='networkidle')
        time.sleep(2)
        
        # If redirected away from login, already logged in!
        if "login" in page.url.lower():
            print("\n" + "=" * 70)
            print("  >>> ACTION REQUIRED: PLEASE SIGN IN IN THE CHROME WINDOW <<<")
            print("  Enter your Email and Password on screen and click 'Sign in'.")
            print("  The script will detect your login and start uploading automatically!")
            print("=" * 70 + "\n")
            
            while "login" in page.url.lower():
                time.sleep(2)
                
            print("  [✓] Login successful! Beginning document upload sequence...\n")
            time.sleep(3)
        else:
            print("  [✓] Session active (already logged in).")

        dates = ["01", "02", "03", "04", "05", "06", "07"]
        
        for d in dates:
            date_str = f"2026-09-{d}"
            folder_path = os.path.join("input_files", d)
            
            print(f"\n=======================================================")
            print(f"        PROCESSING DATE: {date_str}")
            print(f"=======================================================")
            
            if not os.path.exists(folder_path):
                print(f"  [!] Folder 'input_files/{d}' not found on disk. Skipping.")
                continue
                
            mapping = map_date_files(folder_path)
            eod_url = f"https://petron.myhiro.my/station/eod?date={date_str}"
            print(f"  Opening {eod_url}...")
            page.goto(eod_url, wait_until='networkidle')
            time.sleep(5)
            
            # 1. Shift 1
            print("  --- Processing Shift 1 ---")
            if mapping['shift1_pos1']:
                perform_upload_on_page(page, "POS-1", mapping['shift1_pos1'])
            if mapping['shift1_pos2']:
                perform_upload_on_page(page, "POS-2", mapping['shift1_pos2'])
            if mapping['shift1_pos3']:
                perform_upload_on_page(page, "POS-3", mapping['shift1_pos3'])
                
            # 2. Shift 2
            print("  --- Processing Shift 2 ---")
            if mapping['shift2_pos1']:
                perform_upload_on_page(page, "POS-1", mapping['shift2_pos1'])
            if mapping['shift2_pos2']:
                perform_upload_on_page(page, "POS-2", mapping['shift2_pos2'])
            if mapping['shift2_pos3']:
                perform_upload_on_page(page, "POS-3", mapping['shift2_pos3'])
                
            # 3. Station Reports
            print("  --- Processing Station Reports ---")
            if mapping['day_end']:
                perform_upload_on_page(page, "Day End", mapping['day_end'])
            if mapping['opt']:
                perform_upload_on_page(page, "OPT", mapping['opt'])
            if mapping['atg']:
                perform_upload_on_page(page, "ATG", mapping['atg'])
                
            print(f"  [✓] Finished uploads for {date_str}!")
            time.sleep(3)
            
        print("\n" + "=" * 70)
        print("  ALL SCHEDULED DATES HAVE BEEN PROCESSED!")
        print("=" * 70)
        input("\nPress Enter to close browser and finish...")

if __name__ == "__main__":
    run_automation()
