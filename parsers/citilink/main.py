# coding: utf8
import requests
from bs4 import BeautifulSoup as bs
import xlsxwriter as xls
import datetime

class citi:
    def __init__(self):
        self.URL_BAT = "https://www.citilink.ru/catalog/batareiki/GP/"
        self.URL_BANK = 'https://www.citilink.ru/catalog/power-bank/GP/?view_type=grid&f=discount.any%2Crating.any'
        self.ROW = 1

    def pages(self,soup):
        try:
            pages = soup.find('div', class_='PaginationWidget__wrapper-pagination').find_all('a')[-2].text.strip()
            return pages
        except:
            return 1

    def get_info(self,soup,worksheet):
        all_items = soup.find('div', class_='ProductCardCategoryList__grid').find_all('div',class_='product_data__gtm-js')
        for item in all_items:
            metas = []
            try:
                meta_infos = item.find('div', class_='ProductCardVerticalMeta__opinions').find_all('div', class_='ProductCardVerticalMeta__info')
                for meta in meta_infos:
                    count = meta.find('span', class_='ProductCardVerticalMeta__count').text
                    count = count.replace('\n','').replace(' ','')
                    metas.append(count)
            except:
                metas.append('-')
                metas.append('-')
            try:
                div = item.get('data-params')
                ID = div.split(',"')
                DD = {}
                href = item.find('a').get('href')
                for i in ID:
                    i = i.replace('{','').replace('}','').replace('"','')
                    znak = i.split(':')
                    for y in znak:
                        DD.update({znak[0] : znak[1]})
                self.write_info(DD,href,metas,worksheet)
            except:
                pass



    def write_info(self,DD,href,metas, worksheet):
        worksheet.write(self.ROW, 0, 'https://www.citilink.ru'+href)
        worksheet.write(self.ROW, 1, DD.get('id'))
        worksheet.write(self.ROW, 2, DD.get('shortName'))
        worksheet.write(self.ROW, 3, DD.get('price'))
        worksheet.write(self.ROW, 4, DD.get('oldPrice'))
        worksheet.write(self.ROW, 5, DD.get('clubPrice'))
        if metas[0] != '-':
            worksheet.write(self.ROW, 6, metas[0])
        else:
            worksheet.write(self.ROW, 6, 'Нет оценки')
        if metas[1] != '-':
            worksheet.write(self.ROW, 7, metas[1])
        else:
            worksheet.write(self.ROW, 7, 'Нет отзывов')


        self.ROW += 1

    def start(self):
        date = datetime.datetime.today().strftime("%d.%m.%Y")

        workbook = xls.Workbook(f'/opt/reports/citilink/citilink_{date}.xlsx')
        # workbook = xls.Workbook(f'C:\\TEMP\\citilink_{date}.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, 'URL')
        worksheet.write(0, 1, 'id')
        worksheet.write(0, 2, 'shortName')
        worksheet.write(0, 3, 'price')
        worksheet.write(0, 4, 'oldPrice')
        worksheet.write(0, 5, 'clubPrice')
        worksheet.write(0, 6, 'stars')
        worksheet.write(0, 7, 'comments')

        response = requests.get(self.URL_BAT)
        response.encoding = response.apparent_encoding
        soup = bs(response.text, 'html.parser')
        page = int(self.pages(soup))
        for i in range(page):
            URL = self.URL_BAT + f'?p={i+1}'
            response = requests.get(URL)
            response.encoding = response.apparent_encoding
            soup = bs(response.text, 'html.parser')
            self.get_info(soup,worksheet)

        response = requests.get(self.URL_BANK)
        response.encoding = response.apparent_encoding
        soup = bs(response.text, 'html.parser')
        page = int(self.pages(soup))
        for i in range(page):
            URL = self.URL_BANK + f'?p={i+1}'
            response = requests.get(URL)
            response.encoding = response.apparent_encoding
            soup = bs(response.text, 'html.parser')
            self.get_info(soup,worksheet)
            #print(f'page {i+1} powerbank')

        workbook.close()

def main():
    CL = citi().start()

if __name__ == '__main__':
    CL = citi().start()
