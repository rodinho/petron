import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, time, re
from playwright.sync_api import sync_playwright

profile_dir = os.path.abspath("browser_profile")

# Complete verified ATG reading data for Grand Saga Northbound (Tanks 2 to 7)
# Source: C:\Users\User\Documents\petron\input_files\ATG & Manual Meter Reading
ATG_DATA = {
    "2026-09-01": {
        "time": "23:43",
        "tanks": {
            "2": {"dip": "628.5", "litres": "6136", "water": "0"},
            "3": {"dip": "1442.4", "litres": "18559", "water": "0"},
            "4": {"dip": "1445.8", "litres": "18572", "water": "0"},
            "5": {"dip": "1420.1", "litres": "17597", "water": "0"},
            "6": {"dip": "770.1", "litres": "3925", "water": "0"},
            "7": {"dip": "577.8", "litres": "2655", "water": "0"},
        }
    },
    "2026-09-02": {
        "time": "23:41",
        "tanks": {
            "2": {"dip": "616.1", "litres": "5966", "water": "0"},
            "3": {"dip": "1332.1", "litres": "16836", "water": "0"},
            "4": {"dip": "1335.1", "litres": "16845", "water": "0"},
            "5": {"dip": "1095.7", "litres": "12506", "water": "0"},
            "6": {"dip": "733.6", "litres": "3687", "water": "0"},
            "7": {"dip": "576.8", "litres": "2648", "water": "0"},
        }
    },
    "2026-09-03": {
        "time": "23:43",
        "tanks": {
            "2": {"dip": "573.9", "litres": "5396", "water": "0"},
            "3": {"dip": "1247.6", "litres": "15506", "water": "0"},
            "4": {"dip": "1250.4", "litres": "15510", "water": "0"},
            "5": {"dip": "1325.0", "litres": "15343", "water": "0"},  # Physical dip correction
            "6": {"dip": "724.7", "litres": "3629", "water": "0"},
            "7": {"dip": "576.4", "litres": "2646", "water": "0"},
        }
    },
    "2026-09-04": {
        "time": "23:43",
        "tanks": {
            "2": {"dip": "554.5", "litres": "5140", "water": "0"},
            "3": {"dip": "1088.7", "litres": "12999", "water": "0"},
            "4": {"dip": "1090.7", "litres": "12992", "water": "0"},
            "5": {"dip": "1325.3", "litres": "14856", "water": "0"},
            "6": {"dip": "722.2", "litres": "3612", "water": "0"},
            "7": {"dip": "575.7", "litres": "2641", "water": "0"},
        }
    },
    "2026-09-05": {
        "time": "23:41",
        "tanks": {
            "2": {"dip": "521.4", "litres": "4709", "water": "0"},
            "3": {"dip": "1352.0", "litres": "17149", "water": "0"},
            "4": {"dip": "1707.7", "litres": "22496", "water": "0"},
            "5": {"dip": "1557.1", "litres": "18482", "water": "0"},
            "6": {"dip": "705.8", "litres": "3501", "water": "0"},
            "7": {"dip": "575.2", "litres": "2638", "water": "0"},
        }
    },
    "2026-09-06": {
        "time": "23:42",
        "tanks": {
            "2": {"dip": "506.4", "litres": "4518", "water": "0"},
            "3": {"dip": "871.0", "litres": "9634", "water": "0"},
            "4": {"dip": "875.0", "litres": "9656", "water": "0"},
            "5": {"dip": "1298.3", "litres": "14431", "water": "0"},
            "6": {"dip": "695.6", "litres": "3433", "water": "0"},
            "7": {"dip": "565.8", "litres": "2575", "water": "0"},
        }
    },
    "2026-09-07": {
        "time": "23:40",
        "tanks": {
            "2": {"dip": "689.3", "litres": "6986", "water": "0"},
            "3": {"dip": "1520.1", "litres": "19753", "water": "0"},
            "4": {"dip": "1320.0", "litres": "16607", "water": "0"},
            "5": {"dip": "1337.1", "litres": "15042", "water": "0"},
            "6": {"dip": "687.6", "litres": "3380", "water": "0"},
            "7": {"dip": "565.5", "litres": "2573", "water": "0"},
        }
    },
    "2026-09-08": {
        "time": "23:42",
        "tanks": {
            "2": {"dip": "666.4", "litres": "6663", "water": "0"},
            "3": {"dip": "1322.5", "litres": "16685", "water": "0"},
            "4": {"dip": "1324.8", "litres": "16682", "water": "0"},
            "5": {"dip": "1266.4", "litres": "13930", "water": "0"},
            "6": {"dip": "685.4", "litres": "3365", "water": "0"},
            "7": {"dip": "560.0", "litres": "2536", "water": "0"},
        }
    },
}

