from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from requests.exceptions import SSLError
import pandas as pd
import re
from time import sleep
import csv

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--lang=ja-JP')
driver=webdriver.Chrome()

def check_ssl(url):
    try:
        response = requests.get(url, timeout=5)
        # HTTPSリクエストを送信し、SSL証明書を検証
        if response.url.startswith('https'):
            return True
        else:
            return False
    except SSLError:
        return False
    except requests.RequestException:
        return False
base_url='https://r.gnavi.co.jp/area/jp/noodle/rs/?p={}'
links = []

for i in range(1, 3):
    target_url = base_url.format(i)
    driver.get(target_url)
    sleep(10) 

    link_elements = driver.find_elements(By.CSS_SELECTOR, 'a.style_titleLink__oiHVJ')
    for element in link_elements:
        href = element.get_attribute('href')
        links.append(href)
        if len(links) >= 50:  # 50個のリンクに達したら終了
            break
    if len(links) >= 50:
        break

data_list = []
for link in links:
    ssl_status = check_ssl(link)

   # 変数の初期化
    name, phone, email, address, url = '', '', '', '', ''
    prefecture, city, street, building = '', '', '', ''

    try:
        driver.get(link)
        sleep(2)  # ページが完全に読み込まれるまで待つ

        # 店舗名を取得
        name_element = driver.find_element(By.TAG_NAME, 'h1')
        name = name_element.text.strip() if name_element else ''
        
        # 電話番号を取得
        phone_element = driver.find_element(By.CSS_SELECTOR, 'span.number')
        phone = phone_element.text.strip() if phone_element else ''

        url_element = driver.find_element(By.CSS_SELECTOR, 'a.sv-of.double')
        url = url_element.get_attribute('href')if url_element else ''

    
        # 住所を取得
        address_element = driver.find_element(By.CSS_SELECTOR, 'span.region')
        address = address_element.text.strip() if address_element else ''

        # 住所を分割
        pattern = re.compile(
            r'(?P<prefecture>北海道|東京都|京都府|大阪府|.{2,3}県)'  # 都道府県
            r'(?P<city>[\u3040-\u309F\u4E00-\u9FFF\u30A0-\u30FF]+)'  # 市区町村
            r'(?P<street>[0-9０-９]+(?:-[0-9０-９]+)*)'  # 番地
            r'(?:\s*(?P<building>[\u3040-\u309F\u4E00-\u9FFF\u30A0-\u30FFa-zA-Z0-9々〆〤ー\-]+))?'# 建物名（任意）
        )

        match = pattern.match(address)
        if match:
            prefecture = match.group('prefecture') or ''
            city = match.group('city') or ''
            street = match.group('street') or ''
            building = match.group('building') or ''
        else:
            print(f"Address did not match: {address}")

        data_list.append({
            '店舗名': name,
            '電話番号': phone,
            'メールアドレス': '',
            '都道府県': prefecture,
            '市区町村': city,
            '番地': street,
            '建物名': building,
            'URL': url,
            'SSL': ssl_status
        })

    except Exception as e:
        print(f"Error fetching page {link}: {e}")

    sleep(3)    
# ドライバを閉じる
driver.quit()

with open('/home/horikawa/sample.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['店舗名', '電話番号', 'メールアドレス', '都道府県', '市区町村', '番地', '建物名', 'URL', 'SSL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for data in data_list:
        writer.writerow(data)

print("Data has been written to /home/horikawa/sample.csv")



