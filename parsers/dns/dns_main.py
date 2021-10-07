from selenium import webdriver
from bs4 import BeautifulSoup as bs
import xlsxwriter as xls
import time
import datetime

class dns_main:
    def __init__(self):
        self.URL = 'https://www.dns-shop.ru/brand-zone/gp/'
        self.MAIN_URL = 'https://www.dns-shop.ru'
        self.GECKO = '/opt/geckodriver' # linux
        self.SAVE_FOLDER = '/opt/reports/dns/' #linux 
        # self.GECKO = 'C:\\TEMP\\geckodriver.exe' # windows
        # self.SAVE_FOLDER = 'C:\\TEMP\\' # windows
        self.ROW = 1

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
        self.options.binary_location = "/usr/bin/firefox"
        self.options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
        self.options.headless = True
        # disable webdriver mode
        self.options.set_preference("dom.webdriver.enabled", False)
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("permissions.default.image", 2)


    def get_elems(self,soup):
        elements = soup.find('nav', class_='brand-zone-categories').find_all('div', class_='brand-zone-categories__container')
        list_elem = []
        for i in elements:
            try:
                url = i.find('a', href=True)
                url = url['href']
                if self.MAIN_URL + url in list_elem:
                    pass
                else:
                    list_elem.append(self.MAIN_URL + url)
            except:
                pass
        return list_elem

    def write(self,elm_url, name, price, stars, otziv, worksheet):
        worksheet.write(self.ROW, 0, self.MAIN_URL + elm_url)
        worksheet.write(self.ROW, 1, name)
        worksheet.write(self.ROW, 2, price)
        worksheet.write(self.ROW, 3, stars)
        worksheet.write(self.ROW, 4, otziv)
        self.ROW += 1

    def get_info_from_page(self,soup, worksheet):
        page_elm = soup.find('div', class_='products-page__list').find_all('div', class_='catalog-product')
        for elm in page_elm:
            elm_name_url = elm.find('a', class_='catalog-product__name', href=True)
            elm_url = elm_name_url['href'] # link
            name = elm_name_url.find('span').text #name
            stars_otziv = elm.find('div', class_='catalog-product__stat').find('a', class_='catalog-product__rating')
            stars = stars_otziv['data-rating'] # stars
            otziv = stars_otziv.text # otzivov
            try:
                price = elm.find('div', class_='product-buy__price').text
            except:
                price = ''
            self.write(elm_url, name, price, stars, otziv, worksheet)

    def get_pages(self,soup):
        try:
            pages = soup.find('ul', class_='pagination-widget__pages').find_all('li')
            pages = int(pages[-1]['data-page-number'])
        except:
            pages = 1
        return pages

    def start(self):

        driver = webdriver.Firefox(executable_path=self.GECKO, options=self.options, firefox_profile=self.profile)
        date = datetime.datetime.today().strftime("%d.%m.%Y")

        workbook = xls.Workbook(f'{self.SAVE_FOLDER}dns_{date}.xlsx') 
        worksheet = workbook.add_worksheet() 
        worksheet.write(0, 0, 'URL')
        worksheet.write(0, 1, 'NAME')
        worksheet.write(0, 2, 'PRICE')
        worksheet.write(0, 3, 'STARS')
        worksheet.write(0, 4, 'COMMENTS')

        try:
            driver.get(self.URL)
            time.sleep(5)
            src = driver.page_source
            soup = bs(src, 'lxml')
            list_elem = self.get_elems(soup) # get list of elements on main GP page
            # print(list_elem)
            for url in list_elem:
                driver.get(url)
                time.sleep(5)
                src = driver.page_source
                soup = bs(src, 'lxml')
                pages = self.get_pages(soup)
                if pages == 1:
                    self.get_info_from_page(soup,worksheet)
                    pass
                elif pages > 1:
                    self.get_info_from_page(soup,worksheet)
                    for i in range(pages-1):
                        driver.get(url + f'&p={i+2}')
                        time.sleep(5)
                        src = driver.page_source
                        soup = bs(src, 'lxml')
                        self.get_info_from_page(soup,worksheet)

                else:
                    print('wtf')


        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()
        workbook.close()

def main():
    DNS = dns_main()
    DNS.start()


if __name__ == '__main__':
    DNS = dns_main()
    DNS.start()
