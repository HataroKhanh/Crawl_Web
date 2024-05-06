from bs4 import BeautifulSoup
import requests
import json 
import base64
from io import BytesIO
from PIL import Image
import pytesseract
from collections import defaultdict
import sys
import time



hanoi = defaultdict(lambda: defaultdict(dict))

url = "https://www.tratencongty.com/thanh-pho-ha-noi/"
response  = requests.get(url)


def regex(soup):
    address = soup.find(text=lambda t: "Địa chỉ:" in t)
    address = address.split(":")[1].strip()
    representative = soup.find(text=lambda t: "Đại diện pháp luật:" in t)
    representative = representative.split(":")[1].strip()
    #print(soup)
    return (address,representative)

def base_64_convert(data,file_name):
    data = data.split(',')[1]
    data = data.encode('utf-8')
    data = base64.decodebytes(data)
    with open(f'{file_name}.jpg', 'wb') as image_file:
        image_file.write(data)
    return

def img_to_text(file_name):
    img = Image.open(f'{file_name}.jpg')
    return pytesseract.image_to_string(img, config='--psm 6')

try:
    if response.status_code == 200:
        html_quan = BeautifulSoup(response.content,features="html.parser")
        table_quan = html_quan.findAll('a',class_="list-group-item")

        for tag_table_quan in table_quan[2:]:
            name_quan = tag_table_quan.get("href").split('/')[-2].replace('-','_')
            title_quan = tag_table_quan.get('title') 
            url_quan = tag_table_quan.get('href')
            print(f'{title_quan}:')

            response_phuong = requests.get(url_quan)
            if response_phuong.status_code==200:
                html_phuong = BeautifulSoup(response_phuong.content,features="html.parser")
                table_phuong = html_phuong.findAll('a','list-group-item')
                for tag_table_phuong in table_phuong[2:]:
                    name_phuong = tag_table_phuong.get('href').split('/')[-2].replace('-','_')
                    title_phuong = tag_table_phuong.get('title')
                    url_phuong = tag_table_phuong.get('href')
                    
                    page = 1
                    list_companies = []
                    name_companies_dict = defaultdict(lambda:0)
                    while 1:
                        response_page = requests.get(url_phuong + f'?page={page}')
                        html_companies = BeautifulSoup(response_page.content,features="html.parser")
                        html_company_class = html_companies.findAll('div',class_="search-results")
                        if html_company_class != []:
                            for tag_div_companies in html_company_class:
                                tag_a_company = tag_div_companies.find('a')
                                url_company = tag_a_company.get('href')

                                response_company = requests.get(url_company)
                                if response_company.status_code == 200:
                                    html_company = BeautifulSoup(response_company.content,features="html.parser")
                                    table_company = html_company.find(class_="jumbotron")
                                    tag_img_company =  table_company.findAll('img')
                                    name_company = table_company.find('span').text
                                    if name_company in name_companies_dict:
                                        name_company =  name_company+str(name_companies_dict[name_company]+1)
                                    
                                    address,representative = regex(table_company)
                                    try:
                                        phone_data64_img =  tag_img_company[1].get('src')
                                        base_64_convert(phone_data64_img,name_company)
                                        phone_number=img_to_text(name_company)
                                    except Exception as e:
                                        phone_number = "No PhoneNumber"
                                    
                                    dict_company = {"Tên công ty":name_company,
                                                    "Đại diện pháp luật":representative,
                                                    "Địa chỉ":address,
                                                    "Số điện thoại":phone_number.replace('\n','').replace("\x0c","")
                                        }
                                    
                                    list_companies.append(dict_company)
                                    print(dict_company)
                                    print()
                                    time.sleep(2)
                        else:
                            hanoi[title_quan][title_phuong] = list_companies
                            json_object = json.dumps(hanoi, indent=4, ensure_ascii=False)
                            # Writing to sample.json
                            with open("sample.json", "w" , encoding="utf-16") as outfile:
                                outfile.write(json_object)
                            sys.exit(0)
                        time.sleep(120)
                        page+=1

                    hanoi[title_phuong][title_quan] = list_companies
except Exception as e:
    hanoi[title_quan][title_phuong] = list_companies
    json_object = json.dumps(hanoi, indent=4, ensure_ascii=False)
    with open("sample.json", "w" , encoding="utf-16") as outfile:
        outfile.write(json_object)

                    


        
