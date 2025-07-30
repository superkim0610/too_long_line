from Crawler import NaverMapCrawler
from Data import *
import time
import sys

data = get_data()

if __name__ == '__main__':
    if sys.argv[1] == "crawl":
        def crawl():
            dong_list = [
                # "압구정",
                # "신사",
                # "청담",
                # "논현",
                # "삼성",
                # "역삼",
                # "대치",
                # "도곡",
                # "개포",
                # "일원",
                # "수서",
                # "자곡",
                # "율현",
                # "세곡"
            ]

            for dong in dong_list:
                try:
                    c = NaverMapCrawler(headless=False)
                    c.run(f"{dong}동")
                except Exception as e:
                    print(e)
                time.sleep(10)
        crawl()
    elif sys.argv[1] == "integrate":
        raw_csvs_to_integrated_raw_csv()
    elif sys.argv[1] == "address":
        add_lat_lon_to_integrated_raw_csv()
    elif sys.argv[1] == "type":
        classify_restaurant_type_to_integrated_raw_csv()
    elif sys.argv[1] == "ratio":
        calc_review_ratio_to_integrated_raw_csv()
    elif sys.argv[1] == "to_data":
        integrated_raw_csv_to_data_csv()
    elif sys.argv[1] == "run_pipeline":
        preprocess_pipeline()