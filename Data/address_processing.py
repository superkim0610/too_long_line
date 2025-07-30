import pandas as pd
import requests
import time
import re
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("VWORLD_API_KEY")

def normalize_city(address):
    city_map = {
        "서울 ": "서울특별시 ", "부산 ": "부산광역시 ", "대구 ": "대구광역시 ", "인천 ": "인천광역시 ",
        "광주 ": "광주광역시 ", "대전 ": "대전광역시 ", "울산 ": "울산광역시 ", "세종 ": "세종특별자치시 ",
        "경기 ": "경기도 ", "강원 ": "강원도 ", "충북 ": "충청북도 ", "충남 ": "충청남도 ",
        "전북 ": "전라북도 ", "전남 ": "전라남도 ", "경북 ": "경상북도 ", "경남 ": "경상남도 ",
        "제주 ": "제주특별자치도 "
    }
    for short, full in city_map.items():
        if address.startswith(short):
            return address.replace(short, full, 1)
    return address

def clean_address(address):
    cleaned = address.strip()
    cleaned = re.sub(r'\d+동\s*\d+호', '', cleaned)
    cleaned = re.sub(r'(지하|지상)?\d+(층|호)', '', cleaned)
    cleaned = re.sub(r'\s+B\d+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def get_lat_lon_vworld(address):
    url = "https://api.vworld.kr/req/address"
    cleaned_address = clean_address(address)
    full_address = normalize_city(cleaned_address)

    params = {
        "service": "address",
        "request": "getcoord",
        "format": "json",
        "crs": "epsg:4326",
        "address": full_address,
        "key": API_KEY,
        "type": "road"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data['response']['status'] == 'OK':
            point = data['response']['result']['point']
            return float(point['y']), float(point['x'])
        else:
            # print(f"❌ 변환 실패: '{full_address}' → 상태: {data['response']['status']}")
            return None, None
    except Exception as e:
        # print(f"⚠️ 예외 발생: {e}")
        return None, None

def add_lat_lon_to_integrated_raw_csv(INPUT_FILE, OUTPUT_FILE):
    ADDRESS_COLUMN = 'restaurant_address'

    df = pd.read_csv(INPUT_FILE)

    # === 좌표 변환 수행 ===
    latitudes = []
    longitudes = []

    print("주소 변환 중:")
    for addr in tqdm(df[ADDRESS_COLUMN]):
        lat, lon = get_lat_lon_vworld(str(addr), API_KEY)
        latitudes.append(lat)
        longitudes.append(lon)
        time.sleep(0.2)  # API 요청 간격 조절 (너무 빠르면 차단될 수 있음)

    df['restaurant_lat'] = latitudes
    df['restaurant_lon'] = longitudes

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n저장 완료: {OUTPUT_FILE}")
