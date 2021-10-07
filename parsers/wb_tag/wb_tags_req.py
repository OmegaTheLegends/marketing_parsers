import time, datetime
import json
import requests
import pandas as pd
import numpy as np

class wild:
    def __init__(self, search_list, ID_list, links_list):
        self.row = 1
        self.start_payload = ""
        self.start_headers = {
            "authority": "wbxsearch.wildberries.ru",
            "sec-ch-ua": "^\^Google"
        }
        self.ses = requests.Session()
        self.ID_list = ID_list
        self.search_list = search_list
        self.links_list = links_list
        self.finish = []
        self.DF = pd.DataFrame()
        # print(self.ID_list)

    def get_url(self, url, query):
        count = 0
        while count <= 5:
            count += 1
            response = self.ses.request("GET", url, data=self.start_payload, headers=self.start_headers, params=query, timeout=20)
            # print(response.url)
            if response.status_code != 200:
                time.sleep(0.2)
                print(f'status code {response.status_code}')
                if count == 2 and response.status_code == 400:
                    return '400'
                continue
            if len(response.text) <= 3:
                time.sleep(0.2)
                print(f'try again data: {response.text}')
                if count == 2:
                    return '400'
                continue
            else:
                data = json.loads(response.text)
                return data
        # print('Всё плохо.')
        self.ses.close()
        exit()


    ### Первый запрос на получание данных о поиске.
    def first_response(self,searching):
        self.finish.clear()
        self.page = 1
        self.start_url = "https://wbxsearch.wildberries.ru/exactmatch/v2/common"
        self.start_querystring = {"query":f"{searching}"}
        self.data = self.get_url(self.start_url, self.start_querystring)
        # print(self.data)

    ### Запрос что бы узнать кол-во нужных страниц.
    def second_response(self):
        second_url = f"https://wbxcatalog-ru.wildberries.ru/{self.data['shardKey']}/v3/filters/only" if self.data['shardKey'] != 'merger' else "https://wbxcatalog-ru.wildberries.ru/merger/filters"
        preset_id = self.data['query'].split('=')
        preset = preset_id[1]
        preset_or_token = preset_id[0]
        querystring = {"spp":"0",
            "regions":"64,75,4,38,30,33,70,68,71,22,31,66,40,1,80,69,48",
            "stores":"119261,122252,122256,117673,122258,122259,121631,122466,122467,122495,122496,122498,122590,122591,122592,123816,123817,123818,123820,123821,123822,124093,124094,124095,124096,124097,124098,124099,124100,124101,124583,124584,125238,125239,125240,132318,132320,132321,125611,135243,135238,133917,132871,132870,132869,132829,133084,133618,132994,133348,133347,132709,132597,132807,132291,132012,126674,126676,127466,126679,126680,127014,126675,126670,126667,125186,116433,119400,507,3158,117501,120602,6158,121709,120762,124731,1699,130744,2737,117986,1733,686,132043",
            "pricemarginCoeff":"1.0",
            "reg":"0","appType":"1",
            "offlineBonus":"0",
            "onlineBonus":"0",
            "emp":"0",
            "locale":"ru",
            "lang":"ru",
            "curr":"rub",
            "couponsGeo":"12,3,18,15,21",
            "dest":"-1257786,-2162196,-102269,-1029256",
            preset_or_token: str(preset)
            }
        
        data = self.get_url(second_url, querystring)
        count = data['data']['total']
        if int(count) % 100 == 0:
            self.pages  = int(count) // 100
            if self.pages == 0:
                self.pages = 2
        else:
            self.pages  = int(count) // 100 + 2
            if self.pages == 1:
                self.pages = 2

    def searching(self):
        url = f"https://wbxcatalog-ru.wildberries.ru/{self.data['shardKey']}/catalog" if self.data['shardKey'] != 'merger' else "https://wbxcatalog-ru.wildberries.ru/merger/catalog"
        # print(self.pages-1)
        for page in range(1,self.pages):
            if page == 98:
                print('stop on 99 page')
                break
            elif len(self.finish) == len(self.ID_list):
                print(f'Найдены все на {page}')
                break
            preset_id = self.data['query'].split('=')
            preset = preset_id[1]
            preset_or_token = preset_id[0]
            querystring = {
                "spp":"0",
                "regions":"64,75,4,38,30,33,70,68,71,22,31,66,40,1,80,69,48",
                "stores":"119261,122252,122256,117673,122258,122259,121631,122466,122467,122495,122496,122498,122590,122591,122592,123816,123817,123818,123820,123821,123822,124093,124094,124095,124096,124097,124098,124099,124100,124101,124583,124584,125238,125239,125240,132318,132320,132321,125611,135243,135238,133917,132871,132870,132869,132829,133084,133618,132994,133348,133347,132709,132597,132807,132291,132012,126674,126676,127466,126679,126680,127014,126675,126670,126667,125186,116433,119400,507,3158,117501,120602,6158,121709,120762,124731,1699,130744,2737,117986,1733,686,132043",
                "pricemarginCoeff":"1.0",
                "reg":"0",
                "appType":"1",
                "offlineBonus":"0",
                "onlineBonus":"0",
                "emp":"0",
                "locale":"ru",
                "lang":"ru",
                "curr":"rub",
                "couponsGeo":"12,3,18,15,21",
                "dest":"-1257786,-2162196,-102269,-1029256",
                preset_or_token: str(preset),
                "xfilters":self.data['filters'],
                "xparams":self.data['query'],
                "xshard":self.data['shardKey'],
                "page":page,
                "sort":"popular",
                "search":self.data['name']
                }
            data_page = self.get_url(url, querystring)
            if data_page == '400':
                break
            self.check(data_page, page)
        for name in self.ID_list:
            if name not in self.finish:
                self.DF.at[self.row,'TAG'] = str(self.data['name'])
                self.DF.at[self.row,'ID'] = name
                self.DF.at[self.row,'ALL_PAGE'] = self.pages - 1
                self.row += 1



    def check(self, data_page, page):
        items = data_page['data']['products']
        index = 1
        # print(f'check page {page}')
        for i in items:
            # print(i['id'], end=' ')
            if str(i['id']) in self.ID_list:
                self.DF.at[self.row,'TAG'] = str(self.data['name'])
                self.DF.at[self.row,'ID'] = i['id']
                self.DF.at[self.row,'PRICE'] = int(i['salePriceU']) // 100
                self.DF.at[self.row,'STARS'] = i['rating']
                self.DF.at[self.row,'Feedbacks'] = i['feedbacks']
                self.DF.at[self.row,'POSITION'] = index
                self.DF.at[self.row,'PAGE'] = page
                self.DF.at[self.row,'ALL_PAGE'] = self.pages - 1
                self.DF.at[self.row,'PRESTS'] = self.data['shardKey']
                self.row += 1
                self.finish.append(str(i['id']))
            index += 1
        time.sleep(0.1)



    def start(self):
        for search in self.search_list:
            self.first_response(search)
            time.sleep(0.2)
            self.second_response()
            self.searching()
        self.ses.close()
        self.DF.to_excel(f'/opt/reports/wb_tags/WB_TAGS_{datetime.datetime.today().strftime("%d.%m.%Y")}.xlsx', index=False) # /opt/reports/wb_tags/

