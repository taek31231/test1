import streamlit as st
import folium
from streamlit_folium import st_folium

# 국가지질공원 데이터
geoparks = {
    "제주특별자치도": {
        "location": [33.3895, 126.5450],
        "url": "https://www.jeju.go.kr/geopark/",
        "feature": "한라산, 만장굴, 성산일출봉 등 화산활동에 의한 지형이 대표적이며, 현무암 용암지형과 튜물러스, 라바튜브가 잘 보존됨",
        "tour": ["한라산 등반", "만장굴 탐방", "성산일출봉 일출 감상"]
    },
    "울릉도·독도": {
        "location": [37.4842, 130.9053],
        "url": "https://www.ulleung.go.kr/geopark/",
        "feature": "해저 화산활동으로 형성된 화산섬으로, 응회암층, 주상절리, 화산돔 등 다양한 화산 지질 구조가 존재함",
        "tour": ["독도 탐방", "나리분지 탐방", "태하 모노레일 승차"]
    },
    "부산": {
        "location": [35.1796, 129.0756],
        "url": "https://www.busan.go.kr/geopark/",
        "feature": "오륙도, 송도 해상케이블카 등 해양침식 지형과 주상절리대가 발달함",
        "tour": ["오륙도 탐방", "송도 해상케이블카 탑승", "광안리 해수욕장 산책"]
    },
    "청송": {
        "location": [36.4350, 129.0572],
        "url": "https://www.cs.go.kr/geopark/",
        "feature": "빙하 시대의 얼음골, 주왕산 화강암, 대전사 층과 같은 고생대 지층과 침식 지형이 발달함",
        "tour": ["주왕산 등반", "얼음골 탐방", "대전사 사찰 방문"]
    },
    "경북 동해안": {
        "location": [37.5200, 128.9000],
        "url": "https://www.gb.go.kr/geopark/",
        "feature": "능파대, 문암해변, 송지호해변 등 다양한 해양 지질 구조가 발달함",
        "tour": ["능파대 탐방", "문암해변 산책", "송지호해변 일출 감상"]
    },
    "한탄강": {
        "location": [38.0305, 127.0746],
        "url": "https://www.hantanriver-geopark.kr/",
        "feature": "현무암 협곡과 용암대지, 하식절벽 등이 뛰어나며, 약 50만 년 전 화산 분출과 하천 침식작용으로 형성됨",
        "tour": ["현무암 협곡 탐방", "용암대지 산책", "하식절벽 관람"]
    },
    "강원 고생대": {
        "location": [37.7000, 128.2000],
        "url": "https://www.gangwon.go.kr/geopark/",
        "feature": "운봉산, 송지호해변, 문암해변 등 고생대 지층과 해양 지질 구조가 발달함",
        "tour": ["운봉산 등반", "송지호해변 산책", "문암해변 일출 감상"]
    },
    "백령·대청": {
        "location": [37.8000, 124.6000],
        "url": "https://www.bly.go.kr/geopark/",
        "feature": "백령도, 대청도, 해식절벽 등 다양한 해양 지질 구조가 발달함",
        "tour": ["백령도 탐방", "대청도 산책", "해식절벽 관람"]
    },
    "진안·무주": {
        "location": [35.8000, 127.7000],
        "url": "https://www.jinan.go.kr/geopark/",
        "feature": "진안 고원, 무주 반딧불이, 무주 덕유산 등 다양한 지질 구조가 발달함",
        "tour": ["진안 고원 탐방", "무주 반딧불이 관람", "덕유산 등반"]
    },
    "단양": {
        "location": [36.9800, 128.1700],
        "url": "https://www.danyang.go.kr/geopark/",
        "feature": "단양팔경, 고수동굴, 도담삼봉 등 다양한 지질 구조가 발달함",
        "tour": ["단양팔경 탐방", "고수동굴 탐방", "도담삼봉 관람"]
    },
    "무등산": {
        "location": [35.1391, 126.9990],
        "url": "https://www.gwangju.go.kr/geopark/",
        "feature": "주상절리대가 발달해 있으며, 백악기 화산활동의 흔적이 남아 있음. 광주·전남 일대의 지질유산 보존",
        "tour": ["무등산 등반", "백운동계곡 산책", "무등산 정상 관람"]
    },
    "의성": {
        "location": [36.3000, 128.4000],
        "url": "https://www.usc.go.kr/geopark/",
        "feature": "의성 금성산, 의성 고분군, 의성 호암지 등 다양한 지질 구조가 발달함",
        "tour": ["의성 금성산 탐방", "의성 고분군 관람", "의성 호암지 산책"]
    },
    "고군산군도": {
        "location": [35.7000, 126.3000],
        "url": "https://www.goosung.go.kr/geopark/",
        "feature": "고군산군도, 선유도, 장자도 등 다양한 해양 지질 구조가 발달함",
        "tour": ["고군산군도 탐방", "선유도 산책", "장자도 일출 감상"]
    },
    "화성": {
        "location": [37.2000, 126.8000],
        "url": "https://www.hwaseong.go.kr/geopark/",
        "feature": "화성 제암리, 화성 궁평항, 화성 팔탄리 등 다양한 지질 구조가 발달함",
        "tour": ["화성 제암리 탐방", "화성 궁평항 산책", "화성 팔탄리 관람"]
    },
    "고성": {
        "location": [38.2000, 128.2000],
        "url": "https://www.goseong.go.kr/geopark/",
        "feature": "천학정, 능파대, 문암해변 등 다양한 지질 구조가 발달함",
        "tour": ["천학정 탐방", "능파대 산책", "문암해변 일출 감상"]
    },
    "강원 평화지역": {
        "location": [38.0000, 128.5000],
        "url": "https://www.gangwon.go.kr/geopark/",
        "feature": "비무장지대(DMZ)와 접한 지역으로, 다양한 지질 구조와 함께 생태계 보존의 중요성이 강조됨",
        "tour": ["DMZ 탐방", "철원 평화전망대 방문", "화천 평화의 댐 탐방"]
    }
}

# Streamlit UI
st.set_page_config(page_title="대한민국 국가지질공원 지도", layout="wide")
st.title("🗺️ 대한민국 국가지질공원 정보")

selected = st.selectbox("지질공원을 선택하세요:", list(geoparks.keys()))

# 선택된 공원 정보
info = geoparks[selected]
lat, lon = info["location"]

# 설명 출력
st.subheader(selected)
st.markdown(f"**🌐 홈페이지:** [바로가기]({info['url']})")
st.markdown(f"**🧭 주요 지질구조 및 형성 기원:** {info['feature']}")
st.markdown(f"**🚶 추천 지질투어 코스:**")
for tour in info["tour"]:
    st.markdown(f"- {tour}")

# 지도 생성 및 표시
m = folium.Map(location=[36.5, 127.8], zoom_start=6)

# 마커 추가
for name, data in geoparks.items():
    folium.Marker(
        location=data["location"],
        popup=f"<b>{name}</b><br><a href='{data['url']}' target='_blank'>홈페이지</a><br><i>{data['feature']}</i>",
        tooltip=name,
        icon=folium.Icon(color="green" if name == selected else "blue")
    ).add_to(m)

# 지도 표시
st_folium(m, width=800, height=550)
