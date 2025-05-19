import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import pandas as pd
from pathlib import Path
import sys
import random
import time
import logging
from fake_useragent import UserAgent
import ctypes
import pyautogui

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('walmart_scraper.log'),
        logging.StreamHandler()
    ]
)


def setup_chrome_profile():
    profile_dir = os.path.join(os.getcwd(), "chrome_profile")
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    return profile_dir


def init_driver():
    profile_dir = setup_chrome_profile()
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')

    # Add random user agent
    # user_agents = [
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
    # ]
    # options.add_argument(f'user-agent={random.choice(user_agents)}')

    driver = uc.Chrome(options=options)
    return driver, WebDriverWait(driver, 15)


def handle_persistent_captcha(driver, wait):
    """Handle persistent captcha by restarting the browser"""
    logging.warning(
        "Persistent captcha detected. Closing browser and waiting...")
    try:
        driver.quit()
    except:
        pass


def handle_captcha_interaction():
    """Handle captcha by performing mouse interactions"""
    try:
        # Set cursor position twice as specified
        # ctypes.windll.user32.SetCursorPos(279, 392)
        # ctypes.windll.user32.SetCursorPos(279, 392)

        # # First long press
        # pyautogui.mouseDown()
        # time.sleep(12)
        # pyautogui.mouseUp()

        # # Second quick press
        # pyautogui.mouseDown()
        # time.sleep(0.2)
        # pyautogui.mouseUp()

        # Final wait
        time.sleep(2)
        return True
    except Exception as e:
        logging.error(f"Error during captcha interaction: {str(e)}")
        return False


def simulate_human_interaction(driver):
    """Simulate random human-like interactions"""
    try:
        # Random scroll amounts
        scroll_amounts = [1000, 200, 300, 400, 500]

        # Random mouse movements (using JavaScript since it's more reliable)
        driver.execute_script(f"""
            var event = new MouseEvent('mousemove', {{
                'clientX': {random.randint(100, 800)},
                'clientY': {random.randint(100, 600)}
            }});
            document.dispatchEvent(event);
        """)

        # Random scrolling pattern
        for _ in range(random.randint(2, 4)):
            scroll_amount = random.choice(scroll_amounts)
            driver.execute_script(f"window.scrollTo(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))

        # Sometimes scroll back up
        if random.random() < 0.3:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(0.3, 0.7))

    except Exception as e:
        logging.error(f"Error in human simulation: {str(e)}")


def check_for_captcha(driver, wait):
    try:
        captcha_indicators = [
            (By.ID, 'px-captcha'),
        ]

        for by, selector in captcha_indicators:
            try:
                element = driver.find_elements(by, selector)
                if element:
                    logging.warning(
                        "Captcha detected! Starting retry process...")

                    for attempt in range(3):
                        logging.info(
                            f"Attempt {attempt + 1}/3 to resolve captcha")

                        # Wait 10 seconds before checking again
                        time.sleep(10)

                        # Check if captcha is still present
                        if not driver.find_elements(by, selector):
                            logging.info("Captcha resolved after waiting")
                            return False

                        # If captcha still exists, refresh and add random delay
                        driver.refresh()
                        time.sleep(random.uniform(2, 4))
                        simulate_human_interaction(driver)

                        # Check again after refresh
                        if not driver.find_elements(by, selector):
                            logging.info("Captcha resolved after refresh")
                            return False

                        logging.warning(
                            f"Captcha persists after attempt {attempt + 1}")

                    logging.error("Captcha persists after all attempts")
                    return True
            except Exception:
                continue

        return False
    except Exception as e:
        logging.error(f"Error checking for captcha: {str(e)}")
        return False


