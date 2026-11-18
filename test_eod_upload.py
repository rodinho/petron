import os, time
from playwright.sync_api import sync_playwright

profile_dir = os.path.abspath("browser_profile")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True,
        ignore_default_args=['--no-sandbox']
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://petron.myhiro.my/station/eod?date=2026-09-08", wait_until="domcontentloaded")
    time.sleep(5)
    print("Current URL:", page.url)
    
    # Check for inputs
    inputs = page.locator('input[type="file"]').all()
    print(f"Found {len(inputs)} file inputs:")
    for idx, inp in enumerate(inputs):
        aria = inp.get_attribute("aria-label")
        name = inp.get_attribute("name")
        print(f'  [{idx}] aria-label="{aria}", name="{name}"')
        
    slots = page.locator('.pt-slot').all()
    print(f"Found {len(slots)} slots:")
    for idx, s in enumerate(slots):
        print(f'  Slot {idx}: {s.inner_text().replace(chr(10), " ")[:100]}')

    context.close()
