
# scraper/snapdeal_scraper.py
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class SnapdealScraper(BaseScraper):
    def __init__(self):
        # Snapdeal blocking se bachne ke liye undetected mode
        super().__init__(use_undetected=True)
        self.website_name = "Snapdeal"
    
    def search_product(self, product_name):
        try:
            print(f"🔄 Starting {self.website_name} scrape...")
            self.driver.get("https://www.snapdeal.com")
            self.random_delay(2, 4)
            
            search_box = None
            
            # --- Selectors ---
            selectors = [
                "input#search-box-input",   # Best working selector
                "input[name='keyword']",
                "#inputValEnter",
                "input.searchformInput",
                "input#keyword",
                "input[placeholder*='Search']"
            ]
            
            for selector in selectors:
                try:
                    search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if search_box.is_displayed():
                        break
                except:
                    continue
            
            # Fallback
            if not search_box:
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        if inp.is_displayed() and ("keyword" in (inp.get_attribute("name") or "").lower()):
                            search_box = inp
                            break
                except: pass

            if search_box:
                try:
                    search_box.click()
                    search_box.clear()
                except: pass
                
                search_box.send_keys(product_name)
                self.random_delay(0.5, 1)
                search_box.send_keys(Keys.RETURN)
                
                print(f"✅ {self.website_name} search submitted.")
                self.random_delay(3, 5) 
                return True
            else:
                print(f"❌ {self.website_name} search box NOT found.")
                return False
            
        except Exception as e:
            print(f"❌ {self.website_name} search error: {e}")
            return False
    
    def get_product_details(self, max_products=5):
        products = []
        try:
            print(f"🔍 Looking for {self.website_name} products...")
            
            try:
                self.wait_for_element("div.product-tuple-listing", timeout=10)
            except: pass

            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")
            
            if not product_elements:
                print(f"❌ No product containers found.")
                return []
                
            print(f"🎯 Found {len(product_elements)} products. Filtering & Extracting...")

            for i, product in enumerate(product_elements):
                # Stop if we have enough products
                if len(products) >= max_products:
                    break

                try:
                    product_name = "Not found"
                    product_price = "0"
                    product_url = ""
                    product_image = ""

                    # 1. NAME
                    try:
                        name_elem = product.find_element(By.CSS_SELECTOR, "p.product-title")
                        product_name = name_elem.text.strip() or name_elem.get_attribute("title")
                    except:
                        try:
                            product_name = product.find_element(By.TAG_NAME, "img").get_attribute("title")
                        except: pass

                    # --- 🚫 FILTER LOGIC: Skip Covers/Cases ---
                    # Agar naam me 'cover', 'case', 'glass' hai to skip karo
                    bad_keywords = ["cover", "case", "glass", "protector", "guard", "skin", "panel", "bumper"]
                    if any(bad_word in product_name.lower() for bad_word in bad_keywords):
                        # print(f"--- Skipped Accessory: {product_name[:30]}... ---")
                        continue
                    # ------------------------------------------

                    # 2. PRICE
                    try:
                        price_elem = product.find_element(By.CSS_SELECTOR, "span.product-price")
                        product_price = price_elem.get_attribute("display-price")
                        if not product_price:
                            product_price = price_elem.text.strip()
                    except: pass

                    # 3. URL
                    try:
                        link_elem = product.find_element(By.CSS_SELECTOR, "a.dp-widget-link")
                        product_url = link_elem.get_attribute("href")
                    except: pass

                    # 4. IMAGE
                    try:
                        try:
                            hidden_input = product.find_element(By.CSS_SELECTOR, "input.compareImg")
                            product_image = hidden_input.get_attribute("value")
                        except: pass
                        
                        if not product_image:
                            img_elem = product.find_element(By.CSS_SELECTOR, "img.product-image")
                            product_image = img_elem.get_attribute("data-src") or img_elem.get_attribute("src")
                    except: pass
                    
                    cleaned_price = self.extract_price(product_price)
                    
                    if product_name and product_name != "Not found" and cleaned_price > 10:
                        products.append({
                            "name": product_name,
                            "price": cleaned_price,
                            "url": product_url,
                            "website": self.website_name,
                            "image": product_image
                        })
                        print(f"✅ {self.website_name}: {product_name[:30]}... - ₹{cleaned_price}")

                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error getting {self.website_name} products: {e}")
        
        return products