def get_product_info(driver, wait, msid):
    max_retries = 1
    current_retry = 0

    while current_retry < max_retries:
        try:
            url = f"https://www.walmart.ca/en/ip/{msid}"

            # Random delay before navigation
            time.sleep(random.uniform(1, 3))
            driver.get(url)

            # Initial human-like interaction
            simulate_human_interaction(driver)

            if check_for_captcha(driver, wait):
                return "RESTART_BROWSER", None

            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "main")))
            except TimeoutException:
                if check_for_captcha(driver, wait):
                    current_retry += 1
                    if current_retry < max_retries:
                        continue
                    return None, None

            # Random delay before extraction
            time.sleep(random.uniform(0.2, 0.8))

            upc = None
            upc_selectors = [
                "//div[contains(@class, 'pb2')]//h3[contains(text(), 'Universal Product Code')]/../div/span",
                "//h3[contains(text(), 'UPC')]/following-sibling::div//span",
                "//div[contains(text(), 'UPC')]/following-sibling::div//span"
            ]

            for selector in upc_selectors:
                try:
                    upc_element = driver.find_element(By.XPATH, selector)
                    upc = upc_element.text.strip()
                    if upc:
                        break
                except NoSuchElementException:
                    continue

            walmart_id = None
            item_selectors = [
                "//h3[contains(text(), 'Walmart Item')]/../div/span",
                "//div[contains(text(), 'Walmart Item')]/following-sibling::div//span",
                "//span[contains(text(), 'Item #')]/following-sibling::span"
            ]

            for selector in item_selectors:
                try:
                    item_element = driver.find_element(By.XPATH, selector)
                    walmart_id = item_element.text.strip()
                    if walmart_id:
                        break
                except NoSuchElementException:
                    continue

            return upc, walmart_id

        except Exception as e:
            logging.error(
                f"Error getting product info for MSID {msid}: {str(e)}")
            current_retry += 1
            if current_retry < max_retries:
                time.sleep(random.uniform(2, 8))
                continue
            return None, None

    return None, None


def process_csv_files():
    logging.info("Starting UPC and Walmart ID extraction process...")
    driver, wait = init_driver()
    doordash_path = Path("doordash")

    try:
        merged_files = list(doordash_path.glob("*_merged.csv"))
        logging.info(f"Found {len(merged_files)} CSV files to process")

        for file_path in merged_files:
            logging.info(f"Processing file: {file_path.name}")
            df = pd.read_csv(file_path)

            if 'upc' not in df.columns:
                df['upc'] = None
            if 'walmart_id' not in df.columns:
                df['walmart_id'] = None

            rows_to_process = df[
                (df['upc'].isna() | (df['upc'] == '')) &
                (df['walmart_id'].isna() | (df['walmart_id'] == ''))
            ].index

            total_rows = len(rows_to_process)
            if total_rows == 0:
                logging.info(
                    f"All items in {file_path.name} already have UPC and Walmart ID data. Skipping...")
                continue

            logging.info(
                f"Found {total_rows} items without UPC/Walmart ID data")

            for i, row_idx in enumerate(rows_to_process):
                msid = str(df.loc[row_idx, 'msid'])
                logging.info(
                    f"Processing item {i + 1}/{total_rows}: MSID {msid}")

                results = get_product_info(driver, wait, msid)

                if results == ("RESTART_BROWSER", None):
                    driver, wait = handle_persistent_captcha(driver, wait)
                    continue  # Retry the same item

                upc, walmart_id = results
                if upc or walmart_id:
                    df.loc[row_idx, 'upc'] = str(upc) if upc else ''
                    df.loc[row_idx, 'walmart_id'] = str(
                        walmart_id) if walmart_id else ''
                    logging.info(
                        f"Found - UPC: {upc}, Walmart ID: {walmart_id}")

                # Save progress
                df.to_csv(file_path, index=False)

                # Random delay between items
                time.sleep(random.uniform(2, 4))

            logging.info(f"Completed processing {file_path.name}")

    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        if 'df' in locals() and 'file_path' in locals():
            df.to_csv(file_path, index=False)

    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    while True:
        process_csv_files()
        wait_time = random.randrange(240, 420)  # Wait between 3-5 minutes
        logging.info(f"Waiting {int(wait_time)} seconds before restarting...")
        time.sleep(wait_time)
        logging.info("Restarting the script...")
