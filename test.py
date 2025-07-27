from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
import threading
from time import sleep
import random

# Shared lock for resource-sensitive operations
print_lock = threading.Lock()

def human_delay(min=0.3, max=1.2):
    sleep(random.uniform(min, max))

def worker(credentials, max_retries=3):
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                # Configure browser per thread
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    viewport={'width': 1366, 'height': 768}
                )
                page = context.new_page()

                try:
                    # Navigate to login
                    page.goto('https://eportal.oauife.edu.ng/login.php', timeout=15000)
                    human_delay()

                    # Fill credentials
                    page.fill('input[name="user_id"]', credentials['user_id'])
                    human_delay(0.5, 1)

                    page.fill('input[name="pswd"]', credentials['password'])
                    human_delay(0.3, 0.8)

                    # Select session/semester
                    page.select_option('select[name="SessionF"]', '2023')
                    page.select_option('select[name="SemesterF"]', '1')
                    human_delay()

                    # Submit form
                    with page.expect_navigation():
                        page.click('input[name="Submit"]')

                    # Verify login success
                    if not page.locator('text="Welcome"').first.is_visible(timeout=10000):
                        raise Exception("Login verification failed")

                    with print_lock:
                        print(f"✓ Login successful for {credentials['user_id']}")

                    # Navigate to bedspace allocation
                    bedspace_url = 'https://eportal.oauife.edu.ng/bedspaceallocationyear31.php'
                    page.goto(bedspace_url, timeout=15000)

                    # Verify bedspace page
                    if 'bedspaceallocationyear31' not in page.url:
                        raise Exception("Bedspace page redirection failed")

                    if not page.locator('h1:has-text("Bed Space")').first.is_visible():
                        raise Exception("Bedspace content verification failed")

                    with print_lock:
                        print(f"✓ Bedspace access for {credentials['user_id']}")

                    # Perform bedspace operations here
                    # ...

                    return True

                except Exception as e:
                    with print_lock:
                        print(f"Attempt {attempt+1} failed for {credentials['user_id']}: {str(e)}")
                    page.screenshot(path=f'error_{credentials["user_id"]}_{attempt}.png')
                    continue

                finally:
                    browser.close()

        except Exception as e:
            with print_lock:
                print(f"Critical error for {credentials['user_id']}: {str(e)}")
            continue

    return False

if __name__ == "__main__":
    # List of credentials to process
    credentials_list = [
        {
            'user_id': 'EEG/2022/040',
            'password': 'Geekspe@123'
        },
        # Add more credential dictionaries as needed
    ]

    # Configure thread pool
    max_workers = 3  # Adjust based on system capabilities
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, creds) for creds in credentials_list]
        results = [f.result() for f in futures]

    success_rate = sum(results)/len(results)
    print(f"Completed with {success_rate*100:.1f}% success rate")