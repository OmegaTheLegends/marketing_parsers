import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import datetime

logging.basicConfig(level=logging.INFO)
GECKO = '/opt/geckodriver' # linux
SAVE_FOLDER = '/opt/reports/wb_tags/' #linux
# GECKO = 'C:\\TEMP\\geckodriver.exe' # windows
# SAVE_FOLDER = 'C:\\TEMP\\' # windows

class WB_TAG:
    def __init__(self, item_list, ID_list, item_links):
        self.options = webdriver.FirefoxOptions()
        # user-agent
        self.options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
        self.options.headless = True
        # disable webdriver mode
        self.options.set_preference("dom.webdriver.enabled", False)
        self.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        self.ID_list = ID_list
        self.item_links = item_links
        self.item_list = item_list
        self.finish = []
        self.waitlist = []
        self.last_table = []
        self.stop = 0
        self.DF = pd.DataFrame()
        self.ROW = 1
        profile = webdriver.FirefoxProfile()
        # 1 - Allow all images        # 2 - Block all images        # 3 - Block 3rd party images 
        profile.set_preference("permissions.default.image", 2)
        self.driver = webdriver.Firefox(executable_path=GECKO, options=self.options, firefox_profile=profile)

    def refresh(self):
        trying = 0
        while trying != 5:
            trying += 1
            logging.info(f'page refresh {trying} time(s)')
            self.driver.refresh()
            time.sleep(4)
            html = self.driver.page_source
            soup = bs(html, 'lxml')
            try:
                notfound = soup.find('h1', class_='c-h2-v1').text
                notfound = notfound.strip()
                if 'ничего' in notfound:
                    continue
                else:
                    pass
            except:
                pass
            pageinfo = soup.find('div', id='app')
            pageinfo = pageinfo.find_all('div')
            if len(pageinfo) > 1:
                return html
            else:
                pass
        logging.info('def refresh failed')


    # Поисковой запрос, выяснение кол-ва страниц и проход по ним.
    def get_page_source(self,item):
        self.last_table.clear()
        self.stop = 0
        self.page = 1
        self.URL = f'https://www.wildberries.ru/catalog/0/search.aspx?search={item}&xsearch=true'
        self.driver.get(self.URL)
        time.sleep(10)
        html = self.driver.page_source
        self.soup = bs(html, 'lxml')
        self.SURL = self.driver.current_url
        try:
            pages = self.soup.find('span', class_='goods-count').find('span').text
            pages = pages.replace('\xa0','')
        except:
            html = self.refresh()
            html = self.driver.page_source
            self.soup = bs(html, 'lxml')
            self.SURL = self.driver.current_url
            pages = self.soup.find('span', class_='goods-count').find('span').text
            pages = pages.replace('\xa0','')
        if str(pages)[-2:] != '00':
            pages = int(pages) // 100
        else:
            pages = int(pages) // 100 -1
        self.pages = pages+1
        self.search_item(item) # поиск на первой странице
        logging.info(f'{item} - {pages+1} страниц')
        for i in range(int(pages)): # i+2
            if i == 98:
                logging.info(f'stop on page {self.page}')
                break
            else:
                pass
            pg = i+2
            if len(self.finish) == len(self.ID_list):
                logging.info(f'Найдены все нужные SKU для {item}')
                # self.driver.close()
                break
            else:
                pass
            html = self.driver.get(self.URL + f'&page={pg}')
            time.sleep(5)
            self.SURL = self.driver.current_url
            html = self.driver.page_source
            self.soup = bs(html, 'lxml')
            self.page = pg
            self.search_item(item)
        logging.info(f'Over on {self.page} from {pages + 1}')


    # Открытие ссылки, выяснение кол-ва страниц и проход по ним.
    def get_page_source_by_links(self,item):
        self.last_table.clear()
        self.stop = 0
        self.page = 1
        self.URL = item
        self.driver.get(self.URL)
        time.sleep(10)
        html = self.driver.page_source
        self.soup = bs(html, 'lxml')
        self.SURL = self.driver.current_url
        try:
            pages = self.soup.find('span', class_='goods-count').find('span').text
            pages = pages.replace('\xa0','')
        except:
            html = self.refresh()
            html = self.driver.page_source
            self.soup = bs(html, 'lxml')
            self.SURL = self.driver.current_url
            try:
                pages = self.soup.find('span', class_='goods-count').find('span').text
                pages = pages.replace('\xa0','')
            except:
                html = self.refresh()
                html = self.driver.page_source
                self.soup = bs(html, 'lxml')
                self.SURL = self.driver.current_url
                pages = self.soup.find('span', class_='goods-count').find('span').text
                pages = pages.replace('\xa0','')
        print('Не достал кол-во страниц')
        if str(pages)[-2:] != '00':
            pages = int(pages) // 100
        else:
            pages = int(pages) // 100 -1
        self.pages = pages+1
        self.search_item(item) # поиск на первой странице
        logging.info(f'{item} - {pages+1} страниц')
        for i in range(int(pages)): # i+2
            if self.stop == 1:
                logging.info(f'same IDs stop on page {self.page}')
                break
            else:
                pass
            pg = i+2
            if len(self.finish) == len(self.ID_list):
                logging.info(f'Найдены все нужные SKU для {item}')
                # self.driver.close()
                break
            else:
                pass
            old_pages = self.URL.split('?')[-1]
            old_pages = old_pages.split('&')
            for y in old_pages:
                if 'page=' in y:
                    old_page = y
                else:
                    pass
            next_page = self.URL
            next_page = next_page.replace(old_page,f'page={pg}')
            html = self.driver.get(next_page)
            time.sleep(5)
            self.SURL = self.driver.current_url
            html = self.driver.page_source
            self.soup = bs(html, 'lxml')
            self.page = pg
            self.search_item(item)
        logging.info(f'Over on {self.page} from {pages + 1}')



    # Поиск нужных ID на странице и запись в DF
    def search_item(self,item):
        try:
            table = self.soup.find('div', class_="product-card-overflow").find_all('div', class_='product-card')
        except:
            logging.info(f'Обновление страницы, не нашёл товары. Текущая {self.page}')
            html = self.refresh()
            self.SURL = self.driver.current_url
            html = self.driver.page_source
            self.soup = bs(html, 'lxml')
            table = self.soup.find('div', class_="product-card-overflow").find_all('div', class_='product-card')
            pass
        # if table == self.last_table and self.last_table != []:
        #     self.stop = 1
        # else:
        #     pass
        for i in range(len(table)):
            item_id = table[i].get('data-popup-nm-id')
            position = i + 1
            if item_id in self.ID_list:
                # print(f'Нашел {item_id}')
                self.finish.append(item_id)
                ID = item_id

                info_item = self.ITEMS.get(ID)
                name,price,stars,otziv,kolvo,imgs,opisanie = info_item

                self.DF.at[self.ROW,'TAG'] = str(item)
                self.DF.at[self.ROW,'ID'] = int(ID)
                self.DF.at[self.ROW,'PRICE'] = str(price)
                self.DF.at[self.ROW,'STARS'] = str(stars)
                self.DF.at[self.ROW,'REPORTS'] = str(otziv)
                self.DF.at[self.ROW,'BUYS'] = str(kolvo)
                self.DF.at[self.ROW,'IMG'] = str(imgs)
                self.DF.at[self.ROW,'POSITION'] = str(position)
                self.DF.at[self.ROW,'PAGE'] = str(self.page)
                self.DF.at[self.ROW,'ALL_PAGE'] = str(self.pages)
                self.DF.at[self.ROW,'SEARCH URL'] = str(self.SURL)
                self.DF.at[self.ROW,'NAME'] = str(name)
                self.DF.at[self.ROW,'OPISANIE'] = str(opisanie)
                self.ROW += 1
            else:
                pass
            self.last_table = table

    def check_waitlist(self,ID_list):
        self.ITEMS = {}
        for item in ID_list:
            self.driver.get(f'https://www.wildberries.ru/catalog/{str(item)}/detail.aspx?targetUrl=ST')
            time.sleep(7)
            html = self.driver.page_source
            soup = bs(html, 'lxml')
            try:
                notfound = soup.find('h1', class_='c-h2-v1').text
                notfound = notfound.strip()
                if 'ничего' in notfound:
                    logging.info('Обновляем т.к. не отобразился товар')
                    self.driver.refresh()
                    time.sleep(5)
                    html = self.driver.page_source
                    soup = bs(html,'lxml')
                    E404 = soup.find('div', class_='main__container').find('div').get('class')
                    if 'content404' in E404:
                        self.waitlist.append(item)
                        continue
                    else:
                        pass
            except:
                pass
            try:
                qvota = soup.find('pre').text
                qvota = qvota.strip()
                if 'exceeded' in qvota:
                    logging.info('Обновляем т.к. Requests quota exceeded')
                    self.refresh()
                    html = self.driver.page_source
                    soup = bs(html, 'lxml')
            except:
                pass
            button = soup.find('button', class_='btn-main hide').text.strip()
            if button == 'Добавить в корзину':
                self.waitlist.append(item)
            else:
                #### Добываем информацию со страницы
                body = self.driver.find_element_by_css_selector('body')
                # body.send_keys(Keys.PAGE_DOWN)
                # time.sleep(1.5)
                # body.send_keys(Keys.PAGE_DOWN)
                # time.sleep(1.5)
                # body.send_keys(Keys.PAGE_DOWN)
                # time.sleep(1.5)
                # body.send_keys(Keys.PAGE_DOWN)
                # time.sleep(2)
                html = self.driver.page_source
                soup = bs(html, 'lxml')
                try:
                    notfound = soup.find('h1', class_='c-h2-v1').text
                    notfound = notfound.strip()
                    if 'ничего' in notfound:
                        logging.info('Обновляем т.к. не отобразился товар2')
                        self.driver.refresh()
                        body = self.driver.find_element_by_css_selector('body')
                        # body.send_keys(Keys.PAGE_DOWN)
                        # time.sleep(1.5)
                        # body.send_keys(Keys.PAGE_DOWN)
                        # time.sleep(1.5)
                        # body.send_keys(Keys.PAGE_DOWN)
                        # time.sleep(1.5)
                        # body.send_keys(Keys.PAGE_DOWN)
                        # time.sleep(2.5)
                        html = self.driver.page_source
                        soup = bs(html, 'lxml')
                except:
                    pass
                name = soup.find('h1', class_='same-part-kt__header').find_all('span')[-1].text
                main = soup.find('div', class_='same-part-kt')
                imgs = main.find('ul', class_='swiper-wrapper')
                imgs = len(imgs)
                price = main.find('span', class_='price-block__final-price').text
                price = price.replace('&nbsp;','').replace('₽','').replace("\xa0","").strip()
                infos = soup.find('div', class_='same-part-kt__common-info')
                info_p = infos.find_all('p')
                for p in info_p:
                    cl = p.get('class')
                    if 'stars-line' in cl:
                        stars = p.text.strip()
                info_a = infos.find_all('a')
                for a in info_a:
                    cl = a.get('class')
                    if 'same-part-kt__count-review' in cl:
                        otziv = a.text.strip()

                kolvo = soup.find('p', class_='same-part-kt__order-quantity').text
                kolvo = kolvo.strip()
                opisanie = soup.find('div', class_='collapsable__content j-description').text
                self.ITEMS.update({item:[name,price,stars,otziv,kolvo,imgs,opisanie]})
                # print(f'{item=},{name=},{price=},{stars=},{otziv=},{kolvo=},{imgs=},{opisanie=}')

        # Удаляем все ID которых сейчас нет на сайте, из поиска.
        for id in self.waitlist:
            self.ID_list.remove(id)

    def start(self):
        for i in range(len(self.item_list)):
            try:
                self.item_list.remove('nan')
            except:
                pass
        for i in range(len(self.item_links)):
            try:
                self.item_links.remove('nan')
            except:
                pass
        for i in range(len(self.ID_list)):
            try:
                self.ID_list.remove('nan')
            except:
                pass
        self.check_waitlist(self.ID_list)
        for item in self.item_list:
            self.finish.clear()
            self.get_page_source(item)
            if len(self.finish) != len(self.ID_list):
                for id in self.ID_list:
                    if id not in self.finish:
                        self.DF.at[self.ROW,'TAG'] = str(item)
                        self.DF.at[self.ROW,'ID'] = str(id)
                        self.DF.at[self.ROW,'PRICE'] = str('not found')
                        self.DF.at[self.ROW,'STARS'] = str('-')
                        self.DF.at[self.ROW,'REPORTS'] = str('not found')
                        self.DF.at[self.ROW,'BUYS'] = str('-')
                        self.DF.at[self.ROW,'IMG'] = str('-')
                        self.DF.at[self.ROW,'POSITION'] = str('-')
                        self.DF.at[self.ROW,'PAGE'] = str('-')
                        self.DF.at[self.ROW,'ALL_PAGE'] = str(self.pages)
                        self.DF.at[self.ROW,'SEARCH URL'] = str('-')
                        self.DF.at[self.ROW,'NAME'] = str('-')
                        self.DF.at[self.ROW,'OPISANIE'] = str('-')
                        self.ROW += 1
            for w_id in self.waitlist:
                self.DF.at[self.ROW,'TAG'] = str(item)
                self.DF.at[self.ROW,'ID'] = str(w_id)
                self.DF.at[self.ROW,'PRICE'] = str('лист ожидания')
                self.DF.at[self.ROW,'STARS'] = str('-')
                self.DF.at[self.ROW,'REPORTS'] = str('not found')
                self.DF.at[self.ROW,'BUYS'] = str('-')
                self.DF.at[self.ROW,'IMG'] = str('-')
                self.DF.at[self.ROW,'POSITION'] = str('-')
                self.DF.at[self.ROW,'PAGE'] = str('-')
                self.DF.at[self.ROW,'ALL_PAGE'] = str('-')
                self.DF.at[self.ROW,'SEARCH URL'] = str('-')
                self.DF.at[self.ROW,'NAME'] = str('-')
                self.DF.at[self.ROW,'OPISANIE'] = str('-')
                self.ROW += 1


        # Все тоже самое только для LINKS
        for item in self.item_links:
            self.finish.clear()
            self.get_page_source_by_links(item)
            if len(self.finish) != len(self.ID_list):
                for id in self.ID_list:
                    if id not in self.finish:
                        self.DF.at[self.ROW,'TAG'] = str(item)
                        self.DF.at[self.ROW,'ID'] = str(id)
                        self.DF.at[self.ROW,'PRICE'] = str('not found')
                        self.DF.at[self.ROW,'STARS'] = str('-')
                        self.DF.at[self.ROW,'REPORTS'] = str('not found')
                        self.DF.at[self.ROW,'BUYS'] = str('-')
                        self.DF.at[self.ROW,'IMG'] = str('-')
                        self.DF.at[self.ROW,'POSITION'] = str('-')
                        self.DF.at[self.ROW,'PAGE'] = str('-')
                        self.DF.at[self.ROW,'ALL_PAGE'] = str(self.pages)
                        self.DF.at[self.ROW,'SEARCH URL'] = str('-')
                        self.DF.at[self.ROW,'NAME'] = str('-')
                        self.DF.at[self.ROW,'OPISANIE'] = str('-')
                        self.ROW += 1
            for w_id in self.waitlist:
                self.DF.at[self.ROW,'TAG'] = str(item)
                self.DF.at[self.ROW,'ID'] = str(w_id)
                self.DF.at[self.ROW,'PRICE'] = str('лист ожидания')
                self.DF.at[self.ROW,'STARS'] = str('-')
                self.DF.at[self.ROW,'REPORTS'] = str('not found')
                self.DF.at[self.ROW,'BUYS'] = str('-')
                self.DF.at[self.ROW,'IMG'] = str('-')
                self.DF.at[self.ROW,'POSITION'] = str('-')
                self.DF.at[self.ROW,'PAGE'] = str('-')
                self.DF.at[self.ROW,'ALL_PAGE'] = str('-')
                self.DF.at[self.ROW,'SEARCH URL'] = str('-')
                self.DF.at[self.ROW,'NAME'] = str('-')
                self.DF.at[self.ROW,'OPISANIE'] = str('-')
                self.ROW += 1

        self.driver.close()
        self.DF.to_excel(f'{SAVE_FOLDER}WB_TAGS_{datetime.datetime.today().strftime("%d.%m.%Y")}.xlsx')
        self.driver.quit()



def main():
    search_list = []
    search_links = []
    ID_list = []
    tag_list = pd.read_excel('/opt/MarketingBot/parsers/wb_tag/tags_wb.xlsx') #/opt/MarketingBot/parsers/wb_tag/
    # tag_list = pd.read_excel('tags_wb.xlsx') #/opt/MarketingBot/parsers/wb_tag/
    for y in tag_list.TAGS:
        search_list.append(str(y))
    for y in tag_list.LINKS:
        search_links.append(str(y))
    for i in tag_list.ID:
        if str(i).endswith('.0'):
            i = str(i).replace('.0','')
            ID_list.append(str(i))
        else:
            ID_list.append(str(i))
    wb = WB_TAG(search_list, ID_list, search_links)
    wb.start()

if __name__ == '__main__':
    main()