def fill_and_save_date(page, date_str, record):
    print(f"\n========================================================")
    print(f" Processing Actual Daily Dip for Date: {date_str}")
    print(f"========================================================")
    
    url = f"https://petron.myhiro.my/stations/daily-fuel-journal?date={date_str}"
    page.goto(url, wait_until='domcontentloaded')
    time.sleep(3)
    
    # 1. Ensure date matches
    date_inp = page.locator("input[type='date']").first
    if date_inp.count() > 0 and date_inp.input_value() != date_str:
        print(f"Selecting date {date_str}...")
        date_inp.fill(date_str)
        page.keyboard.press("Enter")
        time.sleep(3)
        
    tank_data = record["tanks"]
    time_str = record.get("time", "23:45")
    
    # 2. Open who dipped head-edit if closed
    head_edit = page.locator("[data-test='head-edit']")
    if not head_edit.is_visible():
        who_btn = page.locator("button.dd-who")
        if who_btn.count() > 0:
            who_btn.click()
            time.sleep(1)
            
    # 3. Fill dipped timestamp
    time_inp = page.locator("input[data-test='dip-time']")
    if time_inp.count() > 0:
        full_time = f"{date_str}T{time_str}"
        print(f"Setting dipped time: {full_time}")
        time_inp.fill(full_time)
        time_inp.dispatch_event("change")
        time.sleep(0.5)
        
    # 4. Fill employee if not selected
    person_dd = page.locator(".dd-field-by .form-select")
    if person_dd.count() > 0 and "Choose who" in person_dd.inner_text():
        print("Selecting employee who dipped...")
        person_dd.click()
        time.sleep(1)
        # Select first employee option from station list
        emp = page.locator(".dd-field-by .dropdown-item").first
        if emp.count() > 0:
            print(f"  Selected: {emp.inner_text().strip()}")
            emp.click()
            time.sleep(1)
            
    # 5. Fill tank dips
    rows = page.locator("div[data-test='tank-row']")
    row_count = rows.count()
    print(f"Entering dips for {row_count} tanks...")
    
    for i in range(row_count):
        row = rows.nth(i)
        t_name = row.locator(".dd-tank-name").inner_text().strip()
        if t_name in tank_data:
            info = tank_data[t_name]
            dip_inp = row.locator("input[data-test='dip-input']")
            water_inp = row.locator("input[data-test='water-input']")
            litres_inp = row.locator("input[data-test='dip-litres']")
            
            dip_inp.click()
            dip_inp.fill(info['dip'])
            page.keyboard.press("Tab")
            time.sleep(0.3)
            
            if water_inp.count() > 0 and info.get("water"):
                water_inp.click()
                water_inp.fill(info['water'])
                page.keyboard.press("Tab")
                time.sleep(0.3)
                
            litres_calc = litres_inp.input_value() if litres_inp.count() > 0 else "N/A"
            print(f"  Tank {t_name}: {info['dip']} mm -> {litres_calc} L")

    time.sleep(2)
    
    # 6. Save the record
    save_btn = page.locator("button[data-test='save']")
    save_note = page.locator("[data-test='save-note']").inner_text() if page.locator("[data-test='save-note']").count() > 0 else ""
    print(f"\nStatus before save: '{save_note}'")
    
    if save_btn.count() > 0 and not save_btn.is_disabled():
        print(">>> CLICKING SAVE BUTTON TO PERSIST RECORD... <<<")
        save_btn.click()
        time.sleep(4)
        final_note = page.locator("[data-test='save-note']").inner_text() if page.locator("[data-test='save-note']").count() > 0 else ""
        print(f"[SUCCESS] {final_note}")
    elif "saved" in save_note.lower():
        print(f"[ALREADY SAVED] {save_note}")
    else:
        print(f"[NOTICE] Save button state: disabled={save_btn.is_disabled()}. Note: {save_note}")
        
    scr_path = f"scratch/daily_dip_{date_str.replace('-', '')}_saved.png"
    page.screenshot(path=scr_path)
    print(f"Verification screenshot saved: {scr_path}")

def main():
    print("=" * 65)
    print("   PETRON DAILY FUEL JOURNAL - ACTUAL DAILY DIP AUTOMATION")
    print("=" * 65)
    
    dates_to_run = sorted(list(ATG_DATA.keys()))
    
    if len(sys.argv) > 1:
        req_date = sys.argv[1].strip()
        if req_date in ATG_DATA:
            dates_to_run = [req_date]
        else:
            print(f"Requested date '{req_date}' not found. Running all available dates.")
            
    print(f"Dates to process: {', '.join(dates_to_run)}")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            ignore_default_args=['--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        for date_str in dates_to_run:
            fill_and_save_date(page, date_str, ATG_DATA[date_str])
            
        context.close()
        
    print("\n[ALL COMPLETE] All requested daily dip records processed.")

if __name__ == "__main__":
    main()
