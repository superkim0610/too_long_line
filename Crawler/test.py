import requests
import time
import re
import urllib.parse

API_KEY = "102E4A17-FC5A-3ECA-BA54-0F3F8C478E8E"


def normalize_city(address):
    if address.startswith("서울 "):
        return address.replace("서울 ", "서울특별시 ", 1)
    elif address.startswith("부산 "):
        return address.replace("부산 ", "부산광역시 ", 1)
    elif address.startswith("대구 "):
        return address.replace("대구 ", "대구광역시 ", 1)
    elif address.startswith("인천 "):
        return address.replace("인천 ", "인천광역시 ", 1)
    elif address.startswith("광주 "):
        return address.replace("광주 ", "광주광역시 ", 1)
    elif address.startswith("대전 "):
        return address.replace("대전 ", "대전광역시 ", 1)
    elif address.startswith("울산 "):
        return address.replace("울산 ", "울산광역시 ", 1)
    elif address.startswith("세종 "):
        return address.replace("세종 ", "세종특별자치시 ", 1)
    elif address.startswith("경기 "):
        return address.replace("경기 ", "경기도 ", 1)
    elif address.startswith("강원 "):
        return address.replace("강원 ", "강원도 ", 1)
    elif address.startswith("충북 "):
        return address.replace("충북 ", "충청북도 ", 1)
    elif address.startswith("충남 "):
        return address.replace("충남 ", "충청남도 ", 1)
    elif address.startswith("전북 "):
        return address.replace("전북 ", "전라북도 ", 1)
    elif address.startswith("전남 "):
        return address.replace("전남 ", "전라남도 ", 1)
    elif address.startswith("경북 "):
        return address.replace("경북 ", "경상북도 ", 1)
    elif address.startswith("경남 "):
        return address.replace("경남 ", "경상남도 ", 1)
    elif address.startswith("제주 "):
        return address.replace("제주 ", "제주특별자치도 ", 1)
    else:
        return address


def clean_address(address):
    cleaned = address.strip()
    cleaned = re.sub(r'\d+동\s*\d+호', '', cleaned)
    cleaned = re.sub(r'(지하|지상)?\d+(층|호)', '', cleaned)
    cleaned = re.sub(r'\s+B\d+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def get_lat_lon_vworld(address, key):
    url = "https://api.vworld.kr/req/address"
    cleaned_address = clean_address(address)
    full_address = normalize_city(cleaned_address)

    params = {
        "service": "address",
        "request": "getcoord",
        "format": "json",
        "crs": "epsg:4326",
        "address": full_address,
        "key": key,
        "type": "road"
    }

    # try:
    response = requests.get(url, params=params, timeout=5)
    data = response.json()

    if data['response']['status'] == 'OK':
        point = data['response']['result']['point']
        return float(point['y']), float(point['x'])
    else:
        print(f"변환 실패: '{full_address}' → 상태: {data['response']['status']}")
        print(data["response"]["error"])
        return None, None



print(get_lat_lon_vworld("서울 강남구 언주로150길 51", API_KEY))