import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
import argparse
from playwright.sync_api import sync_playwright

profile_dir = os.path.abspath("browser_profile")
base_input_dir = os.path.abspath("input_files")

def find_opt_file(day_str):
    folder_path = os.path.join(base_input_dir, day_str)
    if not os.path.exists(folder_path):
        return None
    for f in os.listdir(folder_path):
        if "opt" in f.lower() and f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            return os.path.join(folder_path, f)
    return None

def wait_for_login(page):
    """Checks if the user needs to sign in or select station."""
    time.sleep(2)
    url = page.url.lower()
    
    body_text = page.inner_text("body") if page.locator("body").count() > 0 else ""
    needs_login = ("login" in url or "account" in url or 
                   "Sign in to your station" in body_text or 
                   "The page lost its connection" in body_text or
                   "Reload now" in body_text)
    
    if needs_login:
        if "login" not in url and "account" not in url:
            page.goto("https://petron.myhiro.my/Account/Login", wait_until="domcontentloaded")
            time.sleep(2)
            
        print("\n" + "=" * 65)
        print(" [!] ACTION REQUIRED:")
        print("     Please log in to your Petron account in the opened Chrome window.")
        print("     The script will automatically detect your login and continue...")
        print("=" * 65 + "\n")
        
        while True:
            time.sleep(3)
            current_url = page.url.lower()
            current_body = page.inner_text("body") if page.locator("body").count() > 0 else ""
            if "login" not in current_url and "account" not in current_url and "Sign in to your station" not in current_body and "Reload now" not in current_body:
                print(" [✓] Login detected! Continuing upload automation...\n")
                time.sleep(3)
                break

def upload_opt_for_date(page, date_str, day_str):
    opt_path = find_opt_file(day_str)
    if not opt_path:
        print(f"[-] Date {date_str} (Folder {day_str}): No OPT file found. Skipping.")
        return False
        
    file_name = os.path.basename(opt_path)
    url = f"https://petron.myhiro.my/station/eod?date={date_str}"
    print(f"\n=======================================================")
    print(f" Processing Date: {date_str} (Day {day_str})")
    print(f" Target File: {file_name}")
    print(f" URL: {url}")
    print(f"=======================================================")
    
    page.goto(url, wait_until='domcontentloaded')
    time.sleep(3)
    
    # Check if redirected to login or connection lost
    wait_for_login(page)
    if page.url != url:
        page.goto(url, wait_until='domcontentloaded')
        time.sleep(3)
        
    selector = "input[aria-label='Upload OPT'], input[aria-label='Open OPT']"
    inp = page.locator(selector)
    
    # Wait up to 5s for the slot input to be present in DOM
    try:
        inp.first.wait_for(state="attached", timeout=5000)
    except Exception:
        pass
        
    if inp.count() == 0:
        # Fallback: check if there's an Upload OPT button or card
        print("    [!] Slot input not directly found, looking for OPT button/card...")
        btn = page.locator("button:has-text('Upload OPT'), button:has-text('Open OPT')")
        if btn.count() > 0:
            try:
                with page.expect_file_chooser(timeout=5000) as fc_info:
                    btn.first.click()
                fc = fc_info.value
                fc.set_files(opt_path)
                print(f"    [✓] Attached {file_name} via file chooser button.")
            except Exception as e:
                print(f"    [X] Could not attach via button: {e}")
                return False
        else:
            print(f"    [X] Could not find OPT upload slot for {date_str}.")
            return False
    else:
        print(f"    --> Attaching {file_name} to OPT slot...")
        inp.first.set_input_files(opt_path)
        print(f"    [✓] Attached {file_name} successfully.")
        
    time.sleep(2)
    
    # Check if confirmation modal "Replace and read again" appears
    replace_btn = page.locator("button:has-text('Replace and read again')")
    try:
        replace_btn.wait_for(state="visible", timeout=3000)
        print("    [!] Confirmation modal detected: clicking 'Replace and read again'...")
        replace_btn.click(force=True)
        time.sleep(2)
    except Exception:
        pass
        
    # Check if "Read files" button is present and enabled
    read_btn = page.locator("button:has-text('Read files')")
    try:
        if read_btn.count() > 0 and read_btn.is_visible():
            if read_btn.is_enabled():
                print("    --> Clicking 'Read files' button...")
                read_btn.click(force=True)
            else:
                print("    --> 'Read files' is currently reading automatically.")
    except Exception as e:
        print(f"    Notice on Read files button: {e}")
        
    time.sleep(3)
    
    # Save confirmation screenshot
    os.makedirs("scratch", exist_ok=True)
    screenshot_path = f"scratch/opt_{date_str.replace('-', '')}.png"
    try:
        page.screenshot(path=screenshot_path)
        print(f"    [✓] Screenshot saved: {screenshot_path}")
    except Exception:
        pass
        
    return True

def main():
    parser = argparse.ArgumentParser(description="Automate Petron OPT File Upload")
    parser.add_argument("--cdp", type=int, default=None, help="Connect via CDP port (e.g. 9222)")
    parser.add_argument("--start", type=int, default=8, help="Start day (default: 8)")
    parser.add_argument("--end", type=int, default=30, help="End day (default: 30)")
    parser.add_argument("--month", type=str, default="09", help="Month (default: 09)")
    parser.add_argument("--year", type=str, default="2026", help="Year (default: 2026)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()

    days = [str(d).zfill(2) for d in range(args.start, args.end + 1)]
    print("=" * 65)
    print("         PETRON OPT AUTOMATIC DOCUMENT UPLOADER")
    print(f"   Date Range: {args.year}-{args.month}-{days[0]} to {args.year}-{args.month}-{days[-1]}")
    print(f"   Total Days to Process: {len(days)}")
    print("=" * 65)

    with sync_playwright() as p:
        browser = None
        context = None
        if args.cdp:
            try:
                print(f"\nConnecting to Chrome on port {args.cdp}...")
                browser = p.chromium.connect_over_cdp(f"http://localhost:{args.cdp}")
                context = browser.contexts[0]
                print(f"[✓] Successfully connected to existing Chrome via port {args.cdp}!")
            except Exception as e:
                print(f"[!] Could not connect to Chrome port {args.cdp}: {e}")
                print("    Falling back to launching browser...")

        if not context:
            print(f"\nLaunching Google Chrome (visible window)...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                headless=args.headless,
                ignore_default_args=['--no-sandbox'],
                args=["--start-maximized", "--disable-infobars"]
            )
        page = context.pages[0] if context.pages else context.new_page()

        # Initial connection check
        page.goto("https://petron.myhiro.my/station/eod?date=2026-09-08", wait_until="domcontentloaded")
        wait_for_login(page)

        success_count = 0
        skipped_count = 0

        for day in days:
            date_str = f"{args.year}-{args.month}-{day}"
            ok = upload_opt_for_date(page, date_str, day)
            if ok:
                success_count += 1
            else:
                skipped_count += 1
            time.sleep(1)

        print("\n" + "=" * 65)
        print("               UPLOAD BATCH COMPLETED!")
        print(f"   Successfully Processed: {success_count} days")
        print(f"   Skipped / Not Found:    {skipped_count} days")
        print("=" * 65)
        
        time.sleep(3)
        context.close()

if __name__ == "__main__":
    main()
