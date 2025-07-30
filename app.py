import streamlit as st
from streamlit import session_state
from Data.address_processing import get_lat_lon_vworld
from Recommender import recommend
from random import randint

def search():
    lat, lon, types, keywords = st.session_state["lat"], st.session_state["lon"], st.session_state["restaurant_types"], st.session_state["restaurant_keywords"]
    is_error = False

    if len(types) == 0:
        st.session_state.visible_type_min_warn = True
        is_error = True
    else:
        st.session_state.visible_type_min_warn = False

    if len(keywords) == 0:
        st.session_state.visible_keyword_min_warn = True
        is_error = True
    else:
        st.session_state.visible_keyword_min_warn = False

    if len(keywords) > 5:
        st.session_state.visible_keyword_max_warn = True
        is_error = True
    else:
        st.session_state.visible_keyword_max_warn = False

    if is_error:
        st.rerun()
        return None

    recommendation = recommend((lat, lon), types, keywords)
    return recommendation

def init():
    lat = 37.498408928
    lon = 127.03226105
    session_state_init = {
        "visible_type_min_warn": False,
        "visible_keyword_min_warn": False,
        "visible_keyword_max_warn": False,
        "visible_keyword_num": 7,

        "lat": lat,
        "lon": lon,
        "_lat": lat,
        "_lon": lon,
        "restaurant_types": [],
        "restaurant_keywords": [],

        "recommendations": None,
    }

    for k, v in session_state_init.items():
        if not k in st.session_state:
            st.session_state[k] = v

def render_address_container():
    global address, address_button, lat, lon

    with st.container(border=True):
        st.markdown("#### 어디에 있는 음식점을 추천할까요?")
        address_tab, location_tab = st.tabs(["주소", "좌표"])

        with address_tab:
            col1, col2 = st.columns([5, 1])  # 비율 4:1 정도로 필드 넓게, 버튼 좁게

            with col1:
                address = st.text_input("주소", placeholder="서울 강남구 강남대로 396", label_visibility="collapsed")

            with col2:
                address_button = st.button("조회하기", use_container_width=True)

            # 조회 버튼 클릭 시 반응
            if address_button:
                if address.strip() == "":
                    st.warning("주소를 입력해주세요.")
                else:
                    x, y = get_lat_lon_vworld(address)
                    if x is None or y is None:
                        st.warning("주소를 입력해주세요.")
                    else:
                        st.session_state.lat, st.session_state.lon = x, y
                        st.session_state._lat, st.session_state._lon = x, y
                        print(st.session_state.lat, st.session_state.lon)
                        st.success("주소 조회에 성공했어요.")

        with location_tab:
            col1, col2 = st.columns(2)

            with col1:
                st.session_state.lat = st.number_input("위도", value=st.session_state._lat, format="%.6f", step=0.000001)
            with col2:
                st.session_state.lon = st.number_input("경도", value=st.session_state._lon, format="%.6f", step=0.000001)

def render_restaurant_type_container():
    with st.container(border=True):
        st.markdown("#### 무슨 음식을 추천할까요?")

        options = ["한식", "중식", "일식", "양식", "아시아음식"]
        st.session_state.restaurant_types = st.pills("음식점 카테고리", options, selection_mode="multi")

        if st.session_state.visible_type_min_warn:
            st.error("하나 이상의 음식점 카테고리를 골라야해요")

