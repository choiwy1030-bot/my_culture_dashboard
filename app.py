import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 데이터베이스 연결 설정
DB_FILE = '문화데이터베이스.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

# 데이터베이스 파일 존재 여부 확인
if not os.path.exists(DB_FILE):
    st.error(f"🚨 '{DB_FILE}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# 2. 사이드바 메뉴 구성
st.sidebar.title("🎨 문화 데이터 분석")
page = st.sidebar.selectbox("메뉴를 선택하세요", ["홈", "연령대별 장르 선호", "소득수준과 결제금액 관계", "문화접근성과 소비 관계"])

# --- 페이지 1: 홈 ---
if page == "홈":
    st.title("🏛️ 공공 문화데이터 분석 대시보드")
    st.markdown("""
    이 대시보드는 **공공 문화데이터**를 분석하여 지역별, 연령대별 문화 향유 현황을 시각화합니다.
    - **분석 데이터**: 예매내역, 지역별 소득 대비 시설 현황, 밀레니얼 문화역세권 정보
    """)
    
    conn = get_connection()
    tabs = ["예매데이터", "소득대비문화시설", "밀레니얼문화역세권"]
    cols = st.columns(3)
    
    for i, tab in enumerate(tabs):
        count = pd.read_sql(f"SELECT COUNT(*) FROM {tab}", conn).iloc[0, 0]
        cols[i].metric(label=f"{tab} 건수", value=f"{count:,}건")
    conn.close()

# --- 페이지 2: 연령대별 장르 선호 ---
elif page == "연령대별 장르 선호":
    st.header("📊 연령대별 공연 장르 선호 분석")
    
    sql = """
    SELECT 연령대, 장르, COUNT(*) as 예매건수 
    FROM 예매데이터 
    GROUP BY 연령대, 장르
    """
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    
    # 시각화
    fig = px.bar(df, x="연령대", y="예매건수", color="장르", 
                 title="연령대별 장르별 예매 현황", barmode="stack",
                 category_orders={"연령대": ["10대", "20대", "30대", "40대", "50대", "60대 이상"]})
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("**사용한 SQL**\n```sql\n" + sql + "\n```")
    st.markdown("💡 **인사이트**\n1. 특정 연령대에서 압도적으로 선호하는 장르(예: 20대 뮤지컬)를 파악하여 타겟 마케팅이 가능합니다.\n2. 전 연령층에 걸쳐 고르게 분포된 장르를 통해 대중적인 콘텐츠의 특성을 이해할 수 있습니다.")

# --- 페이지 3: 소득수준과 결제금액 관계 ---
elif page == "소득수준과 결제금액 관계":
    st.header("💰 지역 소득수준과 평균 결제금액 분석")
    
    sql = """
    SELECT B.시도명, B.소득순위, AVG(A.결제금액) as 평균결제금액, COUNT(A.공연명) as 예매건수
    FROM 예매데이터 A
    JOIN 소득대비문화시설 B ON A.거주지역 = B.시도명
    GROUP BY B.시도명
    """
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    
    # 시각화
    fig = px.scatter(df, x="소득순위", y="평균결제금액", size="예매건수", color="시도명",
                     hover_name="시도명", title="지역별 소득순위 대비 평균 결제금액 (버블크기: 예매건수)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("**사용한 SQL**\n```sql\n" + sql + "\n```")
    st.markdown("💡 **인사이트**\n1. 소득 순위가 높을수록 1회당 평균 결제 금액이 높은지 상관관계를 확인할 수 있습니다.\n2. 소득은 낮지만 예매 건수가 많은 지역은 '가성비' 중심의 문화 소비가 활발함을 의미합니다.")

# --- 페이지 4: 문화접근성과 소비 관계 ---
elif page == "문화접근성과 소비 관계":
    st.header("🚶 문화접근성과 공연 소비 관계 분석")
    
    # 체크박스 옵션
    exclude_seoul = st.checkbox("서울/경기 제외하고 보기")
    
    sql = """
    SELECT B.시도명, AVG(B.문화접근성지수) as 평균접근성지수, COUNT(A.공연명) as 예매건수, SUM(B.밀레니얼인구수) as 총밀레니얼인구
    FROM 예매데이터 A
    JOIN 밀레니얼문화역세권 B ON A.거주지역 = B.시도명
    GROUP BY B.시도명
    """
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    
    if exclude_seoul:
        df = df[~df['시도명'].isin(['서울', '서울특별시', '경기', '경기도'])]
    
    # 시각화
    fig = px.scatter(df, x="평균접근성지수", y="예매건수", size="총밀레니얼인구", color="시도명",
                     title="문화접근성지수와 예매건수의 관계 (버블크기: 밀레니얼 인구수)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("**사용한 SQL**\n```sql\n" + sql + "\n```")
    st.markdown("💡 **인사이트**\n1. 문화 시설에 대한 접근성이 좋을수록 실제 예매 건수가 증가하는지 시각적으로 보여줍니다.\n2. 수도권 제외 시, 지방 거점 도시의 접근성 대비 소비 효율을 비교 분석하기 용이합니다.")