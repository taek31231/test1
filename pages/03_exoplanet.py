import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 설정 ---
st.title("외계 행성 탐사: 식현상 시뮬레이터")

# --- 사용자 입력 ---
planet_radius = st.slider("행성 반지름 (단위: 임의)", 0.1, 2.0, 0.5, step=0.1)
star_radius = st.slider("항성 반지름 (단위: 임의)", 0.5, 3.0, 1.0, step=0.1)
distance = st.slider("행성-항성 사이 거리 (단위: 임의)", 1.0, 10.0, 5.0, step=0.5)

# --- 시뮬레이션 변수 설정 ---
orbital_period = 10  # 임의의 공전 주기 (frame 수)
num_frames = 200
theta = np.linspace(0, 2*np.pi, num_frames)
x = distance * np.cos(theta)
y = distance * np.sin(theta)

# --- 밝기 변화 계산 ---
# 행성이 항성 디스크를 가릴 때만 밝기 감소
brightness = []
for xi, yi in zip(x, y):
    distance_to_center = np.sqrt(xi**2 + yi**2)
    if distance_to_center < star_radius:
        delta_L = (planet_radius**2) / (star_radius**2)
        brightness.append(1 - delta_L)
    else:
        brightness.append(1)

# --- Plotly 밝기 변화 그래프 ---
fig = go.Figure()
fig.add_trace(go.Scatter(y=brightness, mode='lines', name="밝기"))
fig.update_layout(title="밝기 변화 곡선", xaxis_title="시간", yaxis_title="상대 밝기", yaxis_range=[min(brightness) - 0.05, 1.05])
st.plotly_chart(fig)

# --- 행성 공전 애니메이션 ---
st.subheader("행성 공전 애니메이션")

import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig2, ax = plt.subplots()
star = plt.Circle((0, 0), star_radius, color='yellow', alpha=0.6)
planet = plt.Circle((x[0], y[0]), planet_radius, color='blue')
ax.add_patch(star)
ax.add_patch(planet)
ax.set_xlim(-distance-1, distance+1)
ax.set_ylim(-distance-1, distance+1)
ax.set_aspect('equal')
ax.axis('off')

def update(i):
    planet.center = (x[i], y[i])
    return planet,

ani = animation.FuncAnimation(fig2, update, frames=num_frames, interval=50, blit=True)

from streamlit.components.v1 import html
import tempfile

with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
    from matplotlib.animation import PillowWriter
    ani.save(f.name, writer='pillow', fps=20)
    with open(f.name, "rb") as gif_file:
        st.image(gif_file.read(), caption="행성의 공전 (GIF)", use_column_width=True)
