# scraper/amazon_scraper.py
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__(use_undetected=False) 
        self.website_name = "Amazon"
        self.base_url = "https://www.amazon.in"

    def search_product(self, product_name):
        try:
            print(f"🔄 Starting {self.website_name} scrape...")
            self.driver.get(self.base_url)
            self.random_delay(2, 4)

            print("🔍 Looking for search box...")
            search_box = self.wait_for_element("#twotabsearchtextbox", timeout=15)
            
            if search_box:
                print("✅ Search box found. Typing slowly...")
                search_box.clear()
                
                for char in product_name:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.2)) 
                    
                self.random_delay(1, 2)
                search_box.send_keys(Keys.RETURN)
                
                print(f"✅ {self.website_name} search submitted.")
                self.random_delay(4, 6) # Wait for results to load
                return True
            else:
                print(f"❌ {self.website_name} search box not found.")
                return False

        except Exception as e:
            print(f"❌ {self.website_name} search error: {e}")
            return False

    def get_product_details(self, max_products=5):
        products = []
        try:
            print(f"🔍 Looking for {self.website_name} products...")
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
            self.random_delay(2, 3)

            # This selector is working and finds the containers
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            print(f"🎯 Found {len(product_elements)} product containers. Now extracting details...")

            count = 0
            for product in product_elements:
                if count >= max_products:
                    break 
                    
                try:
                    product_name = "Not found"
                    product_price = "0"
                    product_url = ""
                    product_image = ""

                    # --- Skip "Sponsored" products ---
                    try:
                        product.find_element(By.CSS_SELECTOR, ".s-label-sponsored-product, .puis-label-sponsored-product")
                        print("--- Skipped Sponsored product ---")
                        continue 
                    except:
                        pass # Not sponsored, good

                    # --- NEW: CORRECTED NAME SELECTORS (FROM YOUR HTML) ---
                    name_selectors = [
                        "h2.a-size-medium.a-text-normal span",  # This is the most common one
                        "span.a-size-medium.a-color-base.a-text-normal" # This is the fallback
                    ]
                    for selector in name_selectors:
                        try:
                            name_element = product.find_element(By.CSS_SELECTOR, selector)
                            product_name = name_element.text.strip()
                            if product_name and len(product_name) > 5: 
                                break
                        except:
                            continue

                    # --- CORRECTED PRICE SELECTORS ---
                    price_selectors = [
                        "span.a-price-whole", # Primary
                        "span.a-price span.a-offscreen" # Fallback for hidden prices
                    ]
                    for selector in price_selectors:
                        try:
                            price_element = product.find_element(By.CSS_SELECTOR, selector)
                            product_price = price_element.text.strip()
                            if not product_price: 
                                product_price = price_element.get_attribute("innerHTML").strip()
                            
                            if product_price:
                                break
                        except:
                            continue

                    # --- CORRECTED URL SELECTOR ---
                    try:
                        link_element = product.find_element(By.CSS_SELECTOR, "a.a-link-normal.s-link-style.a-text-normal")
                        product_url = link_element.get_attribute("href")
                        if product_url and product_url.startswith("/"):
                            product_url = self.base_url + product_url
                    except:
                        pass

                    # --- Image Selector ---
                    try:
                        img_element = product.find_element(By.CSS_SELECTOR, "img.s-image")
                        product_image = img_element.get_attribute("src")
                    except:
                        pass

                    cleaned_price = self.extract_price(product_price)

                    if product_name != "Not found" and cleaned_price > 1000 and product_url:
                        products.append({
                            "name": product_name,
                            "price": cleaned_price,
                            "url": product_url,
                            "website": self.website_name,
                            "image": product_image
                        })
                        print(f"✅ {self.website_name}: {product_name[:40]}... - ₹{cleaned_price}")
                        count += 1
                    else:
                        print(f"--- Skipped product (Name: {product_name != 'Not found'} | Price: {cleaned_price > 1000} | URL: {bool(product_url)}) ---")
                    
                except Exception as e:
                    print(f"--- Error processing one Amazon product: {e} ---")
                    continue
        
        except Exception as e:
            print(f"❌ Error getting {self.website_name} products: {e}")
            
        return products