import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time # 애니메이션을 위한 time 모듈

st.set_page_config(layout="wide")
st.title("식현상 시뮬레이션: 항성 밝기 변화")

st.sidebar.header("시뮬레이션 설정")

# --- 1. 사용자 입력 부분 ---
planet_radius_earth_units = st.sidebar.slider(
    "행성 반경 (지구 반경 단위)",
    min_value=0.1, max_value=20.0, value=1.0, step=0.1
)
R_earth = 6371
planet_radius_km = planet_radius_earth_units * R_earth

star_radius_sun_units = st.sidebar.slider(
    "항성 반경 (태양 반경 단위)",
    min_value=0.1, max_value=10.0, value=1.0, step=0.1
)
R_sun = 696340
star_radius_km = star_radius_sun_units * R_sun

distance_au = st.sidebar.number_input(
    "행성과 항성 사이 거리 (AU)",
    min_value=0.1, max_value=10.0, value=1.0, step=0.1
)
AU_to_km = 149597870.7
distance_km = distance_au * AU_to_km

star_temperature_thousand_k = st.sidebar.slider(
    "항성의 온도 (1,000K)",
    min_value=1.0, max_value=30.0, value=5.7, step=0.1
)
star_temperature_k = star_temperature_thousand_k * 1000

# --- 2. 밝기 변화 계산 함수 ---
def calculate_flux_change(star_radius_km, planet_radius_km, distance_from_center_of_star):
    R_s = star_radius_km
    R_p = planet_radius_km
    d = distance_from_center_of_star

    if d >= R_s + R_p:
        return 0.0
    elif d <= abs(R_s - R_p):
        if R_p <= R_s:
            return (np.pi * R_p**2) / (np.pi * R_s**2)
        else:
            return 1.0

    else:
        arg1_arccos = (d**2 + R_s**2 - R_p**2) / (2 * d * R_s)
        arg2_arccos = (d**2 + R_p**2 - R_s**2) / (2 * d * R_p)

        arg1_arccos = np.clip(arg1_arccos, -1.0, 1.0)
        arg2_arccos = np.clip(arg2_arccos, -1.0, 1.0)

        alpha = np.arccos(arg1_arccos)
        beta = np.arccos(arg2_arccos)

        area_overlap = R_s**2 * alpha + R_p**2 * beta - 0.5 * np.sqrt(
            (-d + R_s + R_p) * (d + R_s - R_p) * (d - R_s + R_p) * (d + R_s + R_p)
        )
        return area_overlap / (np.pi * R_s**2)

# --- 시뮬레이션 계산 ---
num_steps = 200
# 트랜짓 시뮬레이션을 위한 '투영 거리' (d) 생성
# 행성이 항성 앞을 가로지르는 시나리오를 가정합니다.
# d는 항성 중심에서 행성 중심까지의 시선 수직 거리입니다.
# d가 (Rs + Rp)보다 크면 가림 없음, 0일 때 최대 가림.
max_overlap_distance = star_radius_km + planet_radius_km

# 트랜짓이 발생하는 동안의 투영 거리를 -1.2 * max_overlap_distance 에서
# +1.2 * max_overlap_distance 까지 선형적으로 변화시킵니다.
# 이렇게 하면 항상 밝기 변화가 나타나는 구간이 포함됩니다.
# 이 `x_pos_for_transit`이 밝기 변화 계산에 사용될 '투영 거리'가 됩니다.
x_pos_for_transit = np.linspace(-max_overlap_distance * 1.2, max_overlap_distance * 1.2, num_steps)
# 행성의 y축 위치는 0으로 고정하여 '시선 방향'임을 나타냅니다.
y_pos_for_transit = np.zeros(num_steps)


flux_changes = []
for d_val in x_pos_for_transit: # 여기를 x_pos_for_transit으로 변경
    # calculate_flux_change 함수는 투영 거리의 절댓값을 사용합니다.
    distance_from_center_of_star_for_calc = abs(d_val) # d_val이 이미 투영 거리

    flux_change_ratio = calculate_flux_change(star_radius_km, planet_radius_km, distance_from_center_of_star_for_calc)
    flux_changes.append(1 - flux_change_ratio) # 1에서 감소 비율을 뺀 값 = 상대 밝기 (상대 밝기 1.0은 변화 없음)

time_steps = np.linspace(0, 1, num_steps)

# --- 3. Plotly 그래프 출력 ---
st.header("항성 밝기 변화 그래프")

