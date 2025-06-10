import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time # 애니메이션을 위한 time 모듈 (현재는 직접적인 애니메이션에 사용되지는 않음)

st.set_page_config(layout="wide")
st.title("식현상 시뮬레이션: 항성 밝기 변화")

st.sidebar.header("시뮬레이션 설정")

# --- 1. 사용자 입력 부분 ---
planet_radius_earth_units = st.sidebar.slider(
    "행성 반경 (지구 반경 단위)",
    min_value=0.1, max_value=20.0, value=1.0, step=0.1
)
# 지구 반경 (km)
R_earth = 6371
planet_radius_km = planet_radius_earth_units * R_earth

star_radius_sun_units = st.sidebar.slider(
    "항성 반경 (태양 반경 단위)",
    min_value=0.1, max_value=10.0, value=1.0, step=0.1
)
# 태양 반경 (km)
R_sun = 696340
star_radius_km = star_radius_sun_units * R_sun

distance_au = st.sidebar.number_input(
    "행성과 항성 사이 거리 (AU)",
    min_value=0.1, max_value=10.0, value=1.0, step=0.1
)
# 1 AU (km)
AU_to_km = 149597870.7
distance_km = distance_au * AU_to_km

star_temperature_thousand_k = st.sidebar.slider(
    "항성의 온도 (1,000K)",
    min_value=1.0, max_value=30.0, value=5.7, step=0.1
)
star_temperature_k = star_temperature_thousand_k * 1000

# --- 2. 밝기 변화 계산 함수 (정사영 공식 활용) ---
def calculate_flux_change(star_radius_km, planet_radius_km, distance_from_center_of_star):
    """
    행성과 항성의 반경, 그리고 행성 중심과 항성 중심 사이의 투영 거리 (시선에 수직인 투영 거리)를
    입력받아 항성 밝기 감소 비율을 계산합니다.
    (두 원의 겹치는 면적 계산 공식 사용)

    Args:
        star_radius_km (float): 항성의 반경 (km)
        planet_radius_km (float): 행성의 반경 (km)
        distance_from_center_of_star (float): 행성 중심과 항성 중심 사이의 투영 거리 (km)

    Returns:
        float: 밝기 감소 비율 (0 ~ 1 사이 값, 0은 변화 없음, 1은 완전 가림)
    """
    R_s = star_radius_km
    R_p = planet_radius_km
    d = distance_from_center_of_star

    # 1. 행성이 항성 밖에 있을 때 (가림 없음)
    if d >= R_s + R_p:
        return 0.0
    # 2. 행성이 항성 안에 완전히 들어왔을 때 (더 작은 원이 더 큰 원 안에)
    elif d <= abs(R_s - R_p):
        if R_p <= R_s: # 행성이 항성보다 작거나 같을 때 (일반적인 경우)
            return (np.pi * R_p**2) / (np.pi * R_s**2)
        else: # 행성이 항성보다 클 때 (이 시뮬레이션에서는 드문 경우, 항성이 가려지는 것)
            return 1.0 # 전부 가림
    # 3. 부분적으로 가려졌을 때
    else:
        # 두 원의 교차하는 면적 계산 공식
        # arccos 인자 범위 제한 (-1.0 ~ 1.0)
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

# --- 시뮬레이션 계산 (트랜짓 시나리오 적용) ---
num_steps = 200

# 트랜짓 시뮬레이션을 위한 '투영 거리' (d) 생성
# 행성이 항성 앞을 가로지르는 시나리오를 가정합니다.
# d는 항성 중심에서 행성 중심까지의 시선 수직 거리입니다.
# d가 (Rs + Rp)보다 크면 가림 없음, 0일 때 최대 가림.
max_overlap_distance = star_radius_km + planet_radius_km

# 트랜짓이 발생하는 동안의 투영 거리를 -1.2 * max_overlap_distance 에서
# +1.2 * max_overlap_distance 까지 선형적으로 변화시킵니다.
# 이렇게 하면 항상 밝기 변화가 나타나는 구간이 포함됩니다.
transit_d_values = np.linspace(-max_overlap_distance * 1.2, max_overlap_distance * 1.2, num_steps)

