import streamlit as st
import pyrebase
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.appspot.com",
    "messagingSenderId": "...",
    "appId": "..."
}
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# ---------------------
# Home 페이지
# ---------------------
class Home:
    def __init__(self):
        st.title("🏠 Home")
        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state['user_email']}님, 환영합니다.")
        st.markdown("""
---
**데이터셋 안내**  
- **population_trends.csv**: 전국·지역별 연도별 인구 추이  

**사용 방법**  
1. 사이드바에서 **EDA** 탭으로 이동  
2. population_trends.csv 파일을 업로드  
3. 탭별 분석 결과 확인
        """)

# ---------------------
# 인증 관련 페이지
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 Login")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                auth.sign_in_with_email_and_password(email, password)
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.success("로그인 성공")
            except:
                st.error("로그인 실패: 이메일 또는 비밀번호를 확인하세요.")

class Register:
    def __init__(self):
        st.title("📝 Register")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("회원가입 성공! 로그인 해주세요.")
            except:
                st.error("회원가입 실패: 이미 등록된 이메일이거나 비밀번호 조건을 확인하세요.")

class FindPassword:
    def __init__(self):
        st.title("🔍 Find Password")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 링크 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
            except:
                st.error("이메일 전송 실패: 이메일을 확인하세요.")

# ---------------------
# EDA 페이지 (population_trends.csv 전용)
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 Population Trends EDA")

        pop_file = st.file_uploader("Upload population_trends.csv", type="csv")
        if not pop_file:
            st.info("먼저 population_trends.csv 파일을 업로드 해주세요.")
            return

        pop_df = pd.read_csv(pop_file)

        # — 전처리: '세종' 결측치 처리 및 숫자형 변환 —
        mask = pop_df['지역'] == "세종"
        pop_df.loc[mask, ['인구','출생아수(명)','사망자수(명)']] = \
            pop_df.loc[mask, ['인구','출생아수(명)','사망자수(명)']].replace('-', 0)
        pop_df[['인구','출생아수(명)','사망자수(명)']] = \
            pop_df[['인구','출생아수(명)','사망자수(명)']].astype(int)

        # — 지역명 한글→영문 매핑(전국 제외) —
        mapping = {
            "서울":"Seoul","부산":"Busan","대구":"Daegu","인천":"Incheon",
            "광주":"Gwangju","대전":"Daejeon","울산":"Ulsan","세종":"Sejong",
            "경기":"Gyeonggi","강원":"Gangwon","충북":"Chungbuk","충남":"Chungnam",
            "전북":"Jeonbuk","전남":"Jeonnam","경북":"Gyeongbuk","경남":"Gyeongnam",
            "제주":"Jeju"
        }

        # — 탭 UI 구성 —
        tabs = st.tabs([
            "기초 통계", "연도별 추이", "지역별 분석", "변화량 분석", "시각화"
        ])

        # 1) 기초 통계
        with tabs[0]:
            st.subheader("Basic Data Overview")
            buf = io.StringIO()
            pop_df.info(buf=buf)
            st.text(buf.getvalue())
            st.dataframe(pop_df.describe())

        # 2) 연도별 추이 & 2035 예측
        with tabs[1]:
            st.subheader("Nationwide Population Trend & 2035 Prediction")
            nation = pop_df[pop_df['지역']=="전국"].copy()
            fig, ax = plt.subplots()
            ax.plot(nation['연도'], nation['인구'], marker='o')
            ax.set_title("Population Trend (Nationwide)")
            ax.set_xlabel("Year")
            ax.set_ylabel("Population")
            recent = nation.tail(3)
            net = recent['출생아수(명)'] - recent['사망자수(명)']
            avg_net = net.mean()
            years_to_2035 = 2035 - recent['연도'].iloc[-1]
            pred = recent['인구'].iloc[-1] + avg_net * years_to_2035
            ax.scatter([2035], [pred], color='red')
            ax.text(2035, pred, f"{int(pred):,}")
            st.pyplot(fig)

        # 3) 지역별 분석 (5년 절대/비율 변화)
        with tabs[2]:
            st.subheader("5-Year Population Change by Region")
            latest = pop_df['연도'].max()
            prev5 = latest - 5
            df5 = pop_df[
                pop_df['연도'].isin([prev5, latest]) & (pop_df['지역']!="전국")
            ].pivot(index='지역', columns='연도', values='인구')
            df5['change'] = df5[latest] - df5[prev5]
            df5['rate']   = df5['change'] / df5[prev5] * 100
            df5.index     = df5.index.map(mapping)
            df5 = df5.sort_values('change', ascending=False)

            # 절대 변화량 그래프
            fig1, ax1 = plt.subplots()
            sns.barplot(x=df5['change']/1000, y=df5.index, ax=ax1)
            ax1.set_title("5-Year Change by Region")
            ax1.set_xlabel("Change (×1,000)")
            ax1.set_ylabel("")
            for i, v in enumerate(df5['change']/1000):
                ax1.text(v + 0.1, i, f"{v:.1f}")
            st.pyplot(fig1)

            # 비율 변화 그래프
            fig2, ax2 = plt.subplots()
            sns.barplot(x=df5['rate'], y=df5.index, ax=ax2)
            ax2.set_title("5-Year Change Rate by Region")
            ax2.set_xlabel("Percent Change (%)")
            ax2.set_ylabel("")
            for i, v in enumerate(df5['rate']):
                ax2.text(v + 0.1, i, f"{v:.1f}%")
            st.pyplot(fig2)

            st.markdown("""
**Explanation**:  
- 첫 번째 그래프는 최근 5년간 지역별 절대 인구 변화량(천 단위)입니다.  
- 두 번째 그래프는 5년 전 대비 인구 변화율(%)을 보여줍니다.
            """)

        # 4) 변화량 분석 (Top 100 Change Cases)
        with tabs[3]:
            st.subheader("Top 100 Population Change Cases")
            pop_df['diff'] = pop_df.groupby('지역')['인구'].diff()
            top100 = pop_df[pop_df['지역']!="전국"].nlargest(100, 'diff')
            styled = (
                top100[['연도','지역','인구','diff']]
                .rename(columns={'diff':'Change'})
                .style
                .format({'인구':'{:,.0f}','Change':'{:,.0f}'})
                .background_gradient(subset=['Change'], cmap='RdBu_r', axis=0)
            )
            st.dataframe(styled)

        # 5) 시각화 (Region-Year Stacked Area)
        with tabs[4]:
            st.subheader("Region-Year Stacked Area Chart")
            pivot = pop_df.pivot(index='연도', columns='지역', values='인구')
            pivot = pivot.drop('전국', axis=1).rename(columns=mapping)
            fig3, ax3 = plt.subplots()
            pivot.plot.area(ax=ax3)
            ax3.set_title("Population by Region (Area Chart)")
            ax3.set_xlabel("Year")
            ax3.set_ylabel("Population")
            st.pyplot(fig3)

# ---------------------
# 페이지 네비게이션
# ---------------------
def main():
    st.set_page_config(page_title="Population EDA App", layout="wide")
    menu = ["Home", "Login", "Register", "FindPw", "EDA"]
    choice = st.sidebar.selectbox("메뉴", menu)
    if choice == "Home":
        Home()
    elif choice == "Login":
        Login()
    elif choice == "Register":
        Register()
    elif choice == "FindPw":
        FindPassword()
    elif choice == "EDA":
        EDA()

if __name__ == "__main__":
    main()