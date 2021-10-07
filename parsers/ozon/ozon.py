from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas
import time, datetime

class ozon:
    def __init__(self):
        self.URL = 'https://www.ozon.ru/seller/ooo-a-zet-1657/products/'
        self.GECKO = '/opt/geckodriver' # linux
        # self.GECKO = 'C:\\python\\geckodriver.exe' # windows
        self.SAVE_FOLDER = '/opt/reports/ozon/' #linux 
        # self.SAVE_FOLDER = 'C:\\TEMP\\' # windows
        self.main_url = 'https://www.ozon.ru'

        self.DF = pandas.DataFrame()

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }


        self.options = webdriver.FirefoxOptions()
        # user-agent
        self.options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
        self.options.headless = True
        # disable webdriver mode
        self.options.set_preference("dom.webdriver.enabled", False)
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("permissions.default.image", 2)


    def get_info_from_page(self,soup):
        body = soup.find_all('div', class_='a0c4')
        time.sleep(1)
        for i in range(len(body)):
            try:
                href = self.main_url + body[i].find('a', class_='a0v2').get('href')
            except:
                href = None
            try:
                fotos = body[i].find('div', class_='a1k2').find_all('span')
                fotos = len(fotos)
            except:
                fotos = None
            try:
                price = body[i].find('span', class_='b5v6 b5v7 c4v8').text
                price = price.replace(' ₽','')
            except:
                price = None
            try:
                name = body[i].find('span', class_='j4 as3 az a0f2 f-tsBodyL item b3u9').text
                if 'GP' in name:
                    brand = 'GP'
                elif 'СТАРТ' in name:
                    brand = 'СТАРТ'
                elif 'Маруся' in name:
                    brand = 'Маруся'
                elif 'Pompea' in name:
                    brand = 'Pompea'
                elif 'Marussia' in name:
                    brand = 'Marussia'
                elif 'Femina' in name:
                    brand = 'Femina'
                elif 'DR.Safe' in name:
                    brand = 'DR.Safe'
                else: brand = ''
            except:
                name = None
                brand = ''
            try:
                stars = body[i].find('div', class_='_3xol').get('style')
                stars = stars.replace('width:','').replace(';','')
            except:
                stars = None
            try:
                reports = body[i].find('a', class_='a1r7').text
            except:
                reports = None
            # print(href, fotos, price, name, stars, reports, brand)
            self.DF.at[self.ROW,'URL'] = str(href)
            self.DF.at[self.ROW,'NAME'] = str(name)
            self.DF.at[self.ROW,'PRICE'] = str(price)
            self.DF.at[self.ROW,'STARS'] = str(stars)
            self.DF.at[self.ROW,'REPORTS'] = str(reports)
            self.DF.at[self.ROW,'FOTOS'] = str(fotos)
            self.DF.at[self.ROW,'BRAND'] = str(brand)

            self.ROW += 1

    def next_page(self):
        self.page += 1
        self.next_p = 'None'
        self.drive.get(self.URL + f'?page={self.page}')
        time.sleep(4)
        self.html = self.drive.page_source
        soup = bs(self.html, 'lxml')
        try:
            self.next_p = soup.find('div', class_='b9i0 _2avF').get('qa-id')
        except:
            pass
        self.get_info_from_page(soup)


    def main(self):
        self.page = 1
        self.ROW = 1
        self.drive = webdriver.Firefox(executable_path=self.GECKO, options=self.options, firefox_profile=self.profile)
        self.drive.get(self.URL)
        time.sleep(4)
        self.html = self.drive.page_source
        soup = bs(self.html, 'lxml')
        self.get_info_from_page(soup)
        try:
            self.next_p = soup.find('div', class_='b9i0 _2avF').get('qa-id')
        except:
            self.next_p = 'None'
        while self.next_p == 'next':
            self.next_page()
        time.sleep(15)
        self.drive.close()
        self.DF.to_excel(f'{self.SAVE_FOLDER}Ozon_{datetime.datetime.today().strftime("%d.%m.%Y")}.xlsx')

if __name__ == '__main__':
    oz = ozon()
    oz.main()

def start():
    oz = ozon()
    oz.main()