flux_changes = []
for d_val in transit_d_values:
    # calculate_flux_change 함수는 투영 거리의 절댓값을 사용합니다.
    distance_from_center_of_star_for_calc = abs(d_val)

    flux_change_ratio = calculate_flux_change(star_radius_km, planet_radius_km, distance_from_center_of_star_for_calc)
    flux_changes.append(1 - flux_change_ratio) # 1에서 감소 비율을 뺀 값 = 상대 밝기 (상대 밝기 1.0은 변화 없음)

# 밝기 변화의 시간 축 (정규화된 시간)
time_steps = np.linspace(0, 1, num_steps)

# --- 3. Plotly 밝기 변화 그래프 출력 ---
st.header("항성 밝기 변화 그래프")

fig_flux = go.Figure(
    data=go.Scatter(x=time_steps, y=flux_changes, mode='lines', name='상대 밝기'),
    layout=go.Layout(
        title='항성 밝기 변화 곡선 (트랜짓 시뮬레이션)',
        xaxis_title='시간 (상대적)',
        yaxis_title='상대 밝기',
        yaxis_range=[0.0, 1.1] # 밝기 범위 0에서 1.1 사이
    )
)
st.plotly_chart(fig_flux, use_container_width=True)

---
st.header("행성 공전 애니메이션 (Plotly)")
st.markdown("""
이전 코드에서 행성의 공전 궤도를 시뮬레이션하는 `x_orbit`, `y_orbit`은 `distance_km`을 공전 궤도 반경으로 사용하여 계산되었습니다.
여기서는 **별도의 Plotly 애니메이션**을 통해 행성이 항성 주위를 공전하는 모습을 시각화합니다.
밝기 변화 시뮬레이션은 트랜짓에 중점을 두었으므로, 이 애니메이션은 '공전'의 개념을 보여주기 위함입니다.
""")
# ---

# 공전 궤도 데이터 (distance_km 사용)
num_animation_frames = 100
animation_theta = np.linspace(0, 2 * np.pi, num_animation_frames)
animation_x_orbit = distance_km * np.cos(animation_theta)
animation_y_orbit = distance_km * np.sin(animation_theta)

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
    x=animation_x_orbit, y=animation_y_orbit, mode='lines',
    line=dict(color='gray', dash='dot'),
    name='행성 궤도'
))

# 애니메이션 프레임 준비
frames = []
for i in range(num_animation_frames):
    frame = go.Frame(data=[
        go.Scatter(
            x=[0], y=[0], mode='markers',
            marker=dict(size=star_radius_km / R_sun * 20, color='orange', symbol='circle')
        ), # 항성 (고정)
        go.Scatter(
            x=[animation_x_orbit[i]], y=[animation_y_orbit[i]], mode='markers',
            marker=dict(size=planet_radius_km / R_earth * 10, color='blue', symbol='circle')
        ) # 행성의 현재 위치
    ], name=str(i))
    frames.append(frame)

fig_animation.frames = frames

# 애니메이션 레이아웃 설정 및 버튼 추가
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

---
st.header("항성 정보 표시")
st.write(f"**항성 반경:** {star_radius_km / 1000:.2f} km")
st.write(f"**행성 반경:** {planet_radius_km / 1000:.2f} km")
st.write(f"**항성 온도:** {star_temperature_k / 1000:.1f} K")

sigma = 5.67e-8 # 스테판-볼츠만 상수 (W/m^2/K^4)
# 면적 계산 시 km -> m 단위 변환 (x 1000)**2
star_surface_area = 4 * np.pi * (star_radius_km * 1000)**2 # m^2
star_luminosity = star_surface_area * sigma * (star_temperature_k)**4 # W

st.write(f"**항성 광도 (예상):** {star_luminosity:.2e} W")
st.write("*(참고: 항성 광도는 밝기 변화 계산에 직접 사용되지는 않지만, 항성의 물리량을 이해하는 데 도움을 줍니다.)*")
