import streamlit as st
import folium
from streamlit_folium import st_folium

# 관광지 데이터
tourist_spots = {
    "에펠탑 (Eiffel Tower)": {
        "location": [48.8584, 2.2945],
        "description": """
        파리의 상징인 에펠탑은 1889년 만국박람회를 위해 건축된 철탑입니다.
        높이는 약 300m에 달하며, 파리 전경을 한눈에 볼 수 있는 전망대로도 유명합니다.
        밤이 되면 조명이 반짝이며, 매 시간 정각마다 반짝이는 라이트 쇼가 열려 관광객에게 큰 인기를 끌고 있습니다.
        """
    },
    "루브르 박물관 (Louvre Museum)": {
        "location": [48.8606, 2.3376],
        "description": """
        세계 최대 규모의 박물관 중 하나인 루브르 박물관은 '모나리자', '밀로의 비너스' 등 수많은 명작을 소장하고 있습니다.
        원래는 왕궁으로 사용되었으며, 현재는 고대부터 현대에 이르기까지 예술과 역사를 아우르는 컬렉션을 전시합니다.
        유리 피라미드 입구도 매우 유명한 포토 스팟입니다.
        """
    },
    "몽생미셸 (Mont Saint-Michel)": {
        "location": [48.636, -1.5115],
        "description": """
        바다가 밀물과 썰물에 따라 섬이 되었다가 육지가 되는 몽생미셸은 프랑스에서 가장 독특한 장소 중 하나입니다.
        중세 시대 수도원이 자리하고 있으며, 고딕 건축의 정수를 볼 수 있는 곳입니다.
        신비로운 분위기와 함께 유네스코 세계문화유산으로도 지정되어 있습니다.
        """
    },
    "베르사유 궁전 (Palace of Versailles)": {
        "location": [48.8049, 2.1204],
        "description": """
        루이 14세에 의해 건설된 베르사유 궁전은 프랑스 절대왕정의 상징입니다.
        호화로운 궁전 내부와 정원, 거울의 방(Hall of Mirrors) 등은 예술과 건축의 정점으로 손꼽힙니다.
        역사적으로도 중요한 장소이며, 매년 수많은 관광객이 찾습니다.
        """
    },
    "니스 해변 (Nice Beach)": {
        "location": [43.6959, 7.2710],
        "description": """
        프랑스 남부 코트다쥐르(Côte d'Azur)에 위치한 니스는 아름다운 해변과 온화한 기후로 유명합니다.
        고급스러운 휴양지로 많은 사람들이 여름휴가를 위해 찾는 곳이며,
        프로므나드 데 장글레(Promenade des Anglais)를 따라 산책하기도 좋습니다.
        """
    }
}

# Streamlit 앱 구성
st.set_page_config(page_title="프랑스 관광 가이드", layout="wide")
st.title("🇫🇷 프랑스 주요 관광지 가이드")

# 관광지 선택
selected_spot = st.selectbox("관광지를 선택하세요:", list(tourist_spots.keys()))

# 선택된 관광지 정보
spot_info = tourist_spots[selected_spot]
lat, lon = spot_info["location"]

# 관광지 설명
st.subheader(selected_spot)
st.markdown(spot_info["description"])

# Folium 지도 생성
m = folium.Map(location=[lat, lon], zoom_start=6)
folium.Marker(
    location=[lat, lon],
    popup=selected_spot,
    tooltip="클릭하면 자세한 위치가 표시됩니다.",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# Streamlit에 Folium 지도 표시
st_data = st_folium(m, width=700, height=500)
