
# scraper/flipkart_scraper.py
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class FlipkartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.website_name = "Flipkart"
    
    def search_product(self, product_name):
        try:
            print(f"[INFO] Starting {self.website_name} scrape...")
            self.driver.get("https://www.flipkart.com")
            self.random_delay(2, 4)
            
            # Popup Close - handle both login popup and notification popup
            try:
                # Try login popup first
                login_popup_close = self.driver.find_element(By.CSS_SELECTOR, "button._2KpZ6l._2doB4z")
                login_popup_close.click()
                self.random_delay(1, 2)
            except:
                try:
                    # Try notification popup
                    notification_close = self.driver.find_element(By.CSS_SELECTOR, "button[class*='close'], button[class*='dismiss']")
                    notification_close.click()
                    self.random_delay(1, 2)
                except:
                    pass  # No popup found
            
            # Search
            search_box = self.wait_for_element("input[name='q']", timeout=10)
            if search_box:
                search_box.clear()
                search_box.send_keys(product_name)
                search_box.send_keys(Keys.RETURN)
                print(f"[OK] {self.website_name} search submitted.")
                self.random_delay(3, 5)
                return True
            return False
            
        except Exception as e:
            print(f"Flipkart search error: {e}")
            return False
    
    def get_product_details(self, max_products=5):
        products = []
        try:
            print(f"[INFO] Looking for {self.website_name} products...")
            
            # Lazy Loading Trigger
            self.driver.execute_script("window.scrollTo(0, 500);")
            self.random_delay(1, 2)

            # --- UNIVERSAL SELECTORS (Updated for 2025 Layouts) ---
            container_selectors = [
                "div._1fQZEK",       # Old Mobiles
                "div.cPHDOP",        # New Mobiles / General
                "div._75nlfW",       # Another Mobile Layout
                "div._1xHGtK",       # Fashion / Watches
                "div._4ddWXP",       # Grid Items
                "div[data-id]"       # Universal Fallback
            ]
            
            product_elements = []
            for selector in container_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > 2:
                    product_elements = elements
                    print(f"[INFO] Found {len(elements)} products using selector: {selector}")
                    break
            
            if not product_elements:
                print("[ERROR] No product containers found.")
                return []

            for i, product in enumerate(product_elements[:max_products]):
                try:
                    product_name = "Not found"
                    product_price = "0"
                    product_url = ""
                    product_image = ""

                    # 1. NAME Extraction (Priority Order)
                    name_selectors = [
                        "div.RG5Slk",    # New Mobiles (Found in Debug)
                        "div.KzDlHZ",    # Common New Mobile Class
                        "div._4rR01T",   # Old Mobiles
                        "a.atJtCj",      # Watches (Found in Debug)
                        "a.IRpwTa",      # Fashion
                        "a.s1Q9rs",      # Grid items
                        "a._2rpwqI"      # Generic
                    ]
                    for sel in name_selectors:
                        try:
                            name_elem = product.find_element(By.CSS_SELECTOR, sel)
                            product_name = name_elem.text.strip() or name_elem.get_attribute("title")
                            if product_name: break
                        except: continue

                    # 2. PRICE Extraction (Priority Order)
                    price_selectors = [
                        "div.Nx9bqj",    # New Standard (Found in Debug logic)
                        "div.hZ3P6w",    # Watches
                        "div._30jeq3",   # Old Standard
                        "div._25b18c",   # Grid
                        "div._1_WHN1"
                    ]
                    for sel in price_selectors:
                        try:
                            price_elem = product.find_element(By.CSS_SELECTOR, sel)
                            product_price = price_elem.text.strip()
                            if product_price: break
                        except: continue

                    # 3. URL Extraction
                    try:
                        # Try New Mobile Link
                        try:
                            link_elem = product.find_element(By.CSS_SELECTOR, "a.k7wcnx") # New Mobile
                            product_url = link_elem.get_attribute("href")
                        except:
                            # Try Watch Link
                            try:
                                link_elem = product.find_element(By.CSS_SELECTOR, "a.CIaYa1") # Watch
                                product_url = link_elem.get_attribute("href")
                            except:
                                # Fallback to any main link
                                link_elem = product.find_element(By.TAG_NAME, "a")
                                product_url = link_elem.get_attribute("href")
                    except: pass

                    # 4. IMAGE Extraction
                    try:
                        img_selectors = [
                            "img.UCc1lI",   # New Mobiles
                            "img.MZeksS",   # Watches
                            "img.DByuf4",   # Common
                            "img._396cs4",  # Old Mobiles
                            "img._2r_T1I",
                            "img"
                        ]
                        for sel in img_selectors:
                            try:
                                img_elem = product.find_element(By.CSS_SELECTOR, sel)
                                product_image = img_elem.get_attribute("src")
                                if product_image: break
                            except: continue
                    except: pass
                    
                    cleaned_price = self.extract_price(product_price)
                    
                    # Filter: Name valid ho aur Price > 10 ho (Unavailable items skip ho jayenge)
                    if product_name and product_name != "Not found" and cleaned_price > 10:
                        products.append({
                            "name": product_name,
                            "price": cleaned_price,
                            "url": product_url,
                            "website": self.website_name,
                            "image": product_image
                        })
                        print(f"[OK] {self.website_name}: {product_name[:30]}... - Rs.{cleaned_price}")

                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error getting products: {e}")
        
        return products
