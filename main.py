import os
import re
import time
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.message import EmailMessage

# Configuration
URL = "https://www.amu.ac.in/training-and-placement/zhcet/notice-and-circular"
MAX_PAGES = 1
CSV_FILE = "notifications.csv"
TEMP_DIR = "temp_pdfs"
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver

def load_existing_notifications():
    existing = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing.add(row['filename'])
    return existing

def save_notifications(new_notices):
    fieldnames = ['title', 'date', 'filename', 'link']
    
    csv_notices = []
    for notice in new_notices:
        csv_notices.append({
            'title': notice['title'],
            'date': notice['date'],
            'filename': notice['filename'],
            'link': notice['link']
        })
    
    existing_data = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_data = list(reader)

    # Combine new and existing notices
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_notices + existing_data)

def extract_pdf_data(driver, session):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
    )
    
    pdf_data = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    
    for row in rows:
        try:
            title = row.find_element(By.CSS_SELECTOR, "td.list-a strong").text.strip()
            date = row.find_element(By.CSS_SELECTOR, "td.upload-a .date-column").text.strip()
            download_btn = row.find_element(By.CSS_SELECTOR, "td.download-a a")
            
            driver.execute_script("""
                window.capturedUrl = null;
                window.originalOpen = window.open;
                window.open = function(url) {
                    window.capturedUrl = url;
                };
            """)
            download_btn.click()
            time.sleep(1)
            pdf_url = driver.execute_script("return window.capturedUrl;")
            driver.execute_script("window.open = window.originalOpen;")
            
            response = session.head(pdf_url, allow_redirects=True)
            if "Content-Disposition" in response.headers:
                filename = re.findall(r"filename\*?=(?:UTF-8'')?\"?([^\"]+)", 
                                    response.headers["Content-Disposition"])[0]
            else:
                filename = os.path.basename(pdf_url).split("?")[0]
            
            pdf_data.append({
                'title': title,
                'date': date,
                'filename': filename,
                'link': pdf_url 
            })
            
        except Exception as e:
            print(f"Error processing row: {str(e)}")
            continue
    
    return pdf_data

def download_pdf(url, session, filename):
    os.makedirs(TEMP_DIR, exist_ok=True)
    filepath = os.path.join(TEMP_DIR, filename)
    
    response = session.get(url, stream=True)
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return filepath

def send_email(new_notices):
    msg = EmailMessage()
    msg["Subject"] = f"New TPO_ZHCET Notifications ({len(new_notices)} New)"
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL

    # Email Body
    email_body = "New Notifications:\n\n"
    for notice in new_notices:
        email_body += (
            f"Title: {notice['title']}\n"
            f"Date: {notice['date']}\n"
            f"Link: {notice['link']}\n\n"
        )

    msg.set_content(email_body)

    # Attachments
    for notice in new_notices:
        file_path = os.path.join('temp_pdfs', notice['filename'])
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(
                    file_data,
                    maintype='application',
                    subtype='pdf',
                    filename=notice['filename']
                )
        else:
            print(f"Warning: File not found - {file_path}")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
def main():
    driver = setup_driver()
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
    
    
    driver.get(URL)
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])
    
    existing_files = load_existing_notifications()
    new_notices = []

    try:
        page_count = 0
        while page_count < MAX_PAGES:
            page_count += 1
            print(f"Processing page {page_count}")
            
            pdf_entries = extract_pdf_data(driver, session)
            for entry in pdf_entries:
                if entry['filename'] not in existing_files:
                    print(f"New notice found: {entry['filename']}")
                    filepath = download_pdf(entry['link'], session, entry['filename'])
                    entry['filepath'] = filepath
                    new_notices.append(entry)
            
           
            try:
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'pagination-next'))
                )
                next_btn.click()
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
                )
                time.sleep(2)
            except Exception as e:
                print(f"Pagination error: {str(e)}")
                break

        if new_notices:
            save_notifications(new_notices)
            print("Sending Mail....")
            send_email(new_notices)
            print(f"Sent email with {len(new_notices)} new notifications")
        else:
            print("No new notifications found")

    finally:
        driver.quit()
        for notice in new_notices:
            try:
                os.remove(notice['filepath'])
            except Exception as e:
                print(f"Error deleting temp file: {str(e)}")

if __name__ == "__main__":
    main()