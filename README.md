# 🛍️ PriceScraper Pro
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/framework-flask-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

An enterprise-grade **price comparison web application** that scrapes and compares product prices across major e-commerce platforms including **Flipkart, Amazon, Croma, and Snapdeal**.

---

## ✨ Features

- **Multi-Platform Scraping** – Compare prices across 4+ major e-commerce websites  
- **Intelligent Product Matching** – Smart algorithms to group similar products  
- **Price History Tracking** – Monitor price changes over time  
- **Wishlist Management** – Save products and set price alerts  
- **OCR Image Search** – Upload product images to extract product names  
- **AI-Powered Chat** – Personalized product recommendations *(optional)*  
- **User Authentication** – Secure login & registration system  
- **Analytics Dashboard** – Track savings and search history  

---

## 🛠️ Technology Stack

- **Backend:** Flask (Python)  
- **Database:** SQLAlchemy with SQLite  
- **Web Scraping:** Selenium WebDriver with Chrome  
- **Authentication:** Flask-Login  
- **Frontend:** Bootstrap 5, HTML5, JavaScript  
- **OCR:** Tesseract via pytesseract  
- **AI Integration:** Google Generative AI *(optional)*  

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/shreyasinghxvii-creator/price-comparison-web-app.git
cd price-comparison-web-app
```

### 2️⃣ Create & activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS / Linux
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables

```bash
cp .env.example .env
# Update values as required
```

### 5️⃣ Run the application

```bash
python app.py
```

Open in browser: **http://localhost:5000**

---

## 🔧 Configuration

| Variable       | Description             | Default             |
|----------------|-------------------------|---------------------|
| SECRET_KEY     | Flask secret key        | dev-key             |
| DATABASE_URL   | Database connection     | sqlite:///db.sqlite |
| GOOGLE_API_KEY | AI API key *(optional)* | None                |
| FLASK_ENV      | Environment             | development         |
| PORT           | Server port             | 5000                |

---

## 📊 Supported Platforms

| Platform  | Status    | Features                |
|-----------|-----------|-------------------------|
| Flipkart  | ✅ Active | Search, pricing, images |
| Amazon IN | ✅ Active | Search, pricing, images |
| Croma     | ✅ Active | Electronics comparison  |
| Snapdeal  | ✅ Active | General products        |

---

## 📁 Project Structure

```
compario/
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
├── static/
├── ocr_processor.py
└── README.md
```

---

## 🛡️ Security Features

- CSRF protection
- Secure session handling
- Input validation & sanitization
- Password hashing (PBKDF2)

---

## 🐛 Troubleshooting

**Scraping blocked?**  
Some sites limit automated access. Try adjusting request delays or rotating User-Agent headers.

**OCR not working?**  
Ensure Tesseract is installed and properly configured in your system PATH.

**Database errors?**  
Delete `instance/db.sqlite` and restart the application to reinitialize the database.

---

## 👩‍💻 Author

**Shreya**

Developed as a full-stack learning and portfolio project using Flask, Selenium, and modern web technologies.

Originally built during an academic internship and later refined for professional portfolio presentation.

---

## 📄 License

This project is licensed under the MIT License.

---

## ⚠️ Disclaimer

This application is for educational and portfolio purposes only.  
Please respect the terms of service of the websites being scraped.