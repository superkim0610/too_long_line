from Crawler import NaverMapCrawler
import time

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
    "수서",
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