fig_flux = go.Figure(
    data=go.Scatter(x=time_steps, y=flux_changes, mode='lines', name='상대 밝기'),
    layout=go.Layout(
        title='항성 밝기 변화 곡선 (트랜짓 시뮬레이션)',
        xaxis_title='시간 (상대적)',
        yaxis_title='상대 밝기',
        yaxis_range=[0.0, 1.1]
    )
)
st.plotly_chart(fig_flux, use_container_width=True)

---

### **애니메이션 출력: 관측자 시점 조정**

st.header("행성의 식현상 애니메이션 (관측 시점 조정)")
st.markdown("""
이 애니메이션은 관측자의 시점에서 행성이 항성 앞을 가로지르는(트랜짓) 모습을 시각적으로 보여줍니다.
행성이 항성을 가릴 때 항성의 밝기가 변화하는 것을 확인할 수 있습니다.
""")

# 애니메이션을 위한 Plotly Figure 생성
fig_animation = go.Figure()

# 초기 항성 그리기 (애니메이션이 시작되기 전 기본 모습)
fig_animation.add_trace(go.Scatter(
    x=[0], y=[0], mode='markers',
    marker=dict(size=star_radius_km / R_sun * 20, color='orange', symbol='circle', opacity=1.0),
    name='항성'
))

# 행성 궤도 (직선으로 표시)
# 행성이 항성 앞을 X축으로 지나가는 것처럼 보이도록 Y축은 0으로 고정
fig_animation.add_trace(go.Scatter(
    x=x_pos_for_transit, y=y_pos_for_transit, mode='lines', # 여기를 x_pos_for_transit, y_pos_for_transit으로 변경
    line=dict(color='gray', dash='dot'),
    name='트랜짓 경로'
))

# 애니메이션 프레임 준비
frames = []
for i in range(num_steps):
    # 해당 프레임에서의 항성 투명도 계산
    current_star_opacity = flux_changes[i]
    if current_star_opacity < 0.05: # 완전히 사라지는 느낌을 위해 최소 투명도 더 낮춤
        current_star_opacity = 0.05

    frame = go.Frame(data=[
        go.Scatter(
            x=[0], y=[0], mode='markers',
            marker=dict(size=star_radius_km / R_sun * 20, color='orange', symbol='circle', opacity=current_star_opacity)
        ), # 항성 (투명도 동적 조절)
        go.Scatter(
            x=[x_pos_for_transit[i]], y=[y_pos_for_transit[i]], mode='markers', # 여기도 x_pos_for_transit, y_pos_for_transit으로 변경
            marker=dict(size=planet_radius_km / R_earth * 10, color='blue', symbol='circle')
        ) # 행성의 현재 위치
    ], name=str(i))
    frames.append(frame)

fig_animation.frames = frames

# 애니메이션 레이아웃 설정 및 버튼 추가
fig_animation.update_layout(
    title='행성 식현상 시뮬레이션 (정면 관측)',
    xaxis_title='X (km)',
    yaxis_title='Y (km)', # Y축은 사실상 관측 시점에서 깊이 개념
    xaxis_range=[-max_overlap_distance * 1.5, max_overlap_distance * 1.5], # 트랜짓 범위 충분히 보이도록 조정
    yaxis_range=[-planet_radius_km * 2, planet_radius_km * 2], # Y축 범위를 행성 크기에 맞춰 좁게 설정
    autosize=False,
    width=600,
    height=400, # 높이를 줄여서 더 납작한 시야를 강조
    showlegend=True,
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 50, 'redraw': True}, 'fromcurrent': True, 'transition': {'duration': 0, 'easing': 'linear'}}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }]
)

st.plotly_chart(fig_animation, use_container_width=True)

---

### **항성 정보 표시**

st.header("항성 정보")
st.write(f"**항성 반경:** {star_radius_km / 1000:.2f} km")
st.write(f"**행성 반경:** {planet_radius_km / 1000:.2f} km")
st.write(f"**항성 온도:** {star_temperature_k / 1000:.1f} K")

sigma = 5.67e-8 # 스테판-볼츠만 상수 (W/m^2/K^4)
star_surface_area = 4 * np.pi * (star_radius_km * 1000)**2 # m^2
star_luminosity = star_surface_area * sigma * (star_temperature_k)**4 # W

st.write(f"**항성 광도 (예상):** {star_luminosity:.2e} W")
st.write("*(참고: 항성 광도는 밝기 변화 계산에 직접 사용되지는 않지만, 항성의 물리량을 이해하는 데 도움을 줍니다.)*")