def render_restaurant_keyword_container():
    categorized_keywords = {
        "음식/가격": [
            "음식이 맛있어요", "재료가 신선해요", "특별한 메뉴가 있어요", "양이 많아요", "가성비가 좋아요",
            "고기 질이 좋아요", "커피가 맛있어요", "디저트가 맛있어요", "메뉴 구성이 알차요", "음료가 맛있어요",
            "건강한 맛이에요", "술이 다양해요", "빵이 맛있어요", "반찬이 잘 나와요", "비싼 만큼 가치있어요",
            "직접 잘 구워줘요", "음식이 빨리 나와요", "잡내가 적어요", "현지 맛에 가까워요", "코스요리가 알차요",
            "종류가 다양해요", "차가 맛있어요", "향신료가 강하지 않아요", "샐러드바가 잘 되어있어요", "가격이 합리적이에요"
        ],
        "분위기": [
            "인테리어가 멋져요", "매장이 청결해요", "매장이 넓어요", "혼밥하기 좋아요", "대화하기 좋아요",
            "특별한 날 가기 좋아요", "아늑해요", "음악이 좋아요", "사진이 잘 나와요", "뷰가 좋아요",
            "차분한 분위기예요", "좌석이 편해요", "오래 머무르기 좋아요", "혼술하기 좋아요", "룸이 잘 되어있어요",
            "야외공간이 멋져요", "아이와 가기 좋아요", "반려동물과 가기 좋아요", "환기가 잘 돼요", "파티하기 좋아요",
            "라이브공연이 훌륭해요"
        ],
        "기타": [
            "친절해요", "단체모임 하기 좋아요", "주차하기 편해요", "화장실이 깨끗해요", "기본 안주가 좋아요",
            "집중하기 좋아요", "컨셉이 독특해요", "주문제작을 잘해줘요", "선물하기 좋아요", "포장이 깔끔해요",
            "읽을만한 책이 많아요", "설명이 자세해요", "특색 있는 제품이 많아요", "포장이 정성스러워요"
        ]
    }

    c = st.container(border=True)
    with c:
        c1 = st.container(border=False)
        c2 = st.container(border=False)

        if st.session_state.visible_keyword_min_warn:
            st.error("하나 이상의 음식점 키워드를 골라야해요")

        if st.session_state.visible_keyword_min_warn:
            st.error("음식점 키워드는 최대 5개까지 고를 수 있어요")

    with c2:
        col1, col2, col3 = st.columns(3)

        with col1:
            options = categorized_keywords["음식/가격"][:st.session_state.visible_keyword_num]
            selection1 = st.pills("음식/가격", options, selection_mode="multi")
        with col2:
            options = categorized_keywords["분위기"][:st.session_state.visible_keyword_num]
            selection2 = st.pills("분위기", options, selection_mode="multi")
        with col3:
            options = categorized_keywords["기타"][:st.session_state.visible_keyword_num]
            selection3 = st.pills("기타", options, selection_mode="multi")

        col_n = 11
        cols = st.columns(col_n)
        with cols[col_n // 2]:
            if st.session_state.visible_keyword_num < max(len(categorized_keywords["음식/가격"]), len(categorized_keywords["분위기"]), len(categorized_keywords["기타"])):
                if st.button(":material/add:", use_container_width=True):
                    st.session_state.visible_keyword_num += 5
                    st.rerun()

    with c1:
        st.markdown("#### 어떤 분위기가 좋을까요?")
        selection = selection1 + selection2 + selection3
        st.session_state["restaurant_keywords"] = selection
        badge_str = " ".join(list(map(lambda x: f":red-badge[{x}]", selection)))
        st.markdown(badge_str)

def render_search_button():
    col_n = 5
    cols = st.columns(col_n)
    with cols[col_n // 2]:
        if st.button("검색하기", use_container_width=True, type="primary"):
            st.session_state.recommendations = search()

def render_recommendation_container():
    recommendation =  session_state.recommendations
    if recommendation is not None:
        with st.container(border=True):
            st.markdown("#### 이용자님의 취향에 따라 추천했어요")
            for restaurant in recommendation.to_dict(orient="records"):
                name = restaurant["restaurant_name"]
                Z = restaurant["Z"]
                distance = restaurant['distance']
                l1 = restaurant["대분류"]

                with st.container(border=True):
                    st.markdown(f'##### {name}')

                    cols2 = st.columns([1, 1, 1, 4, 1.5])
                    with cols2[0]:
                        st.markdown(f'Z: {Z:.2f}')

                    with cols2[1]:
                        st.markdown(f'{distance/1000:.2f}km')

                    with cols2[2]:
                        st.markdown(f'{l1}')

                    with cols2[4]:
                        st.button("대기시간", use_container_width=True, type="secondary", key=str(randint(1, 100000)))
                # st.divider()

def render_evaluation_container():
    recommendation = session_state.recommendations
    if recommendation is not None:
        with st.container(border=True):
            st.markdown("#### 추천을 평가해주세요")
            st.feedback("stars")

def render():
    st.title("Too Long Line")

    render_address_container()
    render_restaurant_type_container()
    render_restaurant_keyword_container()
    render_search_button()
    render_recommendation_container()
    render_evaluation_container()

if __name__ == "__main__":
    st.set_page_config(layout="centered")
    init()
    render()


