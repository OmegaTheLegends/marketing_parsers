import requests, datetime, json, time
import pandas as pd
from bs4 import BeautifulSoup as bs

class VSEINSTR:
    def __init__(self, ID, r_ses):
        self.ID = ID
        self.url = "https://www.vseinstrumenti.ru/lk-api/v2/search/get-results"

        self.payload = {
            'term': f"{ID}",
            'from': "desktop"}
        self.headers = {
            "cookie":'favToken=mkAknHOOyBNcZCQQJhoL8IpYUOXcZDmj; _gcl_au=1.1.983967397.1626942076; tmr_lvid=c8541763ad98c8664f5511860b2dc42a; tmr_lvidTS=1626942076131; _ga=GA1.2.747813940.1626942076; _fbp=fb.1.1626942076287.763713940; goods_per_page=20; rrpvid=818899871131746; rcuid=60ed6a4e2e92f30001797f69; device_uid=4vu2Ll8dYS2U5639nrG24WT7BBhomC8H7xx2krp4v42Rg0N6ctXoJ4g1jR2J813U; SESSIDVI=G3zBKzVS0kmB8WAwRn9JFqBkLpgDN22l; cartToken=jAkRtcuGX1j4k13KDguDlrfEcGca51OI; _gcl_aw=GCL.1629703631.EAIaIQobChMIs76sjs_G8gIVBN-yCh0FOwFTEAAYASAAEgLogfD_BwE; _gac_UA-6106715-1=1.1629703631.EAIaIQobChMIs76sjs_G8gIVBN-yCh0FOwFTEAAYASAAEgLogfD_BwE; _gid=GA1.2.96597822.1629703631; is-visited=1; ab_exps={"186":2,"202":1,"211":4,"218":2,"219":2,"226":3,"230":0,"231":1,"234":2}; wucf=8; showAdminPanel=1; rrviewed=1229870; rrlevt=1629703666377; prev_act_time=1629703835; _ym_uid=1629703849585576666; _ym_d=1629703849; _ym_isad=2; tmr_reqNum=58; _gat=1; _gat_UA-6106715-1=1; cto_bundle=QnrPfl9HOENYT0NvME9Fc2dGQldiUiUyQndTQXRRT2slMkY2WCUyQlk0VnN4a3hIUDkyem5JcXhJcmtKQ2FLYXpxR09NQnpwWmclMkZKNEtRMTNmZWxBVW81eXRuYklvS2RpVmhSMWN3WlZ5cURUbGxNQyUyQk1iMHpwZVltZk1QNlFqZyUyQnkxd1pkVEFONFBNSDJTSk1NV21LYXk0S0RDOSUyRkE0USUzRCUzRA; tmr_detect=0|1629704871426; mindboxDeviceUUID=cf6d860b-b98b-4df8-b556-527c346f7de7',
            "authority": "www.vseinstrumenti.ru",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-length": "36",
            "content-type": "application/json;charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        }

        self.headers2 = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.153"
            }

        #self.ses = requests.Session()
        self.ses2 = r_ses


    def get_page_from_api(self):
        # get url from api
        response_api = requests.post(self.url, json=self.payload, headers=self.headers)
        data = json.loads(response_api.text)
        if len(data) < 1:
            self.tovar_url = 'Не найден'
            self.name = 'Не найден'
            self.price = 'Error'
            self.stars = '-'
            self.otziv = '-'
            self.sklad = 'Error'
            self.stock = ''
            return
        else:
            pass
        try:
            url = data[0]["link"]
        except:
            print(data)
            exit()
        time.sleep(1)
        # write in file urls from api
        if 'http' in url:
            with open("/opt/marketing_parsers/parsers/vseinstrumenti/urls.txt", 'a', encoding='utf8') as f:
                f.write(f'{self.ID}::{url}'+'\n')
        self.get_info_from_page(url)

    def get_info_from_page(self,url):
        # respons html of sell item
        response = self.ses2.get(url, headers=self.headers2)
        self.soup = bs(response.text, 'lxml')
        self.tovar_url = response.url

        try:
            self.name = self.soup.find('h1', class_='title').text
        except:
            self.name = 'Error'
        try:
            self.price = self.soup.find('span', class_='current-price').text
        except:
            self.price = 'Error'
        try:
            self.meta = self.soup.find('div', class_='toggle').find_all('meta')
            self.stars = '-'
            self.otziv = '-'
            for i in self.meta:
                a = i.get('itemprop')
                if a == 'ratingValue':
                    self.stars = i.get('content')
                elif a == 'ratingCount':
                    self.otziv = i.get('content')
                else:
                    pass
        except:
            self.stars = 'Error'
            self.otziv = 'Error'
        try:
            self.sklad = self.soup.find('ul', class_='product-delivery')
            self.sklad = self.sklad.find_all('strong')
            self.sklad = self.sklad[-1].text
        except:
            self.sklad = 'Error'
        try:
            self.stock = self.soup.find('span', class_='add-to-card').get('title')
        except:
            self.stock = ''
