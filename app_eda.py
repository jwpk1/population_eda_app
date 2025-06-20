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
    def __init__(self, *_):
        st.title("🏠 Home")
        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state['user_email']}님, 환영합니다.")
        st.markdown("""
---
**데이터셋 안내**  
1) **train.csv**: Bike Sharing Demand (시간별 자전거 대여량)  
2) **population_trends.csv**: 전국·지역별 연도별 인구 추이  

**사용 방법**:  
- EDA 탭에서 CSV 파일을 업로드하세요.  
- train.csv는 기존 Bike Sharing 분석,  
  population_trends.csv는 인구 분석 전용 탭에서 확인 가능합니다.
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
# EDA 페이지
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 EDA")

        # 1) Bike Sharing EDA (train.csv)
        uploaded = st.file_uploader("Upload train.csv", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded, parse_dates=['datetime'])
            tabs = st.tabs([
                "1. 목적 & 절차", "2. 데이터셋 설명", "3. 데이터 로드 & 품질 체크",
                "4. Datetime 특성 추출", "5. 시각화", "6. 상관관계 분석",
                "7. 회귀 예측", "8. 모델 평가"
            ])
            with tabs[0]:
                st.subheader("목적 및 절차")
                st.write("""
- 목적: 시간별 자전거 대여 수요 예측  
- 절차:  
  1) 데이터 탐색(EDA)  
  2) 특성 추출  
  3) 모델 학습  
  4) 성능 평가
                """)
            with tabs[1]:
                st.subheader("데이터셋 설명")
                st.markdown(df.head().to_markdown())
            with tabs[2]:
                st.subheader("데이터 로드 및 품질 체크")
                buf = io.StringIO()
                df.info(buf=buf)
                st.text(buf.getvalue())
                st.write(df.isnull().sum())
            with tabs[3]:
                st.subheader("Datetime 특성 추출")
                df['hour']      = df['datetime'].dt.hour
                df['dayofweek'] = df['datetime'].dt.dayofweek
                df['month']     = df['datetime'].dt.month
                st.write(df[['hour','dayofweek','month']].head())
            with tabs[4]:
                st.subheader("시각화")
                fig, ax = plt.subplots()
                sns.countplot(x='hour', data=df, ax=ax)
                st.pyplot(fig)
            with tabs[5]:
                st.subheader("상관관계 분석")
                st.write(df.corr())
            with tabs[6]:
                st.subheader("회귀 예측")
                X = df[['hour','dayofweek','month']]
                y = df['count']
                model = LinearRegression().fit(X, y)
                st.write("R²:", model.score(X, y))
            with tabs[7]:
                st.subheader("모델 평가")
                preds = model.predict(X)
                fig2, ax2 = plt.subplots()
                ax2.scatter(y, preds, alpha=0.3)
                st.pyplot(fig2)
        else:
            st.info("먼저 train.csv를 업로드하세요.")

        # 2) Population Trends EDA (population_trends.csv)
        pop_up = st.file_uploader("Upload population_trends.csv", type="csv", key="pop")
        if not pop_up:
            return

        pop_df = pd.read_csv(pop_up)

        # 전처리: '세종' 결측치 '-' → 0, 숫자 변환
        mask = pop_df['지역']=="세종"
        pop_df.loc[mask, ['인구','출생아수(명)','사망자수(명)']] = \
            pop_df.loc[mask, ['인구','출생아수(명)','사망자수(명)']].replace('-', 0)
        pop_df[['인구','출생아수(명)','사망자수(명)']] = \
            pop_df[['인구','출생아수(명)','사망자수(명)']].astype(int)

        # 지역명 한글→영문 매핑 (전국 제외)
        mapping = {
            "서울":"Seoul","부산":"Busan","대구":"Daegu","인천":"Incheon",
            "광주":"Gwangju","대전":"Daejeon","울산":"Ulsan","세종":"Sejong",
            "경기":"Gyeonggi","강원":"Gangwon","충북":"Chungbuk","충남":"Chungnam",
            "전북":"Jeonbuk","전남":"Jeonnam","경북":"Gyeongbuk","경남":"Gyeongnam",
            "제주":"Jeju"
        }

        pop_tabs = st.tabs([
            "기초 통계", "연도별 추이", "지역별 분석", "변화량 분석", "시각화"
        ])

        # 1) 기초 통계
        with pop_tabs[0]:
            st.subheader("Basic Data Overview")
            buf = io.StringIO()
            pop_df.info(buf=buf)
            st.text(buf.getvalue())
            st.dataframe(pop_df.describe())

        # 2) 연도별 추이 & 2035 예측
        with pop_tabs[1]:
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
            years = 2035 - recent['연도'].iloc[-1]
            pred = recent['인구'].iloc[-1] + avg_net * years
            ax.scatter([2035], [pred], color='red')
            ax.text(2035, pred, f"{int(pred):,}")
            st.pyplot(fig)

        # 3) 지역별 분석 (5년 절대/비율 변화)
        with pop_tabs[2]:
            st.subheader("5-Year Population Change by Region")
            latest = pop_df['연도'].max()
            prev5 = latest - 5
            df_recent = pop_df[
                pop_df['연도'].isin([prev5, latest]) & (pop_df['지역']!="전국")
            ]
            pivot = df_recent.pivot(index='지역', columns='연도', values='인구')
            pivot['change'] = pivot[latest] - pivot[prev5]
            pivot['rate']   = pivot['change'] / pivot[prev5] * 100
            pivot.index     = pivot.index.map(mapping)
            pivot = pivot.sort_values('change', ascending=False)

            # 절대 변화량 그래프
            fig3, ax3 = plt.subplots()
            sns.barplot(x=pivot['change']/1000, y=pivot.index, ax=ax3)
            ax3.set_title("5-Year Population Change by Region")
            ax3.set_xlabel("Change (×1,000)")
            ax3.set_ylabel("")
            for i, v in enumerate(pivot['change']/1000):
                ax3.text(v + 0.1, i, f"{v:.1f}")
            st.pyplot(fig3)

            # 비율 변화 그래프
            fig4, ax4 = plt.subplots()
            sns.barplot(x=pivot['rate'], y=pivot.index, ax=ax4)
            ax4.set_title("5-Year Population Change Rate by Region")
            ax4.set_xlabel("Percent Change (%)")
            ax4.set_ylabel("")
            for i, v in enumerate(pivot['rate']):
                ax4.text(v + 0.1, i, f"{v:.1f}%")
            st.pyplot(fig4)

            st.markdown("""
**Explanation**:  
- The first chart shows the 5-year absolute population change (in thousands) for each region.  
- The second chart shows the percentage change relative to the population 5 years ago.
            """)

        # 4) 변화량 분석 (Top 100 Change Cases)
        with pop_tabs[3]:
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

        # 5) 시각화 (지역-연도 누적 영역 그래프)
        with pop_tabs[4]:
            st.subheader("Region-Year Stacked Area Chart")
            pivot2 = pop_df.pivot(index='연도', columns='지역', values='인구')
            pivot2 = pivot2.drop('전국', axis=1).rename(columns=mapping)
            fig5, ax5 = plt.subplots()
            pivot2.plot.area(ax=ax5)
            ax5.set_title("Population by Region (Area Chart)")
            ax5.set_xlabel("Year")
            ax5.set_ylabel("Population")
            st.pyplot(fig5)

# ---------------------
# 앱 실행
# ---------------------
def main():
    st.set_page_config(page_title="EDA App", layout="wide")
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
