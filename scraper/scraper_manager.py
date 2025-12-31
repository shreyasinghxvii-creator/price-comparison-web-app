
# scraper/scraper_manager.py
import concurrent.futures
from .flipkart_scraper import FlipkartScraper
from .amazon_scraper import AmazonScraper
from .snapdeal_scraper import SnapdealScraper
from .croma_scraper import CromaScraper
import time

class ScraperManager:
    def __init__(self):
        self.scrapers = {
            'flipkart': FlipkartScraper,
            'croma': CromaScraper,      
            'amazon': AmazonScraper,    
            'snapdeal': SnapdealScraper
        }
        # Hum in chaaron ko ek saath run karenge
        self.active_scrapers = ['flipkart', 'croma', 'amazon', 'snapdeal'] 

    def _run_single_scraper(self, website_name, product_name, max_products):
        """
        Ek single scraper ko safe tarike se run karne ka function.
        Har thread ke liye naya scraper instance banega.
        """
        if website_name not in self.scrapers:
            return []
            
        print(f"--- [INFO] Starting {website_name} scrape (Thread) ---")
        scraper_class = self.scrapers[website_name]
        
        # Har thread mein naya browser open hoga
        scraper = scraper_class() 
        results = []
        
        try:
            if scraper.search_product(product_name):
                found_products = scraper.get_product_details(max_products)
                results.extend(found_products)
                print(f"--- [OK] {website_name}: Found {len(found_products)} products ---")
            else:
                print(f"--- [ERROR] {website_name}: Search failed ---")
        except Exception as e:
            print(f"--- [ERROR] Error in {website_name}: {e} ---")
        finally:
            # Kaam khatam hote hi browser band karna zaroori hai
            scraper.close()
            
        return results

    def search_all_websites(self, product_name, max_products=5):
        """
        Parallel execution: Saare scrapers ek saath chalenge.
        """
        all_products = []
        start_time = time.time()
        
        print(f"[INFO] Starting parallel search for: {product_name}")

        # ThreadPoolExecutor use karke 4 scrapers ko parallel run karenge
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Tasks submit karo
            future_to_site = {
                executor.submit(self._run_single_scraper, site, product_name, max_products): site 
                for site in self.active_scrapers
            }
            
            # Jaise-jaise result aaye, collect karo
            for future in concurrent.futures.as_completed(future_to_site):
                site = future_to_site[future]
                try:
                    data = future.result()
                    all_products.extend(data)
                except Exception as exc:
                    print(f"{site} generated an exception: {exc}")

        end_time = time.time()
        print(f"--- [COMPLETE] All scrapers finished in {end_time - start_time:.2f} seconds. Total products: {len(all_products)} ---")
        return all_products
