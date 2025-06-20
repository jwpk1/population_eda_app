import streamlit as st
import pyrebase
import time
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.firebasestorage.app",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase   = pyrebase.initialize_app(firebase_config)
auth       = firebase.auth()
firestore  = firebase.database()
storage    = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in         = False
    st.session_state.user_email        = ""
    st.session_state.id_token          = ""
    st.session_state.user_name         = ""
    st.session_state.user_gender       = "선택 안함"
    st.session_state.user_phone        = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 홈 페이지 클래스
# ---------------------
class Home:
    def __init__(self, login_page, register_page, findpw_page):
        st.title("🏠 Home")
        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state.get('user_email')}님 환영합니다.")

        st.markdown("""
        ---
        **Population Trends Dataset**  
        - **File:** `population_trends.csv`  
        - **Columns:**  
          - `연도` (Year)  
          - `지역` (Region, KR)  
          - `인구` (Population)  
          - `출생아수(명)` (Births)  
          - `사망자수(명)` (Deaths)  

        **Region name mapping (KR → EN):**  
        | 한국어 | English      |
        |-------|--------------|
        | 서울   | Seoul        |
        | 부산   | Busan        |
        | 대구   | Daegu        |
        | 인천   | Incheon      |
        | 광주   | Gwangju      |
        | 대전   | Daejeon      |
        | 울산   | Ulsan        |
        | 세종   | Sejong       |
        | 경기   | Gyeonggi-do  |
        | 강원   | Gangwon-do   |
        | 충북   | Chungbuk-do  |
        | 충남   | Chungnam-do  |
        | 전북   | Jeonbuk-do   |
        | 전남   | Jeonnam-do   |
        | 경북   | Gyeongbuk-do |
        | 경남   | Gyeongnam-do |
        | 제주   | Jeju-do      |

        좌측 네비게이션에서 **EDA** 페이지로 이동하여 분석을 시작하세요.
        """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token   = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.user_name         = user_info.get("name", "")
                    st.session_state.user_gender       = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone        = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url", "")

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email    = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name     = st.text_input("성명")
        gender   = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone    = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name":  name,
                    "gender": gender,
                    "phone":  phone,
                    "role":   "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email      = st.session_state.get("user_email", "")
        new_email  = st.text_input("이메일", value=email)
        name       = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender     = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", "선택 안함"))
        )
        phone      = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", ""))

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email  = new_email
            st.session_state.user_name   = name
            st.session_state.user_gender = gender
            st.session_state.user_phone  = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name":  name,
                "gender": gender,
                "phone":  phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        for key in [
            "logged_in","user_email","id_token",
            "user_name","user_gender","user_phone","profile_image_url"
        ]:
            st.session_state[key] = False if key == "logged_in" else ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 Population Trends EDA")
        uploaded = st.file_uploader("Upload population_trends.csv", type="csv")
        if not uploaded:
            st.info("Please upload the population_trends.csv file.")
            return

        # --- 기본 전처리 ---
        df = pd.read_csv(uploaded)
        mask = df['지역'] == '세종'
        df.loc[mask] = df.loc[mask].replace('-', '0')
        for col in ['인구', '출생아수(명)', '사망자수(명)']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # 한글→영문 매핑
        region_map = {
            '서울':'Seoul','부산':'Busan','대구':'Daegu','인천':'Incheon',
            '광주':'Gwangju','대전':'Daejeon','울산':'Ulsan','세종':'Sejong',
            '경기':'Gyeonggi-do','강원':'Gangwon-do','충북':'Chungbuk-do',
            '충남':'Chungnam-do','전북':'Jeonbuk-do','전남':'Jeonnam-do',
            '경북':'Gyeongbuk-do','경남':'Gyeongnam-do','제주':'Jeju-do'
        }

        # 탭 구성
        tabs = st.tabs([
            "기초 통계", "연도별 추이", "지역별 분석",
            "변화량 분석", "시각화"
        ])

        # 1. 기초 통계
        with tabs[0]:
            st.header("Basic Summary Statistics")
            buf = io.StringIO()
            df.info(buf=buf)
            st.subheader("DataFrame Info")
            st.text(buf.getvalue())
            st.subheader("Descriptive Statistics")
            st.dataframe(df.describe())

        # 2. 연도별 전체 인구 추이 & 예측
        with tabs[1]:
            st.header("Yearly Population Trend & Projection")
            df_nat   = df[df['지역']=='전국'].sort_values('연도')
            years    = df_nat['연도']
            pops     = df_nat['인구']
            last_year = years.max()
            recent    = df_nat[df_nat['연도'] > last_year-3]
            avg_net   = (recent['출생아수(명)'] - recent['사망자수(명)']).mean()
            last_pop  = pops.iloc[-1]

            future_years = list(range(last_year+1, 2036))
            proj = [int(last_pop + avg_net*(y-last_year)) for y in future_years]

            fig, ax = plt.subplots()
            ax.plot(years, pops, marker='o', label='Historical')
            ax.plot(future_years, proj, marker='o', linestyle='--', label='Projected')
            ax.set_title("Population Trend")
            ax.set_xlabel("Year")
            ax.set_ylabel("Population")
            ax.legend()
            st.pyplot(fig)

        # 3. 지역별 인구 변화량 순위 (최근 5년)
        with tabs[2]:
            st.header("Regional Population Change Rankings (Last 5 Years)")
            last = df['연도'].max()
            prev = last - 5

            df_sel = df[df['연도'].isin([prev, last])]
            pivot = df_sel.pivot(index='지역', columns='연도', values='인구').drop(index='전국')
            pivot['change']      = pivot[last] - pivot[prev]
            pivot['pct_change']  = pivot['change'] / pivot[prev] * 100

            rank_df = pivot.reset_index().sort_values('change', ascending=False)
            rank_df['region_en'] = rank_df['지역'].map(region_map)

            # 절대 변화 (천 단위)
            fig, ax = plt.subplots()
            sns.barplot(x=rank_df['change']/1000, y=rank_df['region_en'], ax=ax)
            for i, v in enumerate(rank_df['change']/1000):
                ax.text(v, i, f"{v:.1f}", va='center')
            ax.set_title("Population Change by Region (Last 5 Years)")
            ax.set_xlabel("Change (Thousands)")
            st.pyplot(fig)
            st.markdown(
                "The bar chart above shows the net change over the last five years for each region."
            )

            # 변화율 (%)
            fig2, ax2 = plt.subplots()
            sns.barplot(x=rank_df['pct_change'], y=rank_df['region_en'], ax=ax2)
            for i, v in enumerate(rank_df['pct_change']):
                ax2.text(v, i, f"{v:.1f}%", va='center')
            ax2.set_title("Population Change Rate by Region (Last 5 Years)")
            ax2.set_xlabel("Change Rate (%)")
            st.pyplot(fig2)
            st.markdown(
                "This chart shows the percentage change relative to five years ago for each region."
            )

        # 4. 연도별 증감 상위 100 사례
        with tabs[3]:
            st.header("Top 100 Year-over-Year Population Differences")
            df_diff = df.sort_values(['지역','연도'])
            df_diff['diff'] = df_diff.groupby('지역')['인구'].diff()
            df_diff = df_diff[df_diff['지역']!='전국']
            top100 = df_diff.nlargest(100,'diff')[['지역','연도','diff']].copy()
            top100['diff']        = top100['diff'].astype(int)
            top100['region_en']   = top100['지역'].map(region_map)

            display_df = top100[['region_en','연도','diff']].rename(
                columns={'region_en':'Region','연도':'Year','diff':'Difference'}
            )
            styled = (
                display_df.style
                .format({'Difference':'{:,}'})
                .background_gradient(cmap='bwr_r', subset=['Difference'], axis=0)
            )
            st.write(styled)

        # 5. 지역·연도별 누적 영역 그래프
        with tabs[4]:
            st.header("Population by Region & Year (Stacked Area)")
            area_pivot = df.pivot(index='연도', columns='지역', values='인구').drop(columns='전국')
            area_pivot = area_pivot.rename(columns=region_map)

            fig, ax = plt.subplots()
            area_pivot.plot.area(ax=ax)
            ax.set_title("Population by Region and Year")
            ax.set_xlabel("Year")
            ax.set_ylabel("Population")
            st.pyplot(fig)

# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login    = st.Page(Login,    title="Login",    icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW   = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home     = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User     = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout   = st.Page(Logout,   title="Logout",  icon="🔓", url_path="logout")
Page_EDA      = st.Page(EDA,      title="EDA",     icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()
