import schedule
import time
from citilink import main as link
from dns import dns_main
from vseinstrumenti import vi_main as instrumenti
from wb_tag import wb_tags_req as tag_wb

import logging
logging.basicConfig(level=logging.INFO)

def DNS():
	try:
		dns_main.main()
	except Exception as ex:
		logging.info(f'Failed DNS parser. {ex}')

def CL():
	try:
		link.main()
	except Exception as ex:
		logging.info(f'Failed citilink parser. {ex}')

def VI():
	try:
		instrumenti.main()
	except Exception as ex:
		logging.info(f'Failed Vse Instrumenti. {ex}')

def WBTAG():
	try:
		tag_wb.main()
	except Exception as ex:
		logging.info(f'tags WB fail {ex}')


schedule.every().day.at("08:00").do(WBTAG)
schedule.every().day.at("00:20").do(VI)
schedule.every().day.at("05:00").do(DNS)
schedule.every().day.at("00:01").do(CL)

while True:
    schedule.run_pending()
    time.sleep(1)
