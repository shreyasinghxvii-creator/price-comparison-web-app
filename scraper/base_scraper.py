# scraper/base_scraper.py
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- FIX: Better Error Reporting ---
try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME = True
    print("[OK] undetected-chromedriver library found. Will use for Amazon/Snapdeal.")
except Exception as e:
    UNDETECTED_CHROME = False
    print(f"[WARNING] undetected-chromedriver NOT found or error occurred: {e}")
    print("[WARNING] Falling back to regular Selenium.")

class BaseScraper:
    def __init__(self, use_undetected=False):
        self.driver = None
        self.setup_driver(use_undetected)

    def setup_driver(self, use_undetected=False):
        """Chrome browser setup"""
        
        # Priority 1: Use undetected_chromedriver if requested and available
        if use_undetected:
            if UNDETECTED_CHROME:
                try:
                    print("[INFO] Launching undetected_chromedriver...")
                    options = uc.ChromeOptions()
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    # options.add_argument('--headless') 
                    
                    # Set Chrome binary path for macOS
                    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                    
                    self.driver = uc.Chrome(options=options, use_subprocess=False, version_main=142)
                    print("[OK] undetected_chromedriver launched successfully.")
                    return
                except Exception as e:
                    print(f"[ERROR] Failed to launch undetected_chromedriver: {e}")
                    print("[INFO] Falling back to standard Selenium...")
            else:
                print("[WARNING] undetected-chromedriver requested but not installed/working.")

        # Priority 2: Regular Selenium (Fallback)
        print("[INFO] Launching Standard Selenium WebDriver...")
        
        chrome_options = Options()
        # Enhanced anti-blocking settings
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        # Try multiple approaches for ChromeDriver
        driver_created = False
        
        # Method 1: Try webdriver-manager
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            print("[INFO] Attempting to use webdriver-manager...")
            driver_path = ChromeDriverManager().install()
            print(f"[INFO] ChromeDriver path: {driver_path}")
            
            # Fix webdriver-manager path issue
            import os
            if not driver_path.endswith('chromedriver'):
                # webdriver-manager sometimes returns the wrong path
                driver_dir = os.path.dirname(driver_path)
                actual_driver = os.path.join(driver_dir, 'chromedriver')
                if os.path.exists(actual_driver):
                    driver_path = actual_driver
                    print(f"[INFO] Corrected driver path to: {driver_path}")
                else:
                    # Look for chromedriver in the directory
                    for file in os.listdir(driver_dir):
                        if file == 'chromedriver' or (file.startswith('chromedriver') and not file.endswith('.txt')):
                            driver_path = os.path.join(driver_dir, file)
                            print(f"[INFO] Found actual driver: {driver_path}")
                            break
            
            # Ensure the driver is executable
            import stat
            if os.path.exists(driver_path):
                os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                self.driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
                driver_created = True
                print("[OK] webdriver-manager ChromeDriver successful.")
            else:
                print(f"[WARNING] ChromeDriver not found at: {driver_path}")
            
        except Exception as wdm_error:
            print(f"[WARNING] webdriver-manager failed: {wdm_error}")
        
        # Method 2: Try system ChromeDriver
        if not driver_created:
            try:
                print("[INFO] Attempting to use system ChromeDriver...")
                self.driver = webdriver.Chrome(options=chrome_options)
                driver_created = True
                print("[OK] System ChromeDriver successful.")
            except Exception as system_error:
                print(f"[WARNING] System ChromeDriver failed: {system_error}")
        
        # Method 3: Try with explicit Chrome binary path
        if not driver_created:
            try:
                print("[INFO] Attempting with explicit Chrome binary...")
                chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                self.driver = webdriver.Chrome(options=chrome_options)
                driver_created = True
                print("[OK] Explicit Chrome binary successful.")
            except Exception as binary_error:
                print(f"[WARNING] Explicit Chrome binary failed: {binary_error}")
        
        if not driver_created:
            print("[CRITICAL ERROR] All ChromeDriver methods failed!")
            print("[HELP] Please ensure Chrome browser is installed and up to date.")
            print("[HELP] You may need to manually install ChromeDriver: https://chromedriver.chromium.org/")
            raise Exception("Unable to initialize ChromeDriver with any method")
        
        # Remove 'navigator.webdriver' flag to avoid detection
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("[OK] Anti-detection script applied.")
        except Exception as script_error:
            print(f"[WARNING] Could not apply anti-detection script: {script_error}")

    def random_delay(self, min_seconds=2, max_seconds=5):
        """Random delay for anti-blocking"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for element to load"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except:
            return None

    def extract_price(self, price_text):
        """Extract price number from text"""
        if not price_text:
            return 0.0
        
        # Remove currency symbols, text, and commas
        clean_text = re.sub(r'[^\d.]', '', str(price_text))
        
        try:
            return float(clean_text)
        except:
            return 0.0

    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass