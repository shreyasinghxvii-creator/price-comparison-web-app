# 🔐 Security Policy

## Supported Versions

Currently, only the latest version of PriceScraper Pro is supported with security updates.

| Version | Supported |
| :--- | :--- |
| 1.0.x | ✅ Yes |
| < 1.0 | ❌ No |

## Reporting a Vulnerability

This project is developed for **educational and portfolio purposes**. 

If you discover a potential security issue, please **do not open a public GitHub issue**. Instead, please report it by contacting the repository owner through GitHub or via the email associated with this profile. 

All reports will be reviewed responsibly, and I will aim to address significant issues in a timely manner.

## Best Practices for Users

To keep your local setup secure, please follow these guidelines:

* **Environment Variables:** Never commit `.env` files to a public repository. These contain sensitive keys such as `SECRET_KEY` or `GOOGLE_API_KEY`.
* **Database Security:** If running locally, ensure the SQLite database file (`db.sqlite`) has appropriate file permissions.
* **Dependencies:** Regularly update your dependencies using `pip install --upgrade -r requirements.txt` to avoid known vulnerabilities in Flask, Selenium, or other third-party packages.

## ⚠️ Ethical Scraping Disclaimer

This project is intended **strictly for educational use**. 

Users are solely responsible for complying with the **Terms of Service** of the websites being scraped (e.g., Amazon, Flipkart, Croma, Snapdeal). This tool should not be used for:
1. Malicious activity or data harvesting.
2. High-frequency/excessive scraping that impacts site performance.
3. Any actions that violate platform robots.txt policies.

The author assumes no liability for misuse of this application.


Add SECURITY.md policy
