PriceScraper Pro 🛍️

An enterprise-grade price comparison web application that scrapes and compares product prices across major e-commerce platforms including Flipkart, Amazon, Croma, and Snapdeal.

✨ Features

Multi-Platform Scraping – Compare prices across 4+ major e-commerce websites

Intelligent Product Matching – Smart algorithms to group similar products

Price History Tracking – Monitor price changes over time

Wishlist Management – Save products and set price alerts

OCR Image Search – Upload product images to extract product names

AI-Powered Chat – Personalized product recommendations (optional)

User Authentication – Secure login & registration system

Analytics Dashboard – Track savings and search history

🛠️ Technology Stack

Backend: Flask (Python)

Database: SQLAlchemy with SQLite

Web Scraping: Selenium WebDriver with Chrome

Authentication: Flask-Login

Frontend: Bootstrap 5, HTML5, JavaScript

OCR: Tesseract via pytesseract

AI Integration: Google Generative AI (optional)

🚀 Installation
Clone the repository
git clone https://github.com/YOUR_USERNAME/price-comparison-web-app.git
cd price-comparison-web-app

Create & activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

Install dependencies
pip install -r requirements.txt

Configure environment variables
cp .env.example .env
# Update values as required

Run the application
python app.py


Open in browser:

http://localhost:5000

🔧 Configuration
| Variable       | Description             | Default             |
| -------------- | ----------------------- | ------------------- |
| SECRET_KEY     | Flask secret key        | dev-key             |
| DATABASE_URL   | Database connection     | sqlite:///db.sqlite |
| GOOGLE_API_KEY | AI API key *(optional)* | None                |
| FLASK_ENV      | Environment             | development         |
| PORT           | Server port             | 5000                |

📊 Supported Platforms
| Platform  | Status   | Features                |
| --------- | -------- | ----------------------- |
| Flipkart  | ✅ Active | Search, pricing, images |
| Amazon IN | ✅ Active | Search, pricing, images |
| Croma     | ✅ Active | Electronics comparison  |
| Snapdeal  | ✅ Active | General products        |

📁 Project Structure
compario /
├── app.py
├── requirements.txt
├── .env.example
├── scraper/
│   ├── base_scraper.py
│   ├── amazon_scraper.py
│   ├── flipkart_scraper.py
│   ├── croma_scraper.py
│   ├── snapdeal_scraper.py
│   └── scraper_manager.py
├── utils/
│   ├── currency_converter.py
│   └── product_matcher.py
├── templates/
│   ├── about.html
│   ├── analytics.html
│   ├── auth_base.html
│   ├── base.html
│   ├── contact.html
│   ├── features.html
│   ├── history.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── search.html
│   ├── wishlist_backup.html
│   └── wishlist.html
├── static/
│   ├── css/
│   │   ├── enterprise.css
│   │   ├── home.css
│   │   ├── platform.css
│   │   ├── search.css
│   │   ├── style.css
│   │   └── support.css
│   └── js/
│       ├── analytics.js 
│       ├── main.js
│       └── search.js
├── ocr_processor.py
├── Project Structure.txt
├── README.md
└── requirements.txt  

🛡️ Security Features

CSRF protection

Secure session handling

Input validation & sanitization

Password hashing (PBKDF2)

🐛 Troubleshooting

Scraping blocked? Some sites limit automated access

OCR not working? Ensure Tesseract is installed

Database errors? Delete instance/db.sqlite and restart

👩‍💻 Author

Shreya

This project was developed as a full-stack learning and portfolio project using Flask, Selenium, and modern web technologies.

Originally built during an academic internship and later refined for professional portfolio presentation.

📄 License

This project is licensed under the MIT License.

⚠️ Disclaimer

This application is for educational and portfolio purposes only.
Please respect the terms of service of the websites being scraped.

⭐ If You Like This Project

Give it a ⭐ on GitHub — it helps a lot!