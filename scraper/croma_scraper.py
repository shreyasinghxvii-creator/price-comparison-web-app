
# scraper/croma_scraper.py
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class CromaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.website_name = "Croma"
        self.base_url = "https://www.croma.com"

    def search_product(self, product_name):
        try:
            print(f"🔄 Starting {self.website_name} scrape...")
            self.driver.get(self.base_url)
            self.random_delay(3, 5)

            # Close popup if exists
            try:
                close_btn = self.driver.find_element(By.CSS_SELECTOR, "button#wzrk-cancel")
                if close_btn: close_btn.click()
            except: pass

            print("🔍 Looking for search box...")
            search_box = None
            selectors = ["input#searchV2", "input#search", "input[placeholder='What are you looking for?']"]
            
            for selector in selectors:
                search_box = self.wait_for_element(selector, timeout=5)
                if search_box:
                    break
            
            if search_box:
                print(f"✅ {self.website_name} search box found...")
                try:
                    search_box.click()
                    search_box.clear()
                except: pass
                
                search_box.send_keys(product_name)
                self.random_delay(1, 2)
                search_box.send_keys(Keys.RETURN)
                
                print(f"✅ {self.website_name} search submitted.")
                self.random_delay(5, 8) # Wait for results
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
            
            # Selectors for product container
            container_selectors = ["li.product-item", "div.cp-product", "div.product-item"]
            
            product_elements = []
            for selector in container_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    product_elements = elements
                    print(f"🎯 Found {len(elements)} products using selector: {selector}")
                    break
            
            if not product_elements:
                print(f"❌ No product containers found on {self.website_name}.")
                return []

            for i, product in enumerate(product_elements[:max_products]):
                try:
                    product_name = "Not found"
                    product_price = "0"
                    product_url = ""
                    product_image = ""

                    # --- Name Extraction ---
                    try:
                        name_elem = product.find_element(By.CSS_SELECTOR, "h3.product-title, div.product-title")
                        product_name = name_elem.text.strip()
                    except: 
                        # Fallback: Title from image alt or link title
                        try:
                            img = product.find_element(By.TAG_NAME, "img")
                            product_name = img.get_attribute("alt") or img.get_attribute("title")
                        except: pass

                    # --- Price Extraction ---
                    try:
                        price_elem = product.find_element(By.CSS_SELECTOR, "span.amount, span.new-price, span[data-testid='new-price']")
                        product_price = price_elem.text.strip()
                    except: pass

                    # --- URL Extraction ---
                    try:
                        # Try finding 'a' tag inside title first
                        link_elem = product.find_element(By.CSS_SELECTOR, "h3.product-title a, div.product-title a")
                        product_url = link_elem.get_attribute("href")
                    except:
                        try:
                            # Try finding any 'a' tag in the card
                            links = product.find_elements(By.TAG_NAME, "a")
                            for link in links:
                                href = link.get_attribute("href")
                                if href and ("/p/" in href or "/buy/" in href): # Valid Croma product link
                                    product_url = href
                                    break
                        except: pass
                    
                    # Ensure Full URL
                    if product_url and not product_url.startswith("http"):
                        product_url = "https://www.croma.com" + product_url

                    # --- IMAGE EXTRACTION (FIXED FOR LAZY LOADING) ---
                    try:
                        img_elem = None
                        # 1. Try to find the image element in specific containers
                        try:
                            img_elem = product.find_element(By.CSS_SELECTOR, "div.product-img img, div.cp-product-img img")
                        except:
                            # Fallback: Find any image tag
                            img_elem = product.find_element(By.TAG_NAME, "img")
                        
                        if img_elem:
                            # 2. Check hidden attributes first!
                            # Croma often uses 'data-src' or 'data-original' for the real image before loading
                            product_image = img_elem.get_attribute("data-src") or \
                                          img_elem.get_attribute("data-original") or \
                                          img_elem.get_attribute("src")
                                          
                            # If we still got the gif or a 'lazy' placeholder, scroll to it to trigger load
                            if product_image and ("lazy" in product_image.lower() or "gif" in product_image.lower()):
                                self.driver.execute_script("arguments[0].scrollIntoView();", img_elem)
                                time.sleep(0.5) # Short wait for JS to fire and swap the image
                                product_image = img_elem.get_attribute("src")

                    except Exception as e:
                        print(f"Img error: {e}")

                    cleaned_price = self.extract_price(product_price)

                    if product_name and product_name != "Not found" and cleaned_price > 100:
                        products.append({
                            "name": product_name,
                            "price": cleaned_price,
                            "url": product_url,
                            "website": self.website_name,
                            "image": product_image
                        })
                        print(f"✅ {self.website_name}: Found {product_name[:20]}... | URL: {bool(product_url)} | Img: {bool(product_image)}")
                    
                except Exception as e:
                    print(f"Error processing {self.website_name} product {i}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error getting {self.website_name} products: {e}")
            
        return products
