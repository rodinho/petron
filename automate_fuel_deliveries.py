import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, glob, time, pypdf
from playwright.sync_api import sync_playwright

profile_dir = os.path.abspath("browser_profile")
statement_dir = os.path.abspath(r"input_files\Petron Statement")

FUEL_KEYWORDS = ['blaze 95', 'blaze 97', 'blaze 100', 'diesel max', 'turbo diesel', 'gasoline']

def get_fuel_invoices():
    if not os.path.exists(statement_dir):
        print(f"[Error] Directory not found: {statement_dir}")
        return []
        
    in_files = sorted(glob.glob(os.path.join(statement_dir, "IN*.pdf")))
    fuel_files = []
    skipped = []
    
    for f in in_files:
        try:
            reader = pypdf.PdfReader(f)
            txt = reader.pages[0].extract_text().lower()
            if any(k in txt for k in FUEL_KEYWORDS):
                fuel_files.append(f)
            else:
                skipped.append(os.path.basename(f))
        except Exception as e:
            print(f"Error reading {os.path.basename(f)}: {e}")
            
    print(f"Found {len(fuel_files)} fuel invoices to process.")
    if skipped:
        print(f"Skipping non-fuel invoices ({len(skipped)}): {', '.join(skipped)}")
    return fuel_files

def upload_fuel_deliveries(target_files=None, batch_size=6):
    fuel_files = target_files or get_fuel_invoices()
    if not fuel_files:
        print("No fuel invoices found to upload.")
        return
        
    print("=" * 65)
    print("      PETRON FUEL DELIVERIES AUTOMATION")
    print(f"      Total invoices to upload: {len(fuel_files)}")
    print("=" * 65)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            ignore_default_args=['--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto('https://petron.myhiro.my/stations/petron/deliveries', wait_until='domcontentloaded')
        time.sleep(4)
        
        inp = page.locator("input[data-test='pd-upload']")
        if inp.count() == 0:
            print("[Error] Upload input[data-test='pd-upload'] not found on page.")
            context.close()
            return
            
        # Process in batches
        total_batches = (len(fuel_files) + batch_size - 1) // batch_size
        for b_idx in range(total_batches):
            batch = fuel_files[b_idx * batch_size : (b_idx + 1) * batch_size]
            print(f"\n--- Uploading Batch {b_idx + 1}/{total_batches} ({len(batch)} files) ---")
            for bf in batch:
                print(f"  + {os.path.basename(bf)}")
                
            inp.set_input_files(batch)
            print("Waiting 15 seconds for Blazor processing...")
            time.sleep(15)
            
            # Print recent alerts
            alerts = page.locator(".alert, .pt-alert, [role='alert']")
            for i in range(alerts.count()):
                txt = alerts.nth(i).inner_text().strip()
                if "posted" in txt.lower() or "invoice" in txt.lower():
                    print(f"  [Server Status] {txt}")
                    
        time.sleep(5)
        
        # Read final summary card
        print("\n" + "=" * 65)
        print("   FINAL FUEL DELIVERIES DASHBOARD STATUS")
        print("=" * 65)
        
        cards = page.locator(".card, .pt-root, .row")
        screenshot_path = "scratch/fuel_deliveries_dashboard.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        context.close()
    print("\n[COMPLETE] All fuel deliveries have been processed and posted!")

def main():
    if len(sys.argv) > 1:
        req = sys.argv[1].strip()
        all_fuel = get_fuel_invoices()
        matched = [f for f in all_fuel if req.lower() in os.path.basename(f).lower()]
        if matched:
            print(f"Filtering for request '{req}': found {len(matched)} files.")
            upload_fuel_deliveries(target_files=matched)
        else:
            print(f"No fuel invoices matching '{req}'. Running all.")
            upload_fuel_deliveries(target_files=all_fuel)
    else:
        upload_fuel_deliveries()

if __name__ == "__main__":
    main()