def main():
    knows_urls = {}
    FILE = '/opt/marketing_parsers/parsers/instrumenti.xlsx'
    #FILE = 'instrumenti.xlsx'
    with open('/opt/marketing_parsers/parsers/vseinstrumenti/urls.txt', 'r', encoding='utf8') as f:
        for i in f.readlines():
            k,u = i.strip('\n').split('::')
            knows_urls.update({k:u})
    main_file = pd.read_excel(FILE)
    DF = pd.DataFrame()
    num = 0
    r_ses = requests.Session()
    for i in main_file.SKU:
        num += 1
        if num == 50:
            time.sleep(20)
            num = 0
        else:
            pass
        if len(str(i)) == 8 and i != 0 and i != '?' and i != 'nan':
            if str(i) in knows_urls:
                url = knows_urls.get(str(i))
                VS = VSEINSTR(str(i), r_ses)
                VS.get_info_from_page(url)
                DF.at[i,'URL'] = str(VS.tovar_url)
                DF.at[i,'NAME'] = str(VS.name)
                DF.at[i,'PRICE'] = str(VS.price)
                DF.at[i,'STARS'] = str(VS.stars)
                DF.at[i,'REPORTS'] = str(VS.otziv)
                DF.at[i,'SKU'] = str(i)
                DF.at[i,'HOWMANY'] = str(VS.sklad)
                DF.at[i,'STOCK'] = str(VS.stock)
            else:
                print(f'not in file {str(i)}')
                VS = VSEINSTR(str(i), r_ses)
                VS.get_page_from_api()
                DF.at[i,'URL'] = str(VS.tovar_url)
                DF.at[i,'NAME'] = str(VS.name)
                DF.at[i,'PRICE'] = str(VS.price)
                DF.at[i,'STARS'] = str(VS.stars)
                DF.at[i,'REPORTS'] = str(VS.otziv)
                DF.at[i,'SKU'] = str(i)
                DF.at[i,'HOWMANY'] = str(VS.sklad)
                DF.at[i,'STOCK'] = str(VS.stock)
        else:
            DF.at[i,'URL'] = str('-')
            DF.at[i,'NAME'] = str('-')
            DF.at[i,'PRICE'] = str('-')
            DF.at[i,'STARS'] = str('-')
            DF.at[i,'REPORTS'] = str('-')
            DF.at[i,'SKU'] = str(i)
            DF.at[i,'HOWMANY'] = str(VS.sklad)
            DF.at[i,'STOCK'] = str(VS.stock)
    # DF.to_excel(f'VSEINSTUMENTI_{datetime.datetime.today().strftime("%d.%m.%Y")}.xlsx')
    r_ses.close()
    DF.to_excel(f'/opt/reports/vseinstrumenti/VSEINSTUMENTI_{datetime.datetime.today().strftime("%d.%m.%Y")}.xlsx')

if __name__ == '__main__':
    main()

