import schedule
import time
from vseinstrumenti import vi_main as instrumenti
from wb_tag import wb_tags_req as tag_wb

import logging
logging.basicConfig(level=logging.INFO)

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

while True:
    schedule.run_pending()
    time.sleep(1)