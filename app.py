import streamlit as st
from Data.address_processing import get_lat_lon_vworld
# from Data import

def init():
    session_state_init = {
        "lat": 0.0,
        "lon": 0.0,
        "_lat": 0.0,
        "_lon": 0.0,
        "restaurant_types": [],
        "restaurant_keywords": []
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
                address = st.text_input("주소", placeholder="서울특별시 강남구 테헤란로 123", label_visibility="collapsed")

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

def render_restaurant_keyword_container():
    c = st.container(border=True)
    with c:
        c1 = st.container(border=False)
        c2 = st.container(border=False)

    with c2:
        col1, col2, col3 = st.columns(3)

        with col1:
            options = ["가성비", "양 많음", "재료 신선", "커피 맛"]
            selection1 = st.pills("음식/가격", options, selection_mode="multi")
        with col2:
            options = ["아늑함", "인테리어", "조용함", "넓음"]
            selection2 = st.pills("분위기", options, selection_mode="multi")
        with col3:
            options = ["친절함", "주차 편리", "반려동물", "포장 깔끔"]
            selection3 = st.pills("기타", options, selection_mode="multi")

        col_n = 11
        cols = st.columns(col_n)
        with cols[col_n // 2]:
            if st.button(":material/add:", use_container_width=True):
                print("+")

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
        st.button("검색하기", use_container_width=True, type="primary", on_click=search)

def render():
    st.title("Too Long Line")

    render_address_container()
    render_restaurant_type_container()
    render_restaurant_keyword_container()
    render_search_button()

def search():
    print('search button pressed')
    conditions = [
        st.session_state["lat"] != 0.0,
        st.session_state["lon"] != 0.0,
        st.session_state["restaurant_types"] != [],
        st.session_state["restaurant_keywords"] != [],
    ]


if __name__ == "__main__":
    st.set_page_config(layout="centered")
    init()
    render()


