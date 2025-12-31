
# utils/currency_converter.py
import re

class CurrencyConverter:
    def __init__(self):
        self.rates = {
            'USD': 83.2,  # USD to INR
            'EUR': 90.1,  # EUR to INR
            'GBP': 105.5, # GBP to INR
        }
    
    def convert_to_inr(self, price_text):
        """Convert any currency price to INR"""
        if not price_text:
            return price_text
        
        # Check for USD
        if '$' in price_text:
            try:
                amount = float(re.sub(r'[^\d.]', '', price_text))
                return amount * self.rates['USD']
            except:
                pass
        
        # Check for EUR
        if '€' in price_text:
            try:
                amount = float(re.sub(r'[^\d.]', '', price_text))
                return amount * self.rates['EUR']
            except:
                pass
        
        # Check for GBP
        if '£' in price_text:
            try:
                amount = float(re.sub(r'[^\d.]', '', price_text))
                return amount * self.rates['GBP']
            except:
                pass
        
        # If already in INR or unknown, return as is
        return price_text
