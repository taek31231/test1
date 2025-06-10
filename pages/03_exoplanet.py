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
theta = np.linspace(0, 2 * np.pi, num_steps)
x_orbit = distance_km * np.cos(theta)
y_orbit = distance_km * np.sin(theta)

flux_changes = []
for i in range(num_steps):
    # 행성이 항성 앞을 지나갈 때, 항성 중심으로부터의 투영 거리 (x축으로 지나간다고 가정)
    distance_from_center_of_star_for_calc = abs(x_orbit[i])

    if distance_from_center_of_star_for_calc < (star_radius_km + planet_radius_km):
        flux_change_ratio = calculate_flux_change(star_radius_km, planet_radius_km, distance_from_center_of_star_for_calc)
        flux_changes.append(1 - flux_change_ratio)
    else:
        flux_changes.append(1.0)

time_steps = np.linspace(0, 1, num_steps)

# --- 3. Plotly 그래프 출력 ---
st.header("항성 밝기 변화 그래프")

fig_flux = go.Figure(
    data=go.Scatter(x=time_steps, y=flux_changes, mode='lines', name='상대 밝기'),
    layout=go.Layout(
        title='항성 밝기 변화 곡선',
        xaxis_title='시간 (상대적)',
        yaxis_title='상대 밝기',
        yaxis_range=[0.0, 1.1]
    )
)
st.plotly_chart(fig_flux, use_container_width=True)

# --- 4. 애니메이션 출력 ---
# `---`를 Streamlit의 마크다운 구분자로 변경
st.markdown("---") # 여기를 수정했습니다.
st.header("행성의 공전 애니메이션 (Plotly)")

# 애니메이션을 위한 Plotly Figure 생성
fig_animation = go.Figure()

# 항성 그리기
fig_animation.add_trace(go.Scatter(
    x=[0], y=[0], mode='markers',
    marker=dict(size=star_radius_km / R_sun * 20, color='orange', symbol='circle'),
    name='항성'
))

# 행성 궤도 그리기
fig_animation.add_trace(go.Scatter(
    x=x_orbit, y=y_orbit, mode='lines',
    line=dict(color='gray', dash='dot'),
    name='행성 궤도'
))

# 행성 초기 위치 설정 (애니메이션 프레임에 사용될 데이터)
# Plotly 애니메이션을 위한 frames 준비
frames = []
for i in range(num_steps):
    frame = go.Frame(data=[
        go.Scatter(
            x=[0], y=[0], mode='markers',
            marker=dict(size=star_radius_km / R_sun * 20, color='orange', symbol='circle')
        ),
        go.Scatter(
            x=[x_orbit[i]], y=[y_orbit[i]], mode='markers',
            marker=dict(size=planet_radius_km / R_earth * 10, color='blue', symbol='circle')
        )
    ], name=str(i))
    frames.append(frame)

fig_animation.frames = frames

# 애니메이션 버튼 추가
fig_animation.update_layout(
    title='행성 공전 궤도 시뮬레이션',
    xaxis_title='X (km)',
    yaxis_title='Y (km)',
    xaxis_range=[-distance_km * 1.2, distance_km * 1.2],
    yaxis_range=[-distance_km * 1.2, distance_km * 1.2],
    autosize=False,
    width=600,
    height=600,
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

# `---`를 Streamlit의 마크다운 구분자로 변경
st.markdown("---") # 여기를 수정했습니다.
st.header("항성 정보")
st.write(f"**항성 반경:** {star_radius_km / 1000:.2f} km")
st.write(f"**행성 반경:** {planet_radius_km / 1000:.2f} km")
st.write(f"**항성 온도:** {star_temperature_k / 1000:.1f} K")

sigma = 5.67e-8 # 스테판-볼츠만 상수 (W/m^2/K^4)
star_surface_area = 4 * np.pi * (star_radius_km * 1000)**2 # m^2
star_luminosity = star_surface_area * sigma * (star_temperature_k)**4 # W

st.write(f"**항성 광도 (예상):** {star_luminosity:.2e} W")
st.write("*(참고: 항성 광도는 밝기 변화 계산에 직접 사용되지는 않지만, 항성의 물리량을 이해하는 데 도움을 줍니다.)*")