def main():
    search_list = []
    search_links = []
    ID_list = []
    tag_list = pd.read_excel('/opt/marketing_parsers/parsers/wb_tag/tags_wb.xlsx') #/opt/marketing_parsers/parsers/wb_tag/
    # tag_list = pd.read_excel('tags_wb.xlsx') #/opt/marketing_parsers/parsers/wb_tag/
    for y in tag_list.TAGS:
        search_list.append(str(y))
    for y in tag_list.LINKS:
        search_links.append(str(y))
    for i in tag_list.ID:
        if str(i).endswith('.0'):
            i = str(i).replace('.0','')
            ID_list.append(str(i))
        elif np.isnan(i):
            pass
        else:
            ID_list.append(str(i))
    wb = wild(search_list, ID_list, search_links)
    wb.start()

if __name__ == '__main__':
    search_list = []
    search_links = []
    ID_list = []
    tag_list = pd.read_excel('/opt/marketing_parsers/parsers/wb_tag/tags_wb.xlsx') #/opt/marketing_parsers/parsers/wb_tag/
    # tag_list = pd.read_excel('tags_wb.xlsx') #/opt/marketing_parsers/parsers/wb_tag/
    for y in tag_list.TAGS:
        if str(y) not in [None,np.NaN,np.nan,np.NAN,'nan','',' ']:
            search_list.append(str(y))
    # for y in tag_list.LINKS:
        # if y not in [None,np.NaN,np.nan,np.NAN,'nan','',' ']:
        #     search_links.append(str(y))
    for i in tag_list.ID:
        if str(i).endswith('.0'):
            i = str(i).replace('.0','')
            ID_list.append(str(i))
        elif np.isnan(i):
            pass
        else:
            ID_list.append(str(i))
    wb = wild(search_list, ID_list, search_links)
    wb.start()
