import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
from requests.exceptions import SSLError
import csv

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

base_url = 'https://r.gnavi.co.jp/area/jp/japanese/rs/?p={}'
links = []

for i in range(1, 3):
    target_url = base_url.format(i)
    response = requests.get(target_url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.content, 'html.parser')

    for link in soup.find_all('a', class_='style_titleLink__oiHVJ'):
        href = link.get('href')
        if href.startswith('https'):
            links.append(href)
        if len(links) >= 50:  # 50個のリンクに達したら終了
            break
    if len(links) >= 50:
        break

data_list = []
for link in links:
    ssl_status = check_ssl(link)
    
    # 初期化
    name, phone, email, address = '', '', '', ''
    prefecture, city, street, building = '', '', '', ''

    try:
        res = requests.get(link)
        res.encoding = res.apparent_encoding
        page_soup = BeautifulSoup(res.content, 'html.parser')

        name = page_soup.find('h1').text.strip() if page_soup.find('h1') else ''
        phone = page_soup.find('span', class_='number').text.strip() if page_soup.find('span', class_='number') else ''
        address = page_soup.find('span', class_='region').text.strip() if page_soup.find('span', class_='region') else ''

        pattern = re.compile(
            r'(?P<prefecture>北海道|東京都|京都府|大阪府|.{2,3}県)'  # 都道府県
            r'(?P<city>[\u3040-\u309F\u4E00-\u9FFF\u30A0-\u30FF]+)'  # 市区町村
            r'(?P<street>[0-9０-９]+(?:-[0-9０-９]+)*)'  # 番地
            r'(?:\s*(?P<building>[\u3040-\u309F\u4E00-\u9FFF\u30A0-\u30FFa-zA-Z0-9々〆〤ー\-]+))?'# 建物名（任意）
        )

        match = re.search(pattern, address)
        
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
            'URL': '',
            'SSL': ssl_status
        
        })
        

        sleep(3)  # サーバーに対するリクエストの間隔をあける

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {link}: {e}")

output_csv_path = '/home/horikawa/output.csv'
with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['店舗名', '電話番号', 'メールアドレス', '都道府県', '市区町村', '番地', '建物名', 'URL', 'SSL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for data in data_list:
        writer.writerow(data)

print(f"Data has been written to {output_csv_path}")



