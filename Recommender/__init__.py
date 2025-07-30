from Data import get_data
import math
import numpy as np
import pickle
import os

def type_filtering(df, types):
    df = df.dropna(subset=["restaurant_type"])
    df = df.copy()
    df["대분류"] = df["restaurant_type"].apply(lambda x: eval(x)["대분류"])
    print(df[df["대분류"].isin(types)])
    return df[df["대분류"].isin(types)]

def haversine_distance(lat1, lon1, lat2, lon2, radius_km=6371):
    psi1, lambda1 = math.radians(lat1), math.radians(lon1)
    psi2, lambda2 = math.radians(lat2), math.radians(lon2)
    dpsi = psi2 - psi1
    dlambda = lambda2 - lambda1
    a = math.sin(dpsi / 2)**2 + math.cos(psi1) * math.cos(psi2) * math.sin(dlambda / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return radius_km * c * 1000

def dist_filtering(df, loc, distance):
    lat, lon = loc
    df = df.dropna(subset=["restaurant_lat", "restaurant_lon"])

    df['distance'] = df.apply(
        lambda row: haversine_distance(lat, lon, row["restaurant_lat"], row["restaurant_lon"]),
        axis=1
    )
    print(df["distance"])

    return df[df["distance"] <= distance]

def extract_ratio(_dict, keywords):
    # print(_dict, keywords)
    result = []
    for keyword in keywords:
        if keyword in _dict.keys():
            result.append(_dict[keyword])
        else:
            result.append(0.0)
    for _ in range(5-len(result)):
        result.append(0.0)
    return result

def calc_Z(df, keywords, k):
    # df = df.dropna(subset=[])

    df["keyword_ratio"] = df["review_ratio"].apply(lambda x: extract_ratio(eval(x), keywords))
    df["Z"] = df["keyword_ratio"].apply(lambda x: np.array(x) @ k)
    return df


def recommend(user_location, restaurant_types, restaurant_keywords):
    print(restaurant_keywords)
    k_path = "Recommender/k.pickle"
    if os.path.exists(k_path):
        with open(k_path, "rb") as f:
            k = pickle.load(f)
    else:
        k = np.array([8, 6, 3, 2, 1], dtype=float)

    data = get_data()

    data = type_filtering(data, restaurant_types)
    # return data
    data = dist_filtering(data, user_location, 999999)
    data = calc_Z(data, restaurant_keywords, k)
    result = data.sort_values(by="Z", ascending=False).head(15)
    return result


