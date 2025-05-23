
# 📢 TPO Notification Scraper and Email Alert System

This Python script automates the process of scraping the latest notices and circulars from the **Training and Placement Office (TPO) page** of **ZHCET, AMU**. It downloads newly posted PDF files, keeps a record to avoid duplicates, and sends an email with the new notices as attachments.

## 🎯 Why I Made This Project

As a third-year Electrical Engineering student at ZHCET, AMU, I noticed that keeping up with new notices from the Training and Placement Office can be tedious and error-prone. This project was built to automate the process of checking and downloading notices so that no important opportunity is missed.

## 🚀 Features

- ✅ Automatically scrapes new notices from the TPO ZHCET website
- 📥 Downloads and temporarily stores new PDF files
- 📋 Keeps a log of already downloaded files (in `notifications.csv`)
- 📧 Sends an email alert with notice details and attached PDFs

## 🌐 Target Website

[https://www.amu.ac.in/training-and-placement/zhcet/notice-and-circular](https://www.amu.ac.in/training-and-placement/zhcet/notice-and-circular)


## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/tpo-notice-scraper.git
cd tpo-notice-scraper
```

### 2. Install Required Libraries

Make sure you have Python installed, then run:

```bash
pip install selenium requests
```

Also, make sure Google Chrome is installed, and download the appropriate [ChromeDriver](https://chromedriver.chromium.org/downloads) version and place it in your system PATH.

### 3. Set environment variables

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
TO_EMAIL=recipient_email@gmail.com
```

> ⚠️ Use an **App Password** if you’re using Gmail with 2-factor authentication.


## ▶️ Running the Script

Simply run:

```bash
python main.py
```

The script will:
- Scrape the latest notices
- Download PDFs
- Send an email with notice titles, dates, and attachments
- Keeps a log of already downloaded files in 'notification.csv'
- Clean up downloaded files afterward



## 👨‍💻 Author

**Mukhtar Khan**  
ML ENTHUSIAST  


## 📘 Disclaimer

This project is created **solely for educational purposes**. It is intended to demonstrate web scraping, automation with Selenium, and sending emails via SMTP in Python. It is **not affiliated with or endorsed by AMU or ZHCET**. Please use it responsibly and only for personal use.