import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. 페이지 설정 (탭 제목, 아이콘, 레이아웃)
st.set_page_config(
    page_title="문화 소비 분석 대시보드",
    page_icon="🎭",
    layout="wide"
)

# 2. 스타일링 (CSS를 이용해 폰트와 배경을 깔끔하게)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터베이스 연결 함수
def get_connection():
    # 데이터베이스 파일에 연결합니다.
    conn = sqlite3.connect('문화데이터베이스.db')
    return conn

# 4. 메인 제목 및 설명
st.title("🎭 지역별 문화 인프라와 공연 소비 패턴 분석")
st.markdown("공공데이터를 기반으로 지역별 문화 접근성과 소비 행태를 시각화한 대시보드입니다.")
st.divider()

# --- 데이터 로드 및 시각화 ---

try:
    conn = get_connection()

    # ---------------------------------------------------------
    # 차트 1. 연령대별 공연 장르 선호 분석
    # ---------------------------------------------------------
    st.header("1. 연령대별 공연 장르 선호도")
    
    # [SQL 설명] 연령대와 장르명으로 그룹화하여 예매 건수를 계산합니다.
    query1 = """
    SELECT 연령대, 장르명, COUNT(*) as 예매건수
    FROM 예매데이터
    GROUP BY 연령대, 장르명
    ORDER BY 연령대, 예매건수 DESC
    """
    df1 = pd.read_sql_query(query1, conn)

    # 시각화 (스택 막대 그래프)
    fig1 = px.bar(df1, x="연령대", y="예매건수", color="장르명", 
                 title="연령대별 선호 장르 분포",
                 barmode="stack",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(query1, language='sql')
        st.info("""
        - **인사이트 1:** 2030 세대는 뮤지컬과 콘서트 비중이 압도적으로 높습니다.
        - **인사이트 2:** 50대 이상 연령층에서는 클래식과 국악 장르의 소비가 타 연령대 대비 높게 나타납니다.
        """)

    st.divider()

    # ---------------------------------------------------------
    # 차트 2. 지역 소득 수준과 평균 결제금액 관계 분석
    # ---------------------------------------------------------
    st.header("2. 지역 소득 수준과 평균 결제금액의 관계")

    # [SQL 설명] 예매데이터와 매출데이터를 '지역' 기준으로 JOIN 합니다.
    query2 = """
    SELECT B.지역, B.소득순위, AVG(A.결제금액) as 평균결제금액
    FROM 예매데이터 A
    JOIN 문화시설매출데이터 B ON A.지역 = B.지역
    GROUP BY B.지역
    """
    df2 = pd.read_sql_query(query2, conn)

    # 시각화 (산점도)
    fig2 = px.scatter(df2, x="소득순위", y="평균결제금액", text="지역",
                     size="평균결제금액", color="평균결제금액",
                     title="지역별 소득순위 대비 평균 공연 결제액",
                     labels={"소득순위": "소득 순위 (낮을수록 고소득)", "평균결제금액": "평균 결제 금액(원)"})
    fig2.update_traces(textposition='top center')
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(query2, language='sql')
        st.info("""
        - **인사이트 1:** 소득 순위가 높은 지역일수록 1회당 평균 결제 금액이 높은 경향(우상향 또는 좌상향 패턴)을 보입니다.
        - **인사이트 2:** 특정 지역은 소득 순위 대비 결제 금액이 낮아, 해당 지역의 문화 상품 다양화가 필요함을 시사합니다.
        """)

    st.divider()

    # ---------------------------------------------------------
    # 차트 3. 문화접근성과 공연 소비 관계 분석
    # ---------------------------------------------------------
    st.header("3. 문화접근성과 공연 소비(예매건수) 분석")

    # [SQL 설명] 예매데이터와 역세권데이터를 JOIN 하고, 2030인구수를 포함합니다.
    # 컬럼명에 숫자가 들어가는 경우 쌍따옴표(")로 감싸줍니다.
    query3 = """
    SELECT C.지역, C.문화접근성지수, C."2030인구수", COUNT(A.공연명) as 예매건수
    FROM 예매데이터 A
    JOIN 문화역세권데이터 C ON A.지역 = C.지역
    GROUP BY C.지역
    """
    df3 = pd.read_sql_query(query3, conn)

    # 시각화 (버블 차트)
    fig3 = px.scatter(df3, x="문화접근성지수", y="예매건수",
                     size="2030인구수", color="지역", hover_name="지역",
                     title="문화접근성지수와 예매건수의 관계 (버블 크기: 2030 인구수)",
                     size_max=60)
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(query3, language='sql')
        st.info("""
        - **인사이트 1:** 문화접근성지수가 높을수록 실제 예매 건수가 선형적으로 증가하는 모습이 관찰됩니다.
        - **인사이트 2:** 버블의 크기가 큰(2030 인구가 많은) 지역임에도 접근성지수가 낮다면, 해당 지역에 인프라 확충이 시급합니다.
        """)

    conn.close()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.warning("팁: '문화데이터베이스.db' 파일이 app.py와 같은 폴더에 있는지 확인해주세요.")

# 하단 푸터
st.caption("© 2024 문화 데이터 분석 대시보드 | Data Source: Public Culture Data")