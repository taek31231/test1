import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf # yfinance 라이브러리 임포트
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("글로벌 상위 시가총액 Top 10 기업의 3개년 시가총액 변화 (yfinance 데이터 기반)")
st.write("*(주의: 시가총액은 과거 주가와 현재 발행 주식수를 기준으로 추정되므로 실제와 다를 수 있습니다.)*")

# --- 1. Top 10 기업 티커 및 정보 설정 ---
# 현재(2025년 6월) 대략적인 글로벌 시총 상위 기업 티커 목록
# 이 목록은 실제와 다를 수 있으며, 주기적으로 업데이트해야 합니다.
top_tickers = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "GOOGL": "Alphabet", # Google
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "TSM": "TSMC",
    "LLY": "Eli Lilly",
    "JPM": "JPMorgan Chase & Co.", # 금융 기업 추가
    "XOM": "Exxon Mobil" # 에너지 기업 추가
}
# 참고: Saudi Aramco (2222.SR)는 yfinance에서 접근이 어려울 수 있습니다.
# Tesla는 시총 변동성이 커서 Top10에 들지 않을 수 있어 다른 기업으로 대체

# 3개년 기간 설정 (오늘부터 3년 전까지)
end_date = datetime.now()
start_date = end_date - timedelta(days=3 * 365) # 대략 3년

# 시가총액 데이터를 저장할 DataFrame 초기화
market_cap_data = pd.DataFrame()
failed_tickers = []

st.sidebar.header("데이터 로딩 중...")
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

# --- 2. yfinance를 사용하여 데이터 가져오기 및 시가총액 추정 ---
total_tickers = len(top_tickers)
for i, (ticker, company_name) in enumerate(top_tickers.items()):
    status_text.text(f"Fetching data for {company_name} ({ticker})... ({i+1}/{total_tickers})")
    progress_bar.progress((i + 1) / total_tickers)

    try:
        ticker_obj = yf.Ticker(ticker)

        # 1. 최근 발행 주식수(Shares Outstanding) 가져오기 (가장 큰 한계점)
        # yfinance의 info에서 sharesOutstanding를 가져오지만, 이는 최신 값이며 과거 시점에는 적용되지 않음
        # 정확한 시가총액을 위해서는 각 날짜의 발행 주식수가 필요함
        # 여기서는 편의상 가장 최근의 sharesOutstanding를 과거 모든 주가에 곱하겠습니다.
        shares_outstanding = ticker_obj.info.get('sharesOutstanding', None)
        if shares_outstanding is None:
            # 기본적으로 info에서 가져오지 못하면 시총 정보에서 시도
            shares_outstanding = ticker_obj.info.get('sharesOutstanding', None)
            if shares_outstanding is None:
                st.warning(f"Could not retrieve sharesOutstanding for {company_name} ({ticker}). Skipping.")
                failed_tickers.append(ticker)
                continue

        # 2. 3년간의 과거 주가(종가) 데이터 가져오기
        hist = ticker_obj.history(start=start_date, end=end_date)
        if hist.empty:
            st.warning(f"No historical data found for {company_name} ({ticker}). Skipping.")
            failed_tickers.append(ticker)
            continue

        # 시가총액 추정 (종가 * 현재 발행 주식수)
        # 이 시가총액은 '현재' 발행 주식수를 과거에 적용한 것이므로 정확하지 않음
        estimated_market_cap = hist['Close'] * shares_outstanding

        # 단위를 조 달러(Trillion USD)로 변환 (1조 = 1,000,000,000,000)
        market_cap_data[company_name] = estimated_market_cap / 1_000_000_000_000

    except Exception as e:
        st.error(f"Error fetching data for {company_name} ({ticker}): {e}")
        failed_tickers.append(ticker)
        continue

st.sidebar.success("데이터 로딩 완료!")
if failed_tickers:
    st.sidebar.warning(f"Failed to fetch data for: {', '.join(failed_tickers)}")


if market_cap_data.empty:
    st.error("모든 기업의 데이터를 가져오는 데 실패했습니다. 티커를 확인하거나 다시 시도해 주세요.")
else:
    # --- 3. Plotly 그래프 생성 ---
    fig = go.Figure()

    for company in market_cap_data.columns:
        fig.add_trace(go.Scatter(
            x=market_cap_data.index,
            y=market_cap_data[company],
            mode='lines',
            name=company,
            hovertemplate=
                '<b>%{data.name}</b><br>' +
                '날짜: %{x|%Y-%m-%d}<br>' +
                '시가총액: %{y:,.2f}조 달러<extra></extra>'
        ))

    # 레이아웃 설정
    fig.update_layout(
        title={
            'text': '글로벌 상위 시가총액 Top 10 기업의 3개년 변화 (yfinance 데이터 기반)',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='날짜',
        yaxis_title='시가총액 (조 달러)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("참고 사항:")
    st.markdown("""
    * **데이터 출처:** 이 그래프는 `yfinance` 라이브러리를 사용하여 Yahoo Finance의 주가 데이터를 기반으로 시가총액을 **추정**한 것입니다.
    * **시가총액 추정의 한계:** `yfinance`는 과거 시점별 정확한 발행 주식수 데이터를 직접 제공하지 않습니다. 여기서는 **가장 최근 시점의 발행 주식수 데이터를 모든 과거 주가에 곱하여 시가총액을 계산**했으므로, 실제 과거의 정확한 시가총액과는 차이가 있을 수 있습니다. 발행 주식수는 기업의 자사주 매입, 주식 발행 등으로 변동됩니다.
    * **티커 및 순위 변동성:** Top 10 기업의 목록과 순위는 시장 상황에 따라 실시간으로 변동됩니다. 제공된 티커 목록은 작성 시점의 대략적인 상위 기업을 기준으로 합니다.
    """)
