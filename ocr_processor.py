
# ocr_processor.py
import pytesseract
from PIL import Image
import requests
from io import BytesIO
import os
import logging
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        """Initialize OCR processor with system-appropriate Tesseract configuration"""
        self.tesseract_available = self._configure_tesseract()
        
    def _configure_tesseract(self):
        """Configure Tesseract OCR executable path based on the operating system"""
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            # Common macOS installation paths
            possible_paths = [
                '/usr/local/bin/tesseract',  # Homebrew Intel
                '/opt/homebrew/bin/tesseract',  # Homebrew Apple Silicon
                '/usr/bin/tesseract'  # System installation
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract configured at: {path}")
                    return True
                    
        elif system == 'linux':
            # Common Linux paths
            possible_paths = [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract configured at: {path}")
                    return True
                    
        elif system == 'windows':
            # Windows paths
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract configured at: {path}")
                    return True
        
        # If no explicit path found, try system PATH
        try:
            import subprocess
            result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pytesseract.pytesseract.tesseract_cmd = result.stdout.strip()
                logger.info(f"Tesseract found in PATH: {result.stdout.strip()}")
                return True
        except Exception as e:
            logger.warning(f"Could not find tesseract in PATH: {e}")
        
        logger.error("Tesseract OCR executable not found. Please install Tesseract OCR.")
        return False
    
    def extract_text_from_image(self, image_file):
        """Extract product name from image using OCR"""
        
        # Check if Tesseract is available
        if not self.tesseract_available:
            logger.error("Tesseract OCR is not properly configured")
            raise Exception("Tesseract OCR is not available. Please install Tesseract OCR.")
        
        try:
            # Validate image file
            if not image_file:
                raise ValueError("No image file provided")
            
            # Open and process image
            if isinstance(image_file, str) and image_file.startswith('http'):
                # Download image from URL
                logger.info(f"Downloading image from URL: {image_file}")
                response = requests.get(image_file, timeout=10)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
            else:
                # Open local image file
                logger.info("Processing uploaded image file")
                img = Image.open(image_file)
            
            # Validate image
            if img.size[0] < 50 or img.size[1] < 50:
                raise ValueError("Image is too small for OCR processing")
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logger.info(f"Converted image from {img.mode} to RGB")
            
            logger.info(f"Processing image: {img.size[0]}x{img.size[1]} pixels")
            
            # Perform OCR with custom configuration for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '
            text = pytesseract.image_to_string(img, config=custom_config)
            
            # Clean and extract product name
            product_name = self.clean_ocr_text(text)
            
            if not product_name or product_name.strip() == "":
                logger.warning("OCR returned empty result, using fallback")
                return "mobile phone"
            
            logger.info(f"✅ OCR Extracted: {product_name}")
            return product_name
            
        except pytesseract.TesseractError as e:
            logger.error(f"Tesseract OCR Error: {e}")
            raise Exception(f"OCR processing failed: {str(e)}")
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise Exception(f"Failed to process image: {str(e)}")
    
    def clean_ocr_text(self, text):
        """Clean and process OCR text to extract meaningful product name"""
        import re
        
        if not text or not text.strip():
            return ""
        
        # Split into lines and clean
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        if not lines:
            return ""
        
        # Join all lines to analyze complete text
        full_text = ' '.join(lines)
        
        # Remove special characters and excessive whitespace
        cleaned_text = re.sub(r'[^\w\s-]', ' ', full_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Common OCR error corrections
        corrections = {
            r'\bl\b': 'I',  # standalone l to I
            r'\b0\b': 'O',  # standalone 0 to O
            r'iph0ne': 'iphone',
            r'1phone': 'iphone',
            r'sarnsung': 'samsung',
            r'xia0mi': 'xiaomi',
            r'realrne': 'realme',
            r'0ppo': 'oppo',
            r'v1vo': 'vivo',
            r'h0n0r': 'honor',
            r'm0t0': 'moto'
        }
        
        for pattern, replacement in corrections.items():
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
        
        # Look for product-related keywords
        product_keywords = [
            'iphone', 'samsung', 'galaxy', 'pixel', 'oneplus', 'xiaomi', 
            'realme', 'oppo', 'vivo', 'honor', 'moto', 'motorola', 'nokia',
            'apple', 'huawei', 'redmi', 'poco', 'asus', 'sony', 'lg',
            'mobile', 'phone', 'smartphone', 'tablet', 'ipad', 'watch',
            'earbuds', 'headphones', 'laptop', 'computer', 'monitor'
        ]
        
        # Find the most relevant line containing product keywords
        best_match = ""
        max_keywords = 0
        
        for line in lines:
            line_clean = re.sub(r'[^\w\s-]', ' ', line).lower()
            keyword_count = sum(1 for keyword in product_keywords if keyword in line_clean)
            
            if keyword_count > max_keywords or (keyword_count == max_keywords and len(line.strip()) > len(best_match)):
                max_keywords = keyword_count
                best_match = line.strip()
        
        # If no keywords found, use the first substantial line
        if not best_match and lines:
            # Find the longest line with meaningful content
            for line in lines:
                if len(line.strip()) > 3 and not line.isdigit():
                    best_match = line.strip()
                    break
        
        # Final cleanup
        if best_match:
            result = re.sub(r'[^\w\s-]', ' ', best_match)
            result = re.sub(r'\s+', ' ', result).strip()
            
            # Apply corrections again
            for pattern, replacement in corrections.items():
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            
            return result if len(result) > 2 else "mobile phone"
        
        return "electronic product"
