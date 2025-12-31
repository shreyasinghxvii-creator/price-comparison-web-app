
# utils/product_matcher.py
import re

class ProductMatcher:

    def normalize_name(self, name):
        """Clean and simplify product name for matching."""
        name_lower = name.lower()
        # Remove special characters
        name_lower = re.sub(r'[^\w\s]', ' ', name_lower)
        # Remove common words
        name_lower = re.sub(r'\b(apple|samsung|sony|new|latest|model)\b', '', name_lower)
        # Remove (color, storage)
        name_lower = re.sub(r'\([\w\s,]+\)', '', name_lower)
        return name_lower.strip()

    def create_product_key(self, product_name):
        """Create a smart, unique key from product name."""
        name_lower = product_name.lower()
        
        # --- Model Extraction (Example: iPhone 15, S24 Ultra) ---
        model = "unknown_model"
        # iPhone
        model_match = re.search(r'(iphone\s*(\d+\s*(pro|plus|max)?))', name_lower)
        if model_match:
            model = "iphone_" + re.sub(r'\s', '', model_match.group(2)) # 'iphone_15pro'
        else:
            # Samsung
            model_match = re.search(r'(galaxy\s*(s\d+\s*(ultra|plus)?))', name_lower)
            if model_match:
                model = "galaxy_" + re.sub(r'\s', '', model_match.group(2)) # 'galaxy_s24ultra'
            else:
                # General fallback (first 3 words)
                model = "_".join(self.normalize_name(name_lower).split()[:3])

        # --- Storage Extraction (Example: 128GB, 256 GB, 1 TB) ---
        storage = "unknown_storage"
        storage_match = re.search(r'(\d+)\s*(gb|tb)', name_lower)
        if storage_match:
            storage = f"{storage_match.group(1)}{storage_match.group(2)}" # '128gb'

        key = f"{model}_{storage}"
        
        # Agar key valid nahi hai, toh fallback use karo
        if key == "unknown_model_unknown_storage":
             return "_".join(self.normalize_name(name_lower).split()[:4]) # Fallback
        return key

    def get_group_display_name(self, group_key, products):
        """Create a readable group name from the key."""
        # Group ke sabse chhota naam ko display name banate hain
        if products:
            shortest_name = min(products, key=lambda x: len(x['name']))['name']
            # Zyada lamba hai toh short karo
            return shortest_name[:70] + "..." if len(shortest_name) > 70 else shortest_name
        
        return group_key.replace("_", " ").upper() # Fallback

    def group_products_for_display(self, products):
        """Group products for comparison display"""
        groups = {}
        for product in products:
            key = self.create_product_key(product['name'])
            if key not in groups:
                groups[key] = []
            groups[key].append(product)

        final_products = []
        for group_key, group_products in groups.items():
            if group_products:
                group_name = self.get_group_display_name(group_key, group_products)
                
                min_price = min(p['price'] for p in group_products)
                for product in group_products:
                    product['lowest_in_group'] = (product['price'] == min_price)
                    product['group_size'] = len(group_products)
                    product['group_key'] = group_key
                    product['group_name'] = group_name # Readable name add karo
                
                final_products.extend(group_products)
                
        if final_products:
            global_min = min(p['price'] for p in final_products)
            for product in final_products:
                product['lowest_overall'] = (product['price'] == global_min)
                
        return final_products